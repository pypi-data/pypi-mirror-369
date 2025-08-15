import time, os, copy, datetime, math, random, warnings
import subprocess, sys
import numpy as np
import pandas as pd
from scipy import stats, signal

import matplotlib.pyplot as plt
from matplotlib import cm, colormaps
import matplotlib as mpl
from matplotlib.pyplot import figure
from matplotlib.patches import Rectangle
# sys.setrecursionlimit(100000)
from sklearn import cluster, mixture

from importlib_resources import files

SCANVPY = True
try:
    import scanpy as sc
    import anndata
except ImportError:
    print('WARNING: scanpy not installed.')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scanpy"])
        import scanpy as sc
        import anndata
        print('INFO: scanpy was sucessfully installed.')
    except:
        print('WARNING: Cannot install scanpy.')
        SCANVPY = False

STATANNOT = True
try:
    # from statannot import add_stat_annotation
    from statannotations.Annotator import Annotator
except ImportError:
    print('WARNING: statannot not installed or not available. ')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "statannotations"])
        from statannotations.Annotator import Annotator
        print('INFO: statannotations was sucessfully installed.')
    except:
        print('WARNING: Cannot install statannotations.')
        STATANNOT = False

SEABORN = True
try:
    import seaborn as sns
except ImportError:
    print('WARNING: seaborn not installed or not available. ')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "seaborn"])
        import seaborn as sns
        print('INFO: seaborn was sucessfully installed.')
    except:
        print('WARNING: Cannot install seaborn.')
        SEABORN = False

try:
    import plotly.graph_objects as go
except ImportError:
    print('WARNING: plotly not installed.')
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
        import plotly.graph_objects as go
        print('INFO: plotly was sucessfully installed.')
    except:
        print('WARNING: Cannot install plotly.')
    
from .supp import get_abbreviations


def get_sample_to_group_dict( samples, conditions ):
    
    samples = np.array(samples)
    conditions = np.array(conditions)
    
    slst = list(set(list(samples)))
    slst.sort()
    glst = []
    for s in slst:
        b = samples == s
        g = conditions[b][0]
        glst.append(g)
        
    dct = dict(zip(slst, glst))
    return dct


def get_sample_to_group_map( samples, conditions ):
    return get_sample_to_group_dict( samples, conditions )


# df_cnt, df_pct= get_population( adata_s.obs['sid'], 
#                                 adata_s.obs['minor'], sort_by = [] )
def get_population( args_in, cts_in, sort_by = [], sample_col = 'sample' ):

    if isinstance( args_in, pd.Series ) & isinstance( cts_in, pd.Series ):
        pids = args_in.copy(deep = True)
        cts = cts_in.copy(deep = True)
        sg_map = None
        
    elif isinstance( args_in, anndata.AnnData ) & isinstance( cts_in, str ):
        try:
            pids = args_in.obs[sample_col]
            cts = args_in.obs[cts_in]
            sg_map = get_sample_to_group_map( args_in.obs[sample_col], args_in.obs['condition'] )
        except:
            print('ERROR: %s not in obs columns. ' % cts_in)
            return None, None            
    else:
        print('ERROR: Invalid input. The 1st argument must be AnnData or pandas.Series. ')
        return None, None

    pid_lst = list(set(list(pids)))
    pid_lst.sort()
    celltype_lst = list(set(list(cts)))
    celltype_lst.sort()

    df_celltype_cnt = pd.DataFrame(index = pid_lst, columns = celltype_lst)
    df_celltype_cnt.loc[:,:] = 0

    for pid in pid_lst:
        b = np.array(pids) == pid
        ct_sel = np.array(cts)[b]

        for ct in celltype_lst:
            bx = ct_sel == ct
            df_celltype_cnt.loc[pid, ct] = np.sum(bx)

    df_celltype_pct = (df_celltype_cnt.div(df_celltype_cnt.sum(axis = 1), axis = 0)*100).astype(float)
    
    if len(sort_by) > 0:
        df_celltype_pct.sort_values(by = sort_by, inplace = True)

    if sg_map is None:
        slst, clst = get_sample_and_group_from_sample_ext( df_celltype_cnt.index.values )                
        sg_map = dict(zip( slst, clst ))

    df_celltype_cnt.insert(0, 'Group', list(df_celltype_cnt.index.values))
    df_celltype_cnt['Group'] = df_celltype_cnt['Group'].replace( sg_map )
    df_celltype_pct.insert(0, 'Group', list(df_celltype_pct.index.values))
    df_celltype_pct['Group'] = df_celltype_pct['Group'].replace( sg_map )
    
    return df_celltype_cnt, df_celltype_pct


def get_population_per_sample( args_in, cts_in, sort_by = [], sample_col = 'sample' ):
    return get_population( args_in, cts_in, sort_by, sample_col = sample_col )


def get_gene_expression_mean( adata, genes = [], group_col = 'sample', nz_pct = True ): 

    sample_col = group_col
    slst = adata.obs[sample_col].unique().tolist()
    slst.sort()

    sg_map = get_sample_to_group_map( adata.obs[sample_col], adata.obs['condition'] )
    
    if genes is None:
        Xs = adata.to_df()
        df = pd.DataFrame(index = slst, columns = adata.var.index)
    elif len(genes) == 0:
        Xs = adata.to_df()
        df = pd.DataFrame(index = slst, columns = adata.var.index)
    else:
        Xs = adata[:, genes].to_df()
        df = pd.DataFrame(index = slst, columns = genes)

    if nz_pct:
        for s in slst:
            b = adata.obs[sample_col] == s
            mns = (Xs.loc[b,:] > 0).mean(axis = 0)
            df.loc[s,:] = list(mns)
    
        df = df.astype(float)
    else:
        Xs['Group'] = adata.obs[sample_col]
        df = Xs.groupby('Group').mean(numeric_only=True)
        
    df.insert(0, 'Group', list(df.index.values))
    df['Group'] = df['Group'].replace( sg_map )
                  
    return df


def get_cci_means( cci_df_dct, cci_idx_lst = None, 
                   cells = [], genes = [], pval_cutoff = 0.05 ):

    if cci_idx_lst is None:
        ## get coomon cci index
        for j, key in enumerate(cci_df_dct.keys()):
            b = cci_df_dct[key]['pval'] <= pval_cutoff
            if len(cells) > 0:
                b = b & (cci_df_dct[key]['cell_A'].isin(cells) | cci_df_dct[key]['cell_B'].isin(cells))
            if len(genes) > 0:
                b = b & (cci_df_dct[key]['gene_A'].isin(genes) | cci_df_dct[key]['gene_B'].isin(genes))
                         
            if j == 0:
                idx_union = list(cci_df_dct[key].index.values[b])
            else:
                idx_union = list(set(idx_union).union(list(cci_df_dct[key].index.values[b])))
        cci_idx_lst = idx_union
    
    tlst = cci_idx_lst
    slst = list(cci_df_dct.keys())

    df = pd.DataFrame(index = slst, columns = tlst)
    df.loc[:,:] = None
    
    for s in slst:
        dfv = cci_df_dct[s]
        idx = list(dfv.index.values)
        clst = list(set(tlst).intersection(idx))
        df.loc[s, clst] = dfv.loc[clst, 'mean'].astype(float)   
                
    df = df.astype(float)
    
    slst2, clst = get_sample_and_group_from_sample_ext( df.index.values )                
    # sample_group_map = dict(zip( slst, clst ))    
    df.insert( 0, 'Group', clst )
    
    return df
    

def cci_get_diff_interactions( df_cci_sample, sample_group_map = None, 
                               ref_group = None, pval_cutoff = 0.05 ):
    
    df = df_cci_sample.copy(deep = True)
    if 'Group' in list(df.columns.values):
        sample_group_map = dict(zip( df.index.values, df['Group'] ))
        df = df.drop( columns = ['Group'] )

    group = []
    for k in list(df.index.values):
        group.append( sample_group_map[k] )
        
    glst = list(set(group))
    glst.sort()
    group = pd.Series(group, index = df.index)
    
    df_res = pd.DataFrame(index = list(df.columns.values))
    
    if ref_group is None:
        for i, g1 in enumerate(glst):
            
            b_r = (group == g1) # & (~df[item].isnull())
            n_r = np.sum(b_r)
            if n_r > 0:
                for j, g2 in enumerate(glst):
                    if i > j:
                        b_o = (group == g2) 
                        n_o = np.sum(b_o)
                        if n_o > 0:
                            bx = ((~df.loc[b_r,:].isna()).sum() > 1) & ((~df.loc[b_o,:].isna()).sum() > 1)
                            bx = bx & (df.loc[b_r,:].std() >= 1e-8) & (df.loc[b_o,:].std() >= 1e-8)
                            res = stats.ttest_ind(df.loc[b_r,bx], 
                                                  df.loc[b_o,bx], axis=0, 
                                                  equal_var=False,  
                                                  nan_policy='omit', 
                                                  permutations=None, 
                                                  random_state=None, 
                                                  alternative='two-sided', 
                                                  trim=0)
                            df_res.loc[bx, '%s_vs_%s' % (g1, g2)] = res.pvalue
            
    elif ref_group in glst:
    
        b_ref = group == ref_group
        for g in glst:
            if g != ref_group:
                b_r = (group == g)  
                n_r = np.sum(b_r)
    
                b_o = b_ref 
                n_o = np.sum(b_o)
                bx = ((~df.loc[b_r,:].isna()).sum() > 1) & ((~df.loc[b_o,:].isna()).sum() > 1)
                bx = bx & (df.loc[b_r,:].std() >= 1e-8) & (df.loc[b_o,:].std() >= 1e-8)
                res = stats.ttest_ind(df.loc[b_r,bx], 
                                      df.loc[b_o,bx], axis=0, 
                                      equal_var=False, 
                                      nan_policy='omit',  
                                      permutations=None, 
                                      random_state=None, 
                                      alternative='two-sided', 
                                      trim=0)
                df_res.loc[bx, '%s_vs_%s' % (g, ref_group)] = res.pvalue
    
    b = df_res.isnull()
    df_res[b] = 1
    
    pv_min = df_res.min(axis = 1)
    df_res = df_res.loc[pv_min <= pval_cutoff,:]

    df_res['ss'] = (df_res <= pval_cutoff).sum(axis = 1)
    df_res['pp'] = -np.log10(df_res.prod(axis = 1) + 1e-30)
    df_res.sort_values(by = ['ss', 'pp'], ascending = False, inplace = True)
       
    return df_res.iloc[:,:-2]


def test_group_diff( df_sample_by_items, sample_group_map = None, 
                     ref_group = None, pval_cutoff = 0.05 ):
    
    return cci_get_diff_interactions( df_sample_by_items, sample_group_map, 
                               ref_group, pval_cutoff )


### Remove common CCI
def cci_remove_common( df_dct ):
    
    idx_dct = {}
    idxo_dct = {}
    celltype_lst = []

    for j, g in enumerate(df_dct.keys()):
        idx_dct[g] = list(df_dct[g].index.values)
        if j == 0:
            idx_c = idx_dct[g]
        else:
            idx_c = list(set(idx_c).intersection(idx_dct[g]))

        ctA = list(df_dct[g]['cell_A'].unique())
        ctB = list(df_dct[g]['cell_B'].unique())
        celltype_lst = list(set(celltype_lst).union(ctA + ctB))

    for g in df_dct.keys():
        idxo_dct[g] = list(set(idx_dct[g]) - set(idx_c))

    dfs_dct = {}
    for g in df_dct.keys():
        dfs_dct[g] = df_dct[g].loc[idxo_dct[g],:]

    celltype_lst.sort()
    # len(idx_c), celltype_lst
    
    return dfs_dct


## Get matrices summarizing the num CCIs for each condition
def cci_get_ni_mat( df_dct, remove_common = True ):
    
    if remove_common: 
        dfs_dct = cci_remove_common( df_dct )
    else:
        dfs_dct = df_dct
        
    celltype_lst = []
    for j, g in enumerate(dfs_dct.keys()):
        ctA = list(dfs_dct[g]['cell_A'].unique())
        ctB = list(dfs_dct[g]['cell_B'].unique())
        celltype_lst = list(set(celltype_lst).union(ctA + ctB))

    celltype_lst.sort()
    
    df_lst = {} 
    for g in dfs_dct.keys():
        b = dfs_dct[g]['cell_A'].isin(celltype_lst) & (dfs_dct[g]['cell_B'].isin(celltype_lst))
        dfs = dfs_dct[g].loc[b,:]
        df = pd.DataFrame(index = celltype_lst, columns = celltype_lst)
        df.loc[:] = 0
        for a, b in zip(dfs['cell_A'], dfs['cell_B']):
            df.loc[a,b] += 1

        df_lst[g] = df
                
    return df_lst

def get_cci_ni_mat( df_dct, remove_common = True ):
    return cci_get_ni_mat( df_dct, remove_common )


def cci_get_df_to_plot( df_dct, pval_cutoff = 0.01, mean_cutoff = 1, target_cells = None ):

    idx_lst_all = []
    for k in df_dct.keys():
        b = df_dct[k]['pval'] <= pval_cutoff
        b = b & df_dct[k]['mean'] >= mean_cutoff
        if target_cells is not None:
            if isinstance(target_cells, list):
                b1 = df_dct[k]['cell_A'].isin(target_cells)
                b2 = df_dct[k]['cell_B'].isin(target_cells)
                b = b & (b1 | b2)
                
        idx_lst_all = idx_lst_all + list(df_dct[k].index.values[b])

    idx_lst_all = list(set(idx_lst_all))
    display('Union of Interactions: %i' % len(idx_lst_all))    

    df_dct_to_plot = {}
    for k in df_dct.keys():
        df = df_dct[k]
        dfv = pd.DataFrame(index = idx_lst_all, columns = df.columns)
        dfv['mean'] = 0
        dfv['pval'] = 1

        idxt = list(set(idx_lst_all).intersection(list(df.index.values)))
        cols = list(df.columns.values)
        cols.remove('mean')
        cols.remove('pval')
        dfv.loc[idxt, cols] = df.loc[idxt, cols]
        dfv.loc[idxt, 'mean'] = df.loc[idxt, 'mean']
        dfv.loc[idxt, 'pval'] = df.loc[idxt, 'pval']

        gp, cp, ga, gb, ca, cb = [], [], [], [], [], []
        for s in list(dfv.index.values):
            gpt, cpt, gat, gbt, cat, cbt = cpdb_get_gp_n_cp(s)

            gp = gp + [gpt]
            cp = cp + [cpt]
            ga = ga + [gat]
            gb = gb + [gbt]
            ca = ca + [cat]
            cb = cb + [cbt]

        dfv['gene_pair'] = gp
        dfv['cell_pair'] = cp
        dfv['gene_A'] = ga
        dfv['gene_B'] = gb
        dfv['cell_A'] = ca
        dfv['cell_B'] = cb
        
        df_dct_to_plot[k] = dfv
        # print(dfv.shape)
        
    return df_dct_to_plot


####################################
### Function to get markers dict ###

def get_markers_from_deg( df_dct, ref_col = 'score',  N_mkrs = 30, 
                          # nz_pct_test_min = 0.5, nz_pct_ref_max = 0.1,
                          rem_common = True ):
## Get markers from DEG results

    df_deg = df_dct
    mkr_dict = {}
    b = True
    for key in df_deg.keys():
        if ref_col not in list(df_deg[key].columns.values):
            b = False
            break
    
    if not b:
        print('ERROR: %s not found in column name of DEG results.' % ref_col)
        return None

    for key in df_deg.keys():

        g = key.split('_vs_')[0]
        df = df_deg[key].copy(deep = True)
        df = df.sort_values([ref_col], ascending = False)
        mkr_dict[g] = list(df.iloc[:N_mkrs].index.values)

    ## Remove common markers
    if rem_common:
        lst = list(mkr_dict.keys())
        cmm = []
        for j, k1 in enumerate(lst):
            for i, k2 in enumerate(lst):
                if (k1 != k2) & (j < i):
                    lc = list(set(mkr_dict[k1]).intersection(mkr_dict[k2]))
                    cmm = cmm + lc
        cmm = list(set(cmm))

        for j, k in enumerate(lst):
            mkr_dict[k] = list(set(mkr_dict[k]) - set(cmm))

    return mkr_dict


# import pkg_resources
from importlib.resources import files

def load_surfaceome_genes( ):
    
    # data_path = pkg_resources.resource_filename('scodaviz', 'data')
    data_path = None
    try:
        # data_path = pkg_resources.resource_filename('scoda', 'default_optional_files')
        data_path = str( files('scoda').joinpath('default_optional_files') )
        if not os.path.isdir(data_path):
            data_path = None
    except:
        pass
    
    if data_path is None:
        try:
            # data_path = pkg_resources.resource_filename('scodaviz', 'data')
            data_path = str( files('scodaviz').joinpath('data') )
            if not os.path.isdir(data_path):
                data_path = None
        except:
            pass

    if data_path is None:
        return data_path
        
    with open( data_path + '/surfaceome_genes.txt', 'r' ) as f:
        lines = f.readlines()
        gene_lst = []
        for l in lines:
            gene_lst.append(l[:-1])

    gene_lst = ['%s' % (g.lower())  for g in gene_lst]
        
    return gene_lst


def find_condition_specific_markers( df_deg_dct, 
                                     score_col = 'nz_pct_score',
                                     n_markers_max = 100,
                                     score_cutoff = 0.25,
                                     pval_cutoff = 0.05,
                                     nz_pct_fc_cutoff = 1.2,
                                     verbose = False,
                                     surfaceome_only = True ):

    if surfaceome_only:
        surfaceome_gene_lst = load_surfaceome_genes( )
        if surfaceome_gene_lst is None:
            surfaceome_only = False
            
    s = ''
    df_deg_dct_updated = {}
    for k in df_deg_dct.keys():
        
        b = df_deg_dct[k][score_col] >= score_cutoff
        if score_col == 'nz_pct_score':
            if 'nz_pct_pval' in list(df_deg_dct[k].columns.values):
                b = b & (df_deg_dct[k]['nz_pct_pval'] <= pval_cutoff)  
            else:
                b = b & (df_deg_dct[k]['pval'] <= pval_cutoff)                  
            b = b & (df_deg_dct[k]['nz_pct_test'] > df_deg_dct[k]['nz_pct_ref']*nz_pct_fc_cutoff)  
        else:            
            b = b & (df_deg_dct[k]['pval'] <= pval_cutoff)  
            
        if surfaceome_only:
            glst = [g.lower() for g in list(df_deg_dct[k].index.values)]
            glst = pd.Series( glst )
            b = b & np.array(glst.isin(surfaceome_gene_lst))
        df_deg_dct_updated[k] = df_deg_dct[k].loc[b,:].drop(columns = ['Rp']).copy(deep = True)
        df_deg_dct_updated[k].set_index('gene', inplace = True)
        s = s + '   %s (%i -> %i) \n' % (k, len(b), np.sum(b))
        
    if verbose: print('N_markers: \n' + s[:-2])
    
    mkr_dict = get_markers_from_deg( df_deg_dct_updated, 
                                     N_mkrs = n_markers_max, 
                                     ref_col = score_col,
                                     rem_common = False )
    
    s = ''
    for k in mkr_dict.keys():
        s = s + '%s (%i), ' % (k, len(mkr_dict[k]))
    if verbose: print('N_markers_selected: ' + s[:-2])
    
    ## Print results
    mkrs_all = []
    for key in mkr_dict.keys():
        mkr_dict[key].sort()
        lst = mkr_dict[key]
        mkrs_all = mkrs_all + lst
        # if verbose: print('%s (%i): ' % (key, len(lst)), lst)

    return mkr_dict, df_deg_dct_updated 


def save_to_excel( df_dct, file_name, index = True ):
    
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        if isinstance(df_dct, pd.DataFrame):
            df.to_excel(writer, index=index)
            b = True                    
        elif isinstance(df_dct, dict):
            for key in df_dct.keys():
                df = df_dct[key]
                if df.shape[0] > 0:
                    df.to_excel(writer, sheet_name=key, index=index)
        elif isinstance(df_dct, list):
            for j, df in enumerate(df_dct):
                if df.shape[0] > 0:
                    df.to_excel(writer, sheet_name='Sheet%i' % (j+1), index=index)
    return




def find_tumor_origin( adata, tid_col = 'ploidy_dec', ref_taxo_level = 'celltype_major',
                       tumor_name = 'Aneuploid'):
    
    b = adata.obs[tid_col] == tumor_name
    pcnt = adata.obs.loc[b, ref_taxo_level].value_counts()
    tumor_origin = [pcnt.index[0]]
    tumor_origin_celltype = pcnt.index[0]
    if (tumor_origin_celltype == 'unassigned'):
        if len(pcnt) > 1:
            if (pcnt[1] >= pcnt[0]*0.05):
                tumor_origin = tumor_origin + [pcnt.index[1]]
                tumor_origin_celltype = pcnt.index[1]
    #'''
    elif len(pcnt) > 1:
        if pcnt.index[1] == 'unassigned':
            tumor_origin = tumor_origin + ['unassigned']
    #'''
    return tumor_origin_celltype


def filter_gsa_result( dct, neg_log_p_cutoff ):
    
    dct_t = {}
    for kk in dct.keys():
        dft = dct[kk]
        b = dft['-log(p-val)'] >= neg_log_p_cutoff
        dct_t[kk] = dft.loc[b,:]
    return dct_t


### Example 
# lst = [adata_t.obs['cell_type_major_pred'], adata_t.obs['tumor_dec'], adata_t.obs['subtype']] #, 
# plot_sankey_e( lst, title = None, fs = 12, WH = (800, 600), th = 0, title_y = 0.85 )

def plot_sankey( lst, title = None, fs = 12, WH = (700, 800), th = 0, title_y = 0.85 ):
    
    if len(lst) < 2:
        print('ERROR: Input must have length of 2 or more.')
        return
    
    W = WH[0]
    H = WH[1]

    sall = []
    tall = []
    vall = []
    lbl_all = []
    label_lst = []
    
    nn_cnt = 0
    for nn in range(len(lst)-1):
        source_in = ['L%i_%s' % (nn+1, a) for a in list(lst[nn])]
        target_in = ['L%i_%s' % (nn+2, a)  for a in list(lst[nn+1])]
                
        source = pd.Series(source_in).astype(str)
        b = source.isna()
        source[b] = 'N/A'
        target = pd.Series(target_in).astype(str)
        b = target.isna()
        target[b] = 'N/A'

        src_lst = list(set(source))
        tgt_lst = list(set(target))
        src_lst.sort()
        tgt_lst.sort()

        if th > 0:
            bx = np.full(len(source), True)
            for k, s in enumerate(src_lst):
                bs = source == s
                for m, t in enumerate(tgt_lst):
                    bt = target == t
                    b = bs & bt
                    if np.sum(b) < th:
                        bx[b] = False
            source = source[bx]
            target = target[bx]

            src_lst = list(set(source))
            tgt_lst = list(set(target))
            src_lst.sort()
            tgt_lst.sort()

        src = []
        tgt = []
        val = []
        sl_lst = []
        tl_lst = []
        Ns = len((src_lst))
        for k, s in enumerate(src_lst):
            bs = source == s
            for m, t in enumerate(tgt_lst):
                bt = target == t
                b = bs & bt
                if (np.sum(b) > 0):
                    if s not in sl_lst:
                        sn = len(sl_lst)
                        sl_lst.append(s)
                    else:
                        for n, lbl in enumerate(sl_lst):
                            if s == lbl:
                                sn = n
                                break

                    if t not in tl_lst:
                        tn = len(tl_lst) + Ns
                        tl_lst.append(t)
                    else:
                        for n, lbl in enumerate(tl_lst):
                            if t == lbl:
                                tn = n + Ns
                                break

                    src.append(sn)
                    tgt.append(tn)
                    val.append(np.sum(b))
                    label_lst = sl_lst + tl_lst
                    nn_cnt += 1

        if (nn == 0): # | (nn_cnt == 0):
            src2 = src
            tgt2 = tgt
        else:
            lbl_ary = np.array(lbl_all)
            sseq = np.arange(len(lbl_ary))
            src2 = []
            for a in src:
                s = sl_lst[a]
                b = lbl_ary == s
                if np.sum(b) == 1:
                    m = sseq[b][0]
                    src2.append(m)
                else:
                    print('ERROR ... S')
            
            # src2 = [(a + len(lbl_all) - len(sl_lst)) for a in src]
            tgt2 = [(a + len(lbl_all) - len(sl_lst)) for a in tgt]
        
        sall = sall + copy.deepcopy(src2)
        tall = tall + copy.deepcopy(tgt2)
        vall = vall + copy.deepcopy(val)
        if nn == 0:
            lbl_all = copy.deepcopy(label_lst)
        else:
            lbl_all = lbl_all + copy.deepcopy(tl_lst)
    '''
    mat = np.array([sall,tall,vall])
    print(mat)
    print(lbl_all)
    '''      
        
    link = dict(source = sall, target = tall, value = vall)
    node = dict(label = lbl_all, pad=50, thickness=5)
    data = go.Sankey(link = link, node=node)
    layout = go.Layout(height = H, width = W)
    # plot
    fig = go.Figure(data, layout)
    if title is not None:
        fig.update_layout(
            title={
                'text': '<span style="font-size: ' + '%i' % fs + 'px;">' + title + '</span>',
                'y':title_y,
                'x':0.5,
                # 'font': 12,
                'xanchor': 'center',
                'yanchor': 'top'})    
    fig.show()   
    return


### Example 
# plot_population(df_pct, figsize=(6, 4), dpi = 80, return_fig = False)
# df_cnt
    
def plot_population(df_pct, bar_width = 0.6, title = None, title_fs = 12, ylabel = None,
                    label_fs = 11, tick_fs = 10, xtick_rot = 45, xtick_ha = 'center',
                    legend_fs = 10, legend_loc = 'upper left', bbox_to_anchor = (1,1), 
                    legend_ncol = 1, cmap = 'Spectral', figsize=(5, 3), dpi = 100):    

    if cmap is None:
        cmap = 'Spectral'
    color_map = plt.get_cmap(cmap)
    color = color_map(np.arange(df_pct.shape[1])/df_pct.shape[1])

    fig = plt.figure(dpi = dpi)
    ax = df_pct.plot.bar(stacked = True, rot = xtick_rot, figsize = figsize, 
                         color = color, width = bar_width)
    ax.legend( list(df_pct.columns.values), bbox_to_anchor=bbox_to_anchor, 
               loc = legend_loc, fontsize = legend_fs, ncol = legend_ncol )
    plt.xticks(fontsize=tick_fs, ha = xtick_ha)
    plt.yticks(fontsize=tick_fs)
    if isinstance(ylabel, str):
        plt.ylabel(ylabel, fontsize = label_fs)
    plt.title(title, fontsize = title_fs)
    plt.show()
    return


def get_sample_and_group_from_sample_ext( sample_ext ):

    idx = list(sample_ext)
    slst = []
    clst = []
    for i in idx:
        p = i.find(' ')
        if p >= 0:
            clst.append(i[:p])
            slst.append(i[(p+1):])
        else:
            clst.append('-')
            slst.append(i)
            
    return slst, clst

    
def plot_population_grouped(df_pct, sample_group_map = None, sort_by = [], bar_width = 0.6, 
                            title = None, title_y_pos = 1.1, title_fs = 14, ylabel = None,
                            label_fs = 11, tick_fs = 10, xtick_rot = 45, xtick_ha = 'center',
                            legend_fs = 10, legend_loc = 'upper left', bbox_to_anchor = (1,1), 
                            legend_ncol = 1, cmap = 'Spectral', figsize=(5, 3), dpi = 100,
                            wspace=0.06, hspace=0.25 ):    

    df = df_pct.copy(deep = True)
    if 'Group' in list(df.columns.values):
        sample_group_map = dict(zip( df.index.values, df['Group'] ))
        # df = df.drop( columns = ['Group'] )  
    elif sample_group_map is None:
        slst, clst = get_sample_and_group_from_sample_ext( df_pct.index.values )                
        sample_group_map = dict(zip( slst, clst ))
        
        df = pd.DataFrame( np.array(df), index = slst, columns = df_pct.columns )
        df['Group'] = clst
    else:
        df['Group'] = list(df.index.values)
        df['Group'] = df['Group'].replace(sample_group_map)

    if cmap is None:
        cmap = 'Spectral'
    color_map = plt.get_cmap(cmap)
    color = color_map(np.arange(df.drop(columns = ['Group']).shape[1])/df.drop(columns = ['Group']).shape[1])

    num_p = []

    glst = list(df['Group'].unique())
    glst.sort()

    cnt = df['Group'].value_counts()
    for g in glst:
        num_p.append(cnt.loc[g])

    nr, nc = 1, len(glst)
    fig, axes = plt.subplots(nrows=nr, ncols=nc, constrained_layout=False, 
                             gridspec_kw={'width_ratios': num_p}, dpi = dpi)
    fig.tight_layout() 
    if title is not None: 
        fig.suptitle(title, x = 0.5, y = title_y_pos, fontsize = title_fs, ha = 'center')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=wspace, hspace=hspace)

    cnt = 0
    for j, g in enumerate(glst):
        b = df['Group'] == g
        dft = df.loc[b,:].drop(columns = ['Group'])
        if len(sort_by) > 0:
            dft = dft.sort_values(sort_by)

        if nc <= 1: ax_sel = axes
        else: ax_sel = axes[j+cnt]
            
        ax = dft.plot.bar(width = bar_width, stacked = True, ax = ax_sel, 
                          figsize = figsize, legend = None, color = color)
        ax.set_title('%s' % (g), fontsize = title_fs-2)
        if j != 0:
            # ax.set_yticks([])
            pass
        else:
            if isinstance(ylabel, str):
                ax.set_ylabel(ylabel, fontsize = label_fs)

        ax.tick_params(axis='x', labelsize=tick_fs) # , rotation = xtick_rot)
        ax.tick_params(axis='y', labelsize=tick_fs)
        labels = ax.get_xticklabels()
        ax.set_xticklabels(labels, rotation=xtick_rot, ha=xtick_ha)
            
        if g == glst[-1]: 
            ax.legend(dft.columns.values, loc = legend_loc, bbox_to_anchor = bbox_to_anchor, 
                       fontsize = legend_fs, ncol = legend_ncol)  
        else:
            pass
    plt.show()
    
    return


def plot_pct_box( df_pct, sg_map = None, ncols = 3, figsize = None, dpi = 100,
                  title = None, title_y_pos = 1.05, title_fs = 14, rename_cells = None,
                  label_fs = 11, tick_fs = 10, xtick_rot = 0, xtick_ha = 'center', group_order = None,
                  annot = True, annot_ref = None, annot_fmt = 'simple', annot_fs = 10, 
                  ws_hs = (0.3, 0.3), ylabel = None, cmap = 'tab10',
                  stripplot = True, stripplot_ms = 1, stripplot_jitter = True ):

    title2_fs = None
    if title2_fs is None:
        title2_fs = title_fs - 2
        
    df = df_pct.copy(deep = True)
    if 'Group' in list(df.columns.values):
        sg_map = dict(zip( df.index.values, df['Group'] ))
        df = df.drop( columns = ['Group'] )
    elif isinstance(sg_map, pd.Series):
        sg_map = dict(zip( df.index.values, sg_map ))
    
    ## index 이름에서 '--'를 '\n'로 대체
    idx_org = list(df.columns.values)
    idx_new = [s.replace('--', '\n') for s in idx_org]
    rend = dict(zip(idx_org, idx_new))
    df = df.rename(columns = rend)
        
    # nr, nc = nr_nc
    nc = ncols
    nr = int(np.ceil(df.shape[1]/nc))
    if figsize is None:
        figsize = (3*nc,3*nr)
    else:
        figsize = (figsize[0]*nc,figsize[1]*nr)
        
    ws, hs = ws_hs
    fig, axes = plt.subplots(figsize = figsize, dpi=dpi, nrows=nr, ncols=nc, constrained_layout=False)
    fig.tight_layout() # Or equivalently,  "plt.tight_layout()"
    if title is not None:
        fig.suptitle('%s' % title, x = 0.5, y = title_y_pos, fontsize = title_fs, ha = 'center')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=ws, hspace=hs)

    items = list(df.columns.values)

    df['Group'] = list(df.index.values)
    df['Group'] = df['Group'].replace(sg_map)

    lst = df['Group'].unique()

    cnt = 0
    for kk, item in enumerate(items):
        plt.subplot(nr,nc,cnt+1)
        b = df[item].isnull()
        pcnt = df.loc[~b,'Group'].value_counts()
        b1 = pcnt > 1
        group_sel = pcnt.index.values[b1].tolist()

        if len(group_sel) > 1:
            b = (~b) & df['Group'].isin(group_sel)
            
            lst = df.loc[b, 'Group'].unique()
            lst_pair = []
            if annot_ref in lst:
                for k, l1 in enumerate(lst):
                    if l1 != annot_ref:
                        lst_pair.append((annot_ref, l1))
            else:
                for k, l1 in enumerate(lst):
                    for j, l2 in enumerate(lst):
                        if j <  k:
                            lst_pair.append((l1, l2))
        
            ax = sns.boxplot(data = df.loc[b,:], x = 'Group', y = item, order = group_order,
                             hue = 'Group', palette=cmap )
            if stripplot:
                sns.stripplot(x='Group', y=item, data=df.loc[b,:],  
                              color="black", order = group_order, size = stripplot_ms, 
                              jitter = stripplot_jitter )
            if cnt%nc == 0: 
                ax.set_ylabel(ylabel, fontsize = label_fs)                
            else: 
                ax.set_ylabel(None)
                
            if cnt >= nc*(nr-1): 
                ax.set_xlabel('Condition', fontsize = label_fs)
            else: 
                ax.set_xlabel(None)

            title = item
            if (rename_cells is not None) & isinstance(rename_cells, dict):
                for key in rename_cells.keys():
                    title = title.replace(key, rename_cells[key])
            ax.set_title(title, fontsize = title2_fs)
            
            if cnt < (nr*nc - nc):
                # plt.xticks([])
                plt.xticks(rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
                plt.yticks(fontsize = tick_fs)
            else:
                plt.xticks(rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
                plt.yticks(fontsize = tick_fs)
    
            if annot:
                '''
                add_stat_annotation(ax, data=df.loc[b,:], x = 'Group', y = item, 
                                    order = group_order,
                            box_pairs=lst_pair, loc='inside', fontsize = annot_fs,
                            test='t-test_ind', text_format=annot_fmt, verbose=0)
                '''
                annotator = Annotator(ax, pairs=lst_pair, data=df.loc[b,:], 
                                      x="Group", y=item, order=group_order)
                annotator.configure(test='t-test_ind', text_format=annot_fmt, 
                                    loc='inside', verbose=False, show_test_name=False,
                                    fontsize = annot_fs)
                annotator.apply_and_annotate()   

            cnt += 1
            #'''
    
    if (cnt < (nr*nc)):
        if (nr == 1):
            for k in range(nr*nc - cnt):
                axes[cnt%nc + k].axis("off")
        else:
            for k in range(nr*nc - cnt):
                r = nr - int(k/nc)
                axes[r-1][nc - k%nc -1].axis("off")
        
    plt.show()
    return 


import numbers

def plot_violin( df, genes_lst, group_col = 'group', scale = 'width', group_order = None, 
                 inner = 'box', width = 0.9, linewidth = 0.3, bw = 'scott',
                 figsize = (3,2), dpi = 100, text_fs = 10, title = 'Title', title_fs = 14, title_y_pos = 1, 
                 label_fs = 11, tick_fs = 10, xtick_rot = 0, xtick_ha = 'center', 
                 ncols = 2, wspace = 0.15, hspace = 0.4, ylim = None, ylabel = None,
                 cmap = 'tab10' ):

    nr, nc = int(np.ceil(len(genes_lst)/ncols)), int(ncols) # len(df_deg_dct.keys())
    fig, axes = plt.subplots(figsize = (figsize[0]*nc,figsize[1]*nr), nrows=nr, ncols=nc, # constrained_layout=True, 
                             gridspec_kw={'width_ratios': [1]*nc}, dpi = dpi)
    fig.tight_layout() 
    if title is not None:
        fig.suptitle(title, x = 0.5, y = title_y_pos, fontsize = title_fs, ha = 'center')
        
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, 
                        wspace=wspace, hspace=hspace)
    cnt = 0
    for j, gene in enumerate(genes_lst): 
    
        plt.subplot(nr,nc, int(j+1))
        sns.violinplot(x = group_col, y = gene, data = df, density_norm = scale, 
                       linewidth = linewidth, hue = group_col, palette=cmap,
                       order = group_order, width = width, inner = inner, bw_method = bw)
        '''
        plt.title('%s' % (gene), fontsize = label_fs + 1)
        plt.yticks(fontsize = tick_fs)
        plt.xticks(None, rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
        plt.xlabel(None)
        if j%nc == 0: plt.ylabel('Log exp.', fontsize = label_fs)
        else: plt.ylabel(None)
        '''
        if ylim is not None:
            if isinstance( ylim, list ):
                if isinstance( ylim[0], numbers.Number ):
                    plt.ylim(ylim)
                elif isinstance( ylim[0], list ) & (len(ylim) > j):
                    plt.ylim(ylim[j])
        
        plt.title('%s' % (gene), fontsize = label_fs + 1)
        if j%nc == 0: 
            if isinstance( ylabel, str ):
                plt.ylabel( ylabel, fontsize = label_fs )
        else: plt.ylabel(None)
            
        if j >= nc*(nr-1): plt.xlabel('Condition', fontsize = label_fs)
        else: plt.xlabel(None)
        if j < (nr*nc - nc):
            plt.xticks([])
            plt.yticks(fontsize = tick_fs)
        else:
            plt.xticks(rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
            plt.yticks(fontsize = tick_fs)
        
        cnt += 1

    if nc*nr > len(genes_lst):
        for j in range(nc*nr-len(genes_lst)):
            k = j + len(genes_lst) + 1
            ax = plt.subplot(nr,nc,k)
            ax.axis('off')

    plt.show()
    return


## CPDB plot

###################################
### Plot functions for CellPhoneDB

def cci_get_all_pairs( cci_df_dct ):
    
    lst = list(cci_df_dct.keys())
    lst.sort()
    
    gps = []
    cps = []
    for g in lst:
        dfv = cci_df_dct[g]
        gps = gps + list(dfv['gene_pair'])
        cps = cps + list(dfv['cell_pair'])
    
    gps = list(set(gps))
    cps = list(set(cps))

    return gps, cps


def plot_cci_dot_( dfv, n_gene_pairs = None, 
                  pval_cutoff = 0.05, mean_cutoff = 0.1, 
                  target_cells = [], target_genes = [], 
                  legend_fs = 11, legend_mkr_sz = 6, rename_cells = None,
                  tick_fs = 6, xtick_rot = 90, xtick_ha = 'center', 
                  title = None, title_fs = 14, dot_size_max = 1,
                  dpi = 100, swap_ax = False, cmap = None,
                  gene_pair_lst = None, cell_pair_lst = None, y_scale = 1.2 ):
                  # plot_all_gene_pairs = False, plot_all_cell_pairs = False ):

    '''
    gene_pair_lst = None
    cell_pair_lst = None
    if plot_all_gene_pairs | plot_all_cell_pairs:
        gps, cps = cci_get_all_pairs( cci_df_dct )
        if plot_all_gene_pairs: gene_pair_lst = gps
        if plot_all_cell_pairs: cell_pair_lst = cps
    #'''
    
    dfs = dfv.copy(deep = True)
    
    if isinstance(target_cells, list):
        if (len(target_cells) > 0):
            b = (dfs['cell_A'].isin(target_cells) & dfs['cell_B'].isin(target_cells))
            dfs = dfs.loc[b,:]
        
    if isinstance(target_genes, list):
        if (len(target_genes) > 0):
            b = (dfs['gene_A'].isin(target_genes) | dfs['gene_B'].isin(target_genes))
            dfs = dfs.loc[b,:]
    
    if n_gene_pairs is None:
        dfs = dfs.sort_values(by = ['gene_pair', 'cell_pair'])
        b = dfs['pval'] <= pval_cutoff
        b = b & dfs['mean'] >= mean_cutoff    
        dfp = dfs.loc[b,:]
    else:
        dfs['neg_mean'] = -dfs['mean']
        dfp = dfs.sort_values(by = ['pval', 'neg_mean'], ascending = True)
        ilst = dfp['gene_pair'].tolist()
        ilst2 = []
        j = 0
        for j, i in enumerate(ilst):
            if len(list(set(ilst[:j]))) > n_gene_pairs:
                break                
        dfp = dfp.iloc[:j]
    
    if dfp.shape[0] == 0:
        print('WARNING: no interactions met the conditions you provide. ')
        return
    else:
        if (rename_cells is not None) & isinstance(rename_cells, dict):
            cell_pairs = list(dfp['cell_pair'])
            cell_pairs_new = []
            for i in cell_pairs:
                for key in rename_cells.keys():
                    i = i.replace(key, rename_cells[key])
                cell_pairs_new.append(i)
            dfp['cell_pair'] = cell_pairs_new
                
        dfp = dfp.sort_values(by = ['gene_pair', 'cell_pair'])
        if swap_ax == False:
            a = 'gene_pair'
            b = 'cell_pair'
            apl = gene_pair_lst
            bpl = cell_pair_lst
        else:
            b = 'gene_pair'
            a = 'cell_pair'
            apl = cell_pair_lst 
            bpl = gene_pair_lst

        if apl is None:
            y = len(set(dfp[a]))
        else:
            y = len(apl)
            
        if bpl is None:
            x = len(set(dfp[b]))
        else:
            x = len(bpl)
        
        print('%i %ss, %i %ss found' % (y, a, x, b))
        
        pv = -np.log10(dfp['pval']+1e-10).round()
        pvmn, pvmx = int(np.min(pv)), int(np.max(pv))
        
        mn = np.log2((1+dfp['mean']))
        np.min(mn), np.max(mn)    
        
        w = x/6
        # sc.settings.set_figure_params(figsize=(w, w*y_scale*(y/x)), 
        #                               dpi=dpi, facecolor='white')
        plt.rcParams['figure.figsize'] = (w, w*y_scale*(y/x))      
        plt.rcParams['figure.dpi'] = dpi             
        fig, ax = plt.subplots()

        if apl is None:
            a_lst = list(dfp[a].unique())
        else:
            a_lst = apl
        a_lst.sort()
        
        if bpl is None:
            b_lst = list(dfp[b].unique())
        else:
            b_lst = bpl
        b_lst.sort()

        ax.autoscale(False)
        # Set the sorted y-ticks.
        La = len(a_lst)
        ax.set_yticks(np.arange(La))
        ax.set_yticklabels(a_lst)
        ax.set_ylim([-1, La])
        y_map = dict(zip(a_lst, list(np.arange(La))))
        
        # Set the x-ticks.
        Lb = len(b_lst)
        ax.set_xticks(np.arange(Lb))
        ax.set_xticklabels(b_lst)  # `ax.set_xticklabels("abcde")` would work too.
        ax.set_xlim([-1, Lb])
        x_map = dict(zip(b_lst, list(np.arange(Lb))))
        
        mul = legend_mkr_sz*dot_size_max*0.6
        lst_b = [x_map[x] for x in list(dfp[b])]
        lst_a = [y_map[y] for y in list(dfp[a])]
        
        scatter = ax.scatter(lst_b, lst_a, s = pv*mul, c = mn, 
                             linewidth = 0, cmap = cmap)
    
        kw = dict(prop="colors", num=5, fmt="{x:.1f}", # color=scatter.cmap(0.7), 
                  func=lambda s: (s))
        legend1 = ax.legend(*scatter.legend_elements(**kw),
                            loc='upper left', 
                            bbox_to_anchor=(1+1/x, 0.5), 
                            title=' log2(m) ', 
                            fontsize = legend_fs)
        legend1.get_title().set_fontsize(legend_fs)
        ax.add_artist(legend1)
    
        # produce a legend with a cross section of sizes from the scatter
        kw = dict(prop="sizes", num=4, fmt="{x:.0f}", # color=scatter.cmap(0.7), 
                  func=lambda s: (s/mul))
        legend2 = ax.legend(*scatter.legend_elements(**kw),
                            loc='lower left', 
                            bbox_to_anchor=(1+1/x, 0.5), 
                            title='-log10(p)', 
                            fontsize = legend_fs)        
        legend2.get_title().set_fontsize(legend_fs)
    
        if title is not None: plt.title(title, fontsize = title_fs)
        plt.yticks(fontsize = tick_fs)
        plt.xticks(rotation = xtick_rot, ha=xtick_ha, fontsize = tick_fs)
        plt.margins(x=0.6/x, y=0.6/y)
        plt.grid()
        plt.show()   
    return


def plot_cci_dot( cci_df_dct, n_gene_pairs = None, 
                  target_cells = [], target_genes = [], 
                  pval_cutoff = 0.05, mean_cutoff = 0.1, 
                  legend_fs = 11, legend_mkr_sz = 6, rename_cells = None,
                  tick_fs = 6, xtick_rot = 90, xtick_ha = 'center', 
                  title = None, title_fs = 14, dot_size_max = 1,
                  dpi = 100, swap_ax = False, cmap = None,
                  gene_pair_lst = None, cell_pair_lst = None, y_scale = 1.2 ):

    '''
    if rename_cells is not None:
        if rename_cells == True:
            deg_base = adata.uns['analysis_parameters']['CCI_DEG_BASE']
            rename_dct = get_abbreviations()
            rename_cells = rename_dct[deg_base]
        elif isinstance( rename_cells, dict ):
            pass
        else:
            rename_cells = None
    '''

    if isinstance(cci_df_dct, pd.DataFrame):
        dfv = cci_df_dct
        ax = plot_cci_dot_( dfv, n_gene_pairs = n_gene_pairs, 
                      target_cells = target_cells, target_genes = target_genes, 
                      pval_cutoff = pval_cutoff, mean_cutoff = mean_cutoff, 
                      legend_fs = legend_fs, legend_mkr_sz = legend_mkr_sz, rename_cells = rename_cells,
                      tick_fs = tick_fs, xtick_rot = xtick_rot, xtick_ha = xtick_ha, 
                      title = title, title_fs = title_fs, dot_size_max = dot_size_max,
                      dpi = dpi, swap_ax = swap_ax, cmap = cmap,
                      gene_pair_lst = gene_pair_lst, cell_pair_lst = cell_pair_lst, y_scale = y_scale )
        return ax
    elif isinstance(cci_df_dct, dict):
        axes = []
        for g in cci_df_dct.keys():
            dfv = cci_df_dct[g]
            ax = plot_cci_dot_( dfv, n_gene_pairs = n_gene_pairs, 
                          target_cells = target_cells, target_genes = target_genes, 
                          pval_cutoff = pval_cutoff, mean_cutoff = mean_cutoff, 
                          legend_fs = legend_fs, legend_mkr_sz = legend_mkr_sz, rename_cells = rename_cells,
                          tick_fs = tick_fs, xtick_rot = xtick_rot, xtick_ha = xtick_ha, 
                          title = 'CCI for %s' % g, title_fs = title_fs, dot_size_max = dot_size_max,
                          dpi = dpi, swap_ax = swap_ax, cmap = cmap,
                          gene_pair_lst = gene_pair_lst, cell_pair_lst = cell_pair_lst, y_scale = y_scale )
            axes.append(ax)            
        return axes
        
    else:
        print('ERROR: The input was not suitably formatted. ')
        return None
        
    return


def cpdb_get_gp_n_cp(idx):
    
    items = idx.split('--')
    gpt = items[0]
    cpt = items[1]
    gns = gpt.split('_')
    ga = gns[0]
    gb = gns[1]
    cts = cpt.split('|')
    ca = cts[0]
    cb = cts[1]
    
    return gpt, cpt, ga, gb, ca, cb
    
###########################    
### Circle plot for CCI ###
    
def center(p1, p2):
    return (p1[0]+p2[0])/2, (p1[1]+p2[1])/2

def norm( p ):
    n = np.sqrt(p[0]**2 + p[1]**2)
    return n

def vrot( p, s ):
    v = (np.array([[0, -1], [1, 0]]).dot(np.array(p)))
    v = ( v/norm(v) )
    return v #, v2
    
def vrot2( p, t ):
    v = (np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]).dot(p))
    return v #, v2
    
def get_arc_pnts( cp, R, t1, t2, N):
    
    a = (t1 - t2)
    if a >= math.pi:
        t2 = t2 + 2*math.pi
    elif a <= -math.pi:
        t1 = t1 + 2*math.pi
    
    N1 = (N*np.abs(t1 - t2)/(2*math.pi))
    # print(N1)
    s = np.sign(t1 - t2)
    t = t2 + np.arange(N1+1)*(s*2*math.pi/N)
    # if t.max() > (math.pi*2): t = t - math.pi*2
    
    x = np.sin(t)*R + cp[0]
    y = np.cos(t)*R + cp[1]
    x[-1] = np.sin(t1)*R + cp[0]
    y[-1] = np.cos(t1)*R + cp[1]
        
    return x, y, a

def get_arc( p1, p2, R, N ):
    
    A = norm(p1 - p2)
    pc = center(p1, p2)
    
    a = np.sqrt((R*A)**2 - norm(p1 - pc)**2)
    c = pc + vrot(p1 - pc, +1)*a

    d1 = p1 - c
    t1 = np.arctan2(d1[0], d1[1])
    d2 = p2 - c
    t2 = np.arctan2(d2[0], d2[1])

    x, y, t1 = get_arc_pnts( c, R*A, t2, t1, N)
    
    return x, y, c


def get_circ( p1, R, N ):
    
    pp = np.arange(N)*(2*math.pi/N)
    px = np.sin(pp)*0.5
    py = np.cos(pp)
    pnts = np.array([px, py])
    
    t = -np.arctan2(p1[0], p1[1])
    pnts = vrot2( pnts, t+math.pi )*R
    pnts[0,:] = pnts[0,:] + p1[0]*(1+R)
    pnts[1,:] = pnts[1,:] + p1[1]*(1+R)
    x = pnts[0,:]
    y = pnts[1,:]
    c = np.array([0,0])
    
    return x, y, c


def plot_cci_circ( df_in, figsize = (10, 10), dpi = 10, title = None, title_fs = 16, 
                   text_fs = 14, num_fs = 12, margin = 0.08, alpha = 0.5, 
                   linewidth_max = 10, linewidth_log = False, 
                   R_curvature = 4, node_size = 10, rot = True, 
                   cmap = 'Spectral', ax = None, show = True):
            
    linewidth_scale = 0
    log_lw = linewidth_log
    lw_max = linewidth_max
    lw_scale = linewidth_scale
    
    Rs = 0.1
    N = 500
    R = R_curvature
    df = df_in.copy(deep = True)
    mxv = df_in.max().max()
    
    if ax is None: 
        plt.figure(figsize = figsize, dpi = dpi)
        ax = plt.gca()
        
    # color_lst = ['orange', 'navy', 'green', 'gold', # 'lime', 'magenta', \
    #         'turquoise', 'red', 'royalblue', 'firebrick', 'gray']
    # color_map = cm.get_cmap(cmap)
    color_map = colormaps[cmap]
    if df.shape[0] > 1:
        color_lst = [color_map(i/(df.shape[0]-1)) for i in range(df.shape[0])]
    else:
        mmm = 10
        color_lst = [color_map(i/(mmm-1)) for i in range(mmm)]

    clst = list(df.index.values) 

    M = df.shape[0]
    if M > 1:
        pp = np.arange(M)*(2*math.pi/M)
    else:
        pp = np.arange(mmm)*(2*math.pi/mmm)
    px = np.sin(pp)
    py = np.cos(pp)
    pnts = np.array([px, py])
    
    for j in range(M):
        p1 = pnts[:,j]
        for k in range(M):
            p2 = pnts[:,k]
            
            val = df.loc[clst[j], clst[k]]
            if lw_scale > 0:
                lw = val*lw_scale
            elif lw_max > 0:
                lw = val*lw_max/mxv
            else:
                lw = val
            if log_lw: lw = np.log2(lw)                    
                    
            if (df.loc[clst[j], clst[k]] != 0): # & (j!= k):

                if j == k:
                    x, y, c = get_circ( p1, 0.1, N )
                    K = int(len(x)*0.5)
                    d = vrot(p1, 1)
                    d = d*0.05/norm(d)
                elif (j != k) :
                    x, y, c = get_arc( p1, p2, R, N )

                    K = int(len(x)*0.5)
                    d = (p2 - p1)
                    d = d*0.05/norm(d)

                q2 = np.array([x[K], y[K]])
                q1 = np.array([x[K] - d[0], y[K] - d[1]])

                s = norm(q1 - q2)
                
                ha = 'center'
                if c[0] < -1:
                    ha = 'left'
                elif c[0] > 1:
                    ha = 'right'
                    
                va = 'center'
                if c[1] < -1:
                    va = 'bottom'
                elif c[1] > 1:
                    va = 'top'
                    
                if norm(q2) <= 0.7: # mnR*2:
                    ha = 'center'
                    va = 'center'
                    
                if ax is None: 
                    plt.plot(x, y, c = color_lst[j], linewidth = lw, alpha = alpha)
                    if j != k:
                        plt.arrow(q1[0], q1[1], q2[0]-q1[0], q2[1]-q1[1], linewidth = lw,
                              head_width=s/2, head_length=s, 
                              fc=color_lst[j], ec=color_lst[j])
                    plt.text( q2[0], q2[1], ' %i ' % val, fontsize = num_fs, 
                              va = va, ha = ha)
                else:
                    ax.plot(x, y, c = color_lst[j], linewidth = lw, alpha = alpha)
                    if j != k:
                        ax.arrow(q1[0], q1[1], q2[0]-q1[0], q2[1]-q1[1], linewidth = lw,
                              head_width=0.05*lw/lw_max, head_length=s, alpha = alpha, 
                              fc=color_lst[j], ec=color_lst[j])
                    ax.text( q2[0], q2[1], '%i' % val, fontsize = num_fs, 
                             va = va, ha = ha)

            elif (df.loc[clst[j], clst[k]] != 0) & (j== k):
                x, y, c = get_circ( p1, Rs, N )
                K = int(len(x)*0.5)
                d = vrot(p1, 1)
                d = d*0.05/norm(d)

                q2 = np.array([x[K], y[K]])
                q1 = np.array([x[K] - d[0], y[K] - d[1]])

                s = norm(q1 - q2)
                
                ha = 'center'
                if c[0] < -1:
                    ha = 'left'
                elif c[0] > 1:
                    ha = 'right'
                    
                va = 'center'
                if c[1] < -1:
                    va = 'bottom'
                elif c[1] > 1:
                    va = 'top'
                    
                if norm(q2) <= 0.7: # mnR*2:
                    ha = 'center'
                    va = 'center'
                    
                if ax is None: 
                    plt.plot(x, y, c = color_lst[j], linewidth = lw, alpha = alpha)
                    plt.arrow(q1[0], q1[1], q2[0]-q1[0], q2[1]-q1[1], linewidth = lw,
                              head_width=s/2, head_length=s, 
                              fc=color_lst[j], ec=color_lst[j])
                    plt.text( q2[0], q2[1], ' %i ' % val, fontsize = num_fs, 
                              va = va, ha = ha)
                else:
                    ax.plot(x, y, c = color_lst[j], linewidth = lw, alpha = alpha)
                    ax.arrow(q1[0], q1[1], q2[0]-q1[0], q2[1]-q1[1], linewidth = lw,
                              head_width=0.05*lw/lw_max, head_length=s, alpha = alpha, 
                              fc=color_lst[j], ec=color_lst[j])
                    ax.text( q2[0], q2[1], '%i' % val, fontsize = num_fs, 
                             va = va, ha = ha)
    if rot:
        rotation = 90 - 180*np.abs(pp)/math.pi
        b = rotation < -90
        rotation[b] = 180+rotation[b]
    else:
        rotation = np.zeros(M)
        
    for j in range(pnts.shape[1]):
        (x, y) = (pnts[0,j], pnts[1,j])
        
        ha = 'center'
        if x < 0:
            ha = 'right'
        else: 
            ha = 'left'
        va = 'center'
        if y == 0:
            pass
        elif y < 0:
            va = 'top'
        else: 
            va = 'bottom'
            
        if j < M:
            ct = clst[j]
            a = (df.loc[ct, ct] != 0)*(Rs*2)
            rot = rotation[j]
            cc = color_lst[j]
        else:
            ct = ''
            a = 0
            rot = 0
            cc = 'gray'
            
        if ax is None: 
            plt.plot( x, y, 'o', ms = node_size, c = cc)
            plt.text( x, y, ' %s ' % ct, fontsize = text_fs, 
                      ha = ha, va = va, rotation = rot)
        else:
            ax.plot( x, y, 'o', ms = node_size, c = cc)
            ax.text( x*(1+a), y*(1+a), '  %s  ' % ct, fontsize = text_fs, 
                     ha = ha, va = va, rotation = rot)

    if ax is None: 
        plt.xticks([])
        plt.yticks([])
        plt.margins(x=margin, y=margin)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.margins(x=margin, y=margin)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False) 
        
    if title is not None: ax.set_title(title, fontsize = title_fs )
        
    if show: plt.show()
    return


def plot_cci_circ_group( df_dct, target = [], 
                         rename_cells = None, remove_common = False,
                         ncol = 3, figsize = (8,7), dpi = 100,
                         title = None, title_y_pos = 1, title_fs = 18, 
                         text_fs = 16, num_fs = 12, margin = 0.08, alpha = 0.5, 
                         linewidth_max = 10, linewidth_log = False,  
                         R_curvature = 3, node_size = 10, rot = False, 
                         cmap = 'Spectral', wspace = 0.35, hspace = 0.2 ):

    df_lst = get_cci_ni_mat( df_dct, remove_common )
    if isinstance(rename_cells, dict):
        for k in df_lst.keys():
            df_lst[k].rename(columns = rename_cells, index = rename_cells, inplace = True)

    if target is None:
        df_lst2 = df_lst
    elif not isinstance(target, list):
        print('ERROR: targte must be a list of celltypes.')
        return 
    elif len(target) == 0:
        df_lst2 = df_lst
    else:
        ## check if target exists in the data
        b = True
        for key in df_lst.keys():
            celltypes = df_lst[key].columns.values.tolist()
            b = len(list(set(target).intersection(celltypes))) == len(target)
            if not b: break

        if not b:
            s = ''
            for t in target:
                s = s + '%s,' % t
            s = s[:-1]
            print('ERROR: %s not exists in the data.' % s)
            return
        else:
            df_lst2 = {}
            for key in df_lst.keys():
                df = df_lst[key]
                msk = df.copy(deep = True)
                msk.loc[:,:] = 0
                msk.loc[target,:] = 1
                msk.loc[:,target] = 1
                df_lst2[key] = df*msk
   
    n_max = 0
    for k in df_lst2.keys():
        n_max = max( df_lst2[k].max().max(), n_max )
    linewidth_scale = linewidth_max/(n_max + 0.01)
    lw_max_dict = {}
    for k in df_lst2.keys():
        lw_max_dict[k] = df_lst2[k].max().max()*linewidth_scale
    
    cond_lst = list(df_lst2.keys())
    cond_lst.sort()
    ws_hs = [wspace, hspace]
    
    R = R_curvature
    N = 500
    nc = ncol
    nr = int(np.ceil(len(cond_lst)/nc))
    # nr, nc = 1, int(len(cond_lst))
    fig, axes = plt.subplots(figsize = (figsize[0]*nc,figsize[1]*nr), nrows=nr, ncols=nc, # constrained_layout=False, 
                             gridspec_kw={'width_ratios': [1]*nc}, dpi = dpi)
    fig.tight_layout() 
    plt.subplots_adjust(left=0.025, bottom=0.025, right=0.975, top=0.975, wspace=ws_hs[0], hspace=ws_hs[1])
    if title is not None: plt.suptitle(title, fontsize = title_fs, y = title_y_pos)

    cnt = 0
    for j, k in enumerate(cond_lst):

        df = df_lst2[k]*(df_lst2[k] > 0).copy(deep = True)
        if df.shape[0] > 0:
            cnt += 1
            plt.subplot(nr,nc,cnt)

            if nr == 1: ax = axes[int(j)]
            else: ax = axes[int(j/nc)][j%nc]

            plot_cci_circ( df, title = k, title_fs = text_fs + 2, 
                           text_fs = text_fs, num_fs = num_fs, margin = margin, alpha = alpha, 
                           R_curvature = R_curvature, 
                           linewidth_max = lw_max_dict[k], # linewidth_max, 
                           # linewidth_scale = 0, # linewidth_scale, 
                           linewidth_log = linewidth_log, 
                           node_size = node_size, rot = rot, cmap = cmap, 
                           ax = ax, show = False)

    if cnt < (nr*nc):
        for k in range(int(nr*nc - cnt)):
            j = k + cnt
            ax = plt.subplot(nr,nc,j+1)
            ax.axis('off')

    plt.show()
    return


def plot_cnv_250810( adata_in, groupby = 'ploidy_dec', N_cells_min = 20,
              title = 'log2(CNR)', title_fs = 14, title_y_pos = 1.1, 
              label_fs = 12, tick_fs = 12, figsize = (12, 6), swap_axes = False, 
              var_group_rotation = 45, cmap='RdBu_r', vmax = 1, spot_llst = None,
              cnv_obsm_key = 'X_cnv', cnv_uns_key = 'cnv', spot_resample = 100,
              xlabel = 'Genomic spot', xtick_rot = 0, xtick_ha = 'center', 
              show_ticks = True, alpha = 0.3 ):

    pcnt = adata_in.obs[groupby].value_counts()
    bp = pcnt >= N_cells_min
    b = adata_in.obs[groupby].isin(list(pcnt.index.values[bp]))
    adata = adata_in[b,:].copy()
    
    X_cnv = adata.obsm[cnv_obsm_key]
    chrs = np.array([' ']*X_cnv.shape[1])

    if isinstance(cnv_uns_key, str):
        
        '''
        # clst = adata.uns[cnv_uns_key]['spot_to_chr_map']        
        # df_chr = pd.DataFrame( {'chr': clst} )
        
        df_chr_pos = adata.uns[cnv_uns_key]['df_chr_pos']        
        vg_pos = []
        vg_labels = []
        for c in df_chr_pos.index:
            start = df_chr_pos.loc[c,'start']
            end = df_chr_pos.loc[c,'end']
            vg_pos.append((start+5, end-5))
            vg_labels.append(c)
        '''
        
        chr_pos = adata.uns[cnv_uns_key]['chr_pos']
        df_chr_pos = pd.DataFrame({'chr_pos': list(chr_pos.values()), 'chr': list(chr_pos.keys()) }, index = chr_pos.keys())
        df_chr_pos = df_chr_pos.sort_values('chr_pos')
        # display(df_chr_pos)
        
        ## Get chromosome name for each loci in X_cnv
        chrs = []
        for i in range(df_chr_pos.shape[0]):
            if i < (df_chr_pos.shape[0]-1):
                start = list(df_chr_pos.iloc[i])[0]
                end = list(df_chr_pos.iloc[i+1])[0]
            else:
                start = list(df_chr_pos.iloc[i])[0]
                end = X_cnv.shape[1]
        
            chrs = chrs + list([df_chr_pos.index.values[i]]*int(end-start))
        
        df_chr = pd.DataFrame({'chr': chrs})
        
        lst = list(df_chr_pos['chr']) # list(df_chr['chr'].unique())
    
        ## Get vg_pos & vg_labels
        cnt = 0
        vg_pos = []
        vg_labels = []
        for i in lst:
            b = df_chr['chr'] == i
            vg_pos.append((cnt+5, cnt+np.sum(b)-5))
            vg_labels.append(i)
            cnt += np.sum(b)
        
        ## Create AnnData for plot
        ad = anndata.AnnData(X = X_cnv, var = df_chr, obs = adata.obs)
    else:
        vg_pos = None
        vg_labels = None
        ad = anndata.AnnData(X = X_cnv, obs = adata.obs)
        
    ad.var['spot_no'] = np.arange(len(ad.var.index.values))
    ad.var['spot_no'] = ad.var['spot_no'].astype(str)
    ad.var.set_index('spot_no', inplace = True)
    
    X = np.abs(ad.to_df())
    vmax = X.quantile([0.99]).mean(axis = 1)*2

    ax_dict = sc.pl.heatmap(ad, var_names = ad.var.index.values, groupby = groupby, 
                            show = False, figsize = figsize, swap_axes = swap_axes, 
                            var_group_positions = vg_pos, var_group_labels = vg_labels, 
                            var_group_rotation = var_group_rotation, 
                            cmap=cmap, vmax = vmax, vmin = -vmax, show_gene_labels = show_ticks)

    if spot_llst is not None:
        if isinstance(spot_llst, list):
            nlst = []
            for lst in spot_llst:
                s = '%i ~ %i' % (lst[0], lst[-1])
                nlst.append( s )
            slst = spot_llst
        else:
            nlst = list(spot_llst.keys())
            slst = list(spot_llst.values())
                
    ax_dict['heatmap_ax'].set_title(title, fontsize = title_fs, y = title_y_pos)
    if swap_axes:
        xtick_ha = 'right'
        
        if 'groupby_ax' in list(ax_dict.keys()):
            ax_dict['groupby_ax'].set_xlabel(groupby, fontsize = label_fs)
            ticks = ax_dict['groupby_ax'].get_xticklabels()
            ax_dict['groupby_ax'].set_xticklabels(ticks, fontsize = tick_fs)
        
        if xlabel is not None:
            ax_dict['heatmap_ax'].set_ylabel(xlabel, fontsize = label_fs)

        x_ticks = np.arange(0, len(ad.var.index.values), spot_resample)
        ax_dict['heatmap_ax'].set_yticks(x_ticks, x_ticks, rotation=xtick_rot, ha=xtick_ha, fontsize = tick_fs)

        if spot_llst is not None:
            for name, lst in zip (nlst, slst):
                L = ad.obs.shape[0]
                ax_dict['heatmap_ax'].add_patch(Rectangle((0, lst[0]), L, lst[-1]-lst[0], fill = True, 
                                                           edgecolor = 'gold', facecolor = 'gold', 
                                                           lw = 0.5, alpha = alpha))
                ax_dict['heatmap_ax'].text(int(L*0.01), lst[0], name, fontsize = tick_fs, 
                                           rotation = 0, va = 'center', ha = 'left')    
        pass
    else:
        if 'groupby_ax' in list(ax_dict.keys()):
            ax_dict['groupby_ax'].set_ylabel(groupby, fontsize = label_fs)
            ticks = ax_dict['groupby_ax'].get_yticklabels()
            ax_dict['groupby_ax'].set_yticklabels(ticks, fontsize = tick_fs)
        
        if xlabel is not None:
            ax_dict['heatmap_ax'].set_xlabel(xlabel, fontsize = label_fs)

        x_ticks = np.arange(0, len(ad.var.index.values), spot_resample)
        ax_dict['heatmap_ax'].set_xticks(x_ticks, x_ticks, rotation=xtick_rot, ha=xtick_ha, fontsize = tick_fs)

        if spot_llst is not None:
            for name, lst in zip (nlst, slst):
                L = ad.obs.shape[0]
                ax_dict['heatmap_ax'].add_patch(Rectangle((lst[0], -0.5), lst[-1]-lst[0], L, fill = True, 
                                                           edgecolor = 'gold', facecolor = 'gold', 
                                                           lw = 0.5, alpha = 0.3))
                ax_dict['heatmap_ax'].text(lst[0], int(L*0.01)-0.4, name, fontsize = tick_fs, 
                                           rotation = -90, va = 'top', ha = 'left')        
    
    # plt.show()
    return ax_dict


def plot_cnv( adata_in, groupby = 'ploidy_dec', N_cells_min = 50, N_cells_max = 0,
              title = 'log2(CNR)', title_fs = 14, title_y_pos = 1.1, show_cna_spots = False,
              label_fs = 12, tick_fs = 12, figsize = (12, 6), swap_axes = False, 
              var_group_rotation = 45, cmap='RdBu_r', vmax = 1, spot_llst = None,
              cnv_obsm_key = 'X_cnv', cnv_uns_key = 'cnv', spot_resample = 100,
              xlabel = 'Genomic spot', xtick_rot = 0, xtick_ha = 'center', 
              show_ticks = True, alpha = 0.3, Ns_min = 0.5 ):

    if groupby not in list( adata_in.obs.columns.values ):
        print('ERROR: %s not in the obs.columns. ' % groupby )
        return None, None
    else:
        pcnt = adata_in.obs[groupby].value_counts()    
        if (N_cells_max > 0) & (N_cells_max < 1):
            N_cells_max = int(pcnt.quantile(N_cells_max))
            if (N_cells_min > 0) & (N_cells_min < 1): 
                N_cells_min = int(N_cells_max*N_cells_min)
            print('N_cells_max: %i, %i (%i, %i) ' % (N_cells_max, N_cells_min, pcnt[0], pcnt[-1]))

        bp = pcnt >= N_cells_min
        b = adata_in.obs[groupby].isin(list(pcnt.index.values[bp]))
        adata = adata_in[b,:] #.copy()
        
        if N_cells_max > 0:
            ## Resample cells to balance cell counts across samples 
            slst = adata.obs[groupby].unique()
            idx_all = adata.obs.index.values
            idx_sel = []
            for s in slst:
                b = adata.obs[groupby] == s
                
                if np.sum(b) <= N_cells_max:
                    idx_sel = idx_sel + list(idx_all[b])
                else:
                    idx_sel = idx_sel + random.sample(list(idx_all[b]), N_cells_max)
            
            adata = adata_in[idx_sel,:]


    if spot_llst is None:
        if show_cna_spots:                
            results = find_signif_CNV_gain_regions( adata, 
                                                    N_cells_min = N_cells_min, N_cells_max = N_cells_max,
                                                    std_scale = 0.5, gmm_ncomp_t = 3, gmm_ncomp_n = 1, 
                                                    n_samples_min = Ns_min, N_spots_min = 10 )
            spot_llst = results['spots']
            
            
    X_cnv = adata.obsm[cnv_obsm_key]
    chrs = np.array([' ']*X_cnv.shape[1])

    if isinstance(cnv_uns_key, str):
        
        chr_pos = adata.uns[cnv_uns_key]['chr_pos']
        df_chr_pos = pd.DataFrame({'chr_pos': list(chr_pos.values()), 'chr': list(chr_pos.keys()) }, index = chr_pos.keys())
        df_chr_pos = df_chr_pos.sort_values('chr_pos')
        
        ## Get chromosome name for each loci in X_cnv
        chrs = []
        for i in range(df_chr_pos.shape[0]):
            if i < (df_chr_pos.shape[0]-1):
                start = list(df_chr_pos.iloc[i])[0]
                end = list(df_chr_pos.iloc[i+1])[0]
            else:
                start = list(df_chr_pos.iloc[i])[0]
                end = X_cnv.shape[1]
        
            chrs = chrs + list([df_chr_pos.index.values[i]]*int(end-start))
        
        df_chr = pd.DataFrame({'chr': chrs})
        
        lst = list(df_chr_pos.index.values) # list(adata.uns[cnv_uns_key]['df_chr_pos'].index.values)
        
        ## Get vg_pos & vg_labels
        cnt = 0
        vg_pos = []
        vg_labels = []
        for i in lst:
            b = df_chr['chr'] == i
            vg_pos.append((cnt+5, cnt+np.sum(b)-5))
            vg_labels.append(i)
            cnt += np.sum(b)
        
        ## Create AnnData for plot
        ad = anndata.AnnData(X = X_cnv, var = df_chr, obs = adata.obs)
    else:
        vg_pos = None
        vg_labels = None
        ad = anndata.AnnData(X = X_cnv, obs = adata.obs)

        
    ad.var['spot_no'] = np.arange(len(ad.var.index.values))
    ad.var['spot_no'] = ad.var['spot_no'].astype(str)
    ad.var.set_index('spot_no', inplace = True)
    
    if isinstance( ad.X, np.ndarray ):
        vmax = np.quantile( np.abs(ad.X), 0.99).mean()*2
    else:
        vmax = np.quantile( np.abs(ad.X.data), 0.995 )

    ax_dict = sc.pl.heatmap(ad, var_names = ad.var.index.values, groupby = groupby, 
                            show = False, figsize = figsize, swap_axes = swap_axes, 
                            var_group_positions = vg_pos, var_group_labels = vg_labels, 
                            var_group_rotation = var_group_rotation, 
                            cmap=cmap, vmax = vmax, vmin = -vmax, show_gene_labels = show_ticks)

    if spot_llst is not None:
        if isinstance(spot_llst, list):
            nlst = []
            for lst in spot_llst:
                s = '%i ~ %i' % (lst[0], lst[-1])
                nlst.append( s )
            slst = spot_llst
        else:
            nlst = list(spot_llst.keys())
            slst = list(spot_llst.values())
                
    ax_dict['heatmap_ax'].set_title(title, fontsize = title_fs, y = title_y_pos)
    if swap_axes:
        xtick_ha = 'right'
        
        if 'groupby_ax' in list(ax_dict.keys()):
            ax_dict['groupby_ax'].set_xlabel(groupby, fontsize = label_fs)
            ticks = ax_dict['groupby_ax'].get_xticklabels()
            ax_dict['groupby_ax'].set_xticklabels(ticks, fontsize = tick_fs)
        
        if xlabel is not None:
            ax_dict['heatmap_ax'].set_ylabel(xlabel, fontsize = label_fs)

        x_ticks = np.arange(0, len(ad.var.index.values), spot_resample)
        ax_dict['heatmap_ax'].set_yticks(x_ticks, x_ticks, rotation=xtick_rot, ha=xtick_ha, fontsize = tick_fs)

        if spot_llst is not None:
            for name, lst in zip (nlst, slst):
                L = ad.obs.shape[0]
                ax_dict['heatmap_ax'].add_patch(Rectangle((0, lst[0]), L, lst[-1]-lst[0], fill = True, 
                                                           edgecolor = 'gold', facecolor = 'gold', 
                                                           lw = 0.5, alpha = alpha))
                ax_dict['heatmap_ax'].text(int(L*0.01), lst[0], name, fontsize = tick_fs, 
                                           rotation = 0, va = 'center', ha = 'left')    
        pass
    else:
        if 'groupby_ax' in list(ax_dict.keys()):
            ax_dict['groupby_ax'].set_ylabel(groupby, fontsize = label_fs)
            ticks = ax_dict['groupby_ax'].get_yticklabels()
            ax_dict['groupby_ax'].set_yticklabels(ticks, fontsize = tick_fs)
        
        if xlabel is not None:
            ax_dict['heatmap_ax'].set_xlabel(xlabel, fontsize = label_fs)

        x_ticks = np.arange(0, len(ad.var.index.values), spot_resample)
        ax_dict['heatmap_ax'].set_xticks(x_ticks, x_ticks, rotation=xtick_rot, ha=xtick_ha, fontsize = tick_fs)

        if spot_llst is not None:
            for name, lst in zip (nlst, slst):
                L = ad.obs.shape[0]
                ax_dict['heatmap_ax'].add_patch(Rectangle((lst[0], -0.5), lst[-1]-lst[0], L, fill = True, 
                                                           edgecolor = 'gold', facecolor = 'gold', 
                                                           lw = 0.5, alpha = 0.3))
                ax_dict['heatmap_ax'].text(lst[0], int(L*0.01)-0.4, name, fontsize = tick_fs, 
                                           rotation = -90, va = 'top', ha = 'left')        

    if show_cna_spots:
        return ax_dict, results
    else:
        return ax_dict, None


def get_normal_pdf( x, mu, var, nbins):
    
    MIN_ABS_VALUE = 1e-8
    y = np.array(x)
    mn_x = y.min()
    mx_x = y.max()
    dx = mx_x - mn_x
    mn_x -= dx/4
    mx_x += dx/4
    L = 100
    # dx = len(y)*(mx_x-mn_x)/L
    dx = (mx_x-mn_x)/nbins
    xs = np.arange(mn_x,mx_x, dx )
    pdf = (dx*len(y))*np.exp(-((xs-mu)**2)/(2*var+MIN_ABS_VALUE))/(np.sqrt(2*math.pi*var)+MIN_ABS_VALUE) + MIN_ABS_VALUE
    return pdf, xs


def plot_td_stats( params, n_bins = 30, title = None, title_fs = 14,
                   label_fs = 12, tick_fs = 11, legend_fs = 11, 
                   legend_loc = 'upper left', bbox_to_anchor = (1, 1),
                   figsize = (4,3), log = True, alpha = 0.8 ):
    
    th = params['th']
    m0 = params['m0']
    v0 = params['v0']
    w0 = params['w0']
    m1 = params['m1']
    v1 = params['v1']
    w1 = params['w1']
    df = params['df']
        
    mxv = df['cmean'].max()
    mnv = df['cmean'].min()
    Dv = mxv - mnv
    dv = Dv/200

    x = np.arange(mnv,mxv,dv)
    pdf0, xs0 = get_normal_pdf( x, m0, v0, 100)
    pdf1, xs1 = get_normal_pdf( x, m1, v1, 100)
    
    pr = pdf1/(pdf1 + pdf0) # get_malignancy_prob( xs0, [w0, m0, v0, w1, m1, v1] )
    bx = (xs0 >= m0) & ((xs1 <= m1))

    nn = len(df['cmean'])
    pdf0 = pdf0*(w0*nn*(200/n_bins)/pdf0.sum())
    pdf1 = pdf1*(w1*nn*(200/n_bins)/(pdf1.sum())) 

    max_pdf = max(pdf0.max(), pdf1.max())
    
    plt.figure(figsize = figsize)
    ax = plt.gca()
    
    counts, bins = np.histogram(df['cmean'], bins = n_bins)
    # max_cnt = np.max(counts)

    legend_labels = []
    
    max_cnt = 0
    b = df['tumor_dec'] == 'Normal'
    if np.sum(b) > 0:
        legend_labels.append('Normal')
        counts, bins_t, bar_t = plt.hist(df.loc[b, 'cmean'], bins = bins, alpha = alpha)
        max_cnt = max(max_cnt, np.max(counts))
    b = df['tumor_dec'] == 'Tumor'
    if np.sum(b) > 0:
        legend_labels.append('Tumor')
        counts, bins_t, bar_t = plt.hist(df.loc[b, 'cmean'], bins = bins, alpha = alpha)
        max_cnt = max(max_cnt, np.max(counts))
    b = df['tumor_dec'] == 'unclear'
    if np.sum(b) > 0:
        legend_labels.append('unclear')
        counts, bins_t, bar_t = plt.hist(df.loc[b, 'cmean'], bins = bins, alpha = alpha)
        max_cnt = max(max_cnt, np.max(counts))
    
    sf = 0.9*max_cnt/max_pdf
    plt.plot(xs0, pdf0*sf)
    plt.plot(xs1, pdf1*sf)
    plt.plot([th, th], [0, max_cnt]) # max(pdf0.max()*sf, pdf1.max()*sf)])
    plt.plot(xs0[bx], pr[bx]*max_cnt)

    if title is not None: plt.title(title, fontsize = title_fs)
    plt.xlabel('CNV_score', fontsize = label_fs)
    plt.ylabel('Number of clusters', fontsize = label_fs)
    plt.legend(['Normal distr.', 'Tumor distr.', 'Threshold', 'Tumor Prob.'], #, 'Score hist.'], 
               loc = legend_loc, bbox_to_anchor = bbox_to_anchor, fontsize = legend_fs)
    if log: plt.yscale('log')
    ax.tick_params(axis='x', labelsize=tick_fs)
    ax.tick_params(axis='y', labelsize=tick_fs)
    plt.grid()
    plt.show()
        
    return 
    
### Plot dot

def remove_common( mkr_dict, prn = True ):

    cts = list(mkr_dict.keys())
    mkrs_all = []
    for c in cts:
        mkrs_all = mkrs_all + list(mkr_dict[c])
    mkrs_all = list(set(mkrs_all))
    df = pd.DataFrame(index = mkrs_all, columns = cts)
    df.loc[:,:] = 0

    for c in cts:
        df.loc[mkr_dict[c], c] = 1
    Sum = df.sum(axis = 1)
    
    to_del = []
    s = ''
    for c in cts:
        b = (df[c] > 0) & (Sum == 1)
        mkrs1 = list(df.index.values[b])
        if prn & (len(mkr_dict[c]) != len(mkrs1)):
            s = s + '%s: %i > %i, ' % (c, len(mkr_dict[c]), len(mkrs1))
        
        if len(mkrs1) == 0:
            to_del.append(c)
        else:
            mkr_dict[c] = mkrs1

    if prn & len(s) > 0:
        print(s[:-2])

    if len(to_del) > 0:
        for c in cts:
            if c in to_del:
                del mkr_dict[c]
                
    return mkr_dict


def get_markers_all4(mkr_file, target_lst, genes = None, 
                    rem_cmn = False ):
    
    # target = 'Myeloid cell'
    if isinstance(mkr_file, dict):
        mkr_dict = mkr_file
    else:
        print('ERROR: marker input must be a dictionary.')
        return None
    
    if target_lst is not None:
        if len(target_lst) > 0:
            mkr_dict_new = {}
            for c in target_lst:
                if c in list(mkr_dict.keys()):
                    mkr_dict_new[c] = mkr_dict[c]
            mkr_dict = mkr_dict_new
            
    if rem_cmn:
        mkr_dict = remove_common( mkr_dict, prn = True )
        
    mkrs_all = [] #['SELL']
    mkrs_cmn = []
    for ct in mkr_dict.keys():
        if genes is not None:
            ms = list(set(mkr_dict[ct]).intersection(genes))
        else: 
            ms = mkr_dict[ct]
        mkrs_all = mkrs_all + ms
        if len(mkrs_cmn) == 0:
            mkrs_cmn = ms
        else:
            mkrs_cmn = list(set(mkrs_cmn).intersection(ms))

    mkrs_all = list(set(mkrs_all))
    if genes is not None:
        mkrs_all = list(set(mkrs_all).intersection(genes))
    
    return mkrs_all, mkr_dict


def remove_mac_common_markers(mkrs_dict):   

    lst2 = list(mkrs_dict.keys())
    lst = []
    Mono = None
    for item in lst2:
        if item[:3] == 'Mac':
            lst.append(item)
        if item[:4] == 'Mono':
            Mono = item
            
    if len(lst) > 1:
        mac_common = mkrs_dict[lst[0]]
        for item in lst[1:]:
            mac_common = list(set(mac_common).intersection(mkrs_dict[item]))
            
        for item in lst:
            for mkr in mac_common:
                mkrs_dict[item].remove(mkr)
#         if Mono is not None:
#             mono_lst = mkrs_dict[Mono]
#             del mkrs_dict[Mono]
#             mkrs_dict[Mono] = mono_lst
            
    return mkrs_dict

    
def update_markers_dict2(mkrs_all, mkr_dict, X, y, rend = None, cutoff = 0.3, 
                        Nall = 20, Npt = 20, Npt_tot = 0):
    
    if rend is None:
        lst = list(mkr_dict.keys())
        lst.sort()
        rend = dict(zip(lst, lst))
    else:
        lst = list(rend.keys())
        
    df = pd.DataFrame(index = lst, columns = mkrs_all)
    df.loc[:,:] = 0
        
    for ct in lst:
        if ct in list(mkr_dict.keys()):
            b = y == ct
            ms = list(set(mkr_dict[ct]).intersection(mkrs_all))
            pe = list((X.loc[b,ms] > 0).mean(axis = 0))
            for j, m in enumerate(ms):
                df.loc[ct, m] = pe[j]

    if df.shape[0] == 1:
        mkrs_all = list(df.columns.values)
        mkrs_dict = {}
        
        pe_lst = []
        pex_lst = []
        
        for ct in lst:
            b = y == ct
            ms = list(set(mkr_dict[ct]).intersection(mkrs_all))
            pe = np.array((X.loc[b,ms] > 0).mean(axis = 0))
            pex = np.array((X.loc[~b,ms] > 0).mean(axis = 0))
            odr = np.array(-pe).argsort()
            ms_new = []
            for o in odr:
                if (pe[o] >= cutoff):
                    ms_new.append(ms[o])

            pe = pe[~np.isnan(pe)]
            pex = pex[~np.isnan(pex)]
            pe_lst = pe_lst + list(pe)
            pex_lst = pex_lst + list(pex)
            
            if len(ms_new) > 0:
                mkrs_dict[rend[ct]] = ms_new[:min(Npt,len(ms_new))]
            else:
                mkrs_dict[rend[ct]] = ms[:min(Npt,len(ms))]
                
        mkrs_dict2 = mkrs_dict
    else:
        p1 = df.max(axis = 0)
        p2 = p1.copy(deep = True)
        p2[:] = 0
        idx = df.index.values
        # print(df)
        for m in list(df.columns.values):
            odr = np.array(-df[m]).argsort()
            p2[m] = df.loc[idx[odr[1]], m]
        nn = (df >= 0.5).sum(axis = 0)

        b0 = p1 > 0
        b1 = (p2/(p1 + 0.0001)) < 0.5
        b2 = nn < 4
        b = b0 # & b1 & b2
        df = df.loc[:,b]
        mkrs_all = list(df.columns.values)

        mkrs = [] 
        cts = [] 
        pes = [] 
        mkrs_dict = {}
        pe_dict = {}
        pex_dict = {}
        # mkrs_all = [] 
        for ct in lst:
            b = y == ct
            if ct in list(mkr_dict.keys()):
                ms = list(set(mkr_dict[ct]).intersection(mkrs_all))
                p2t = np.array(p2[ms])
                p1t = np.array(p1[ms])
                pe = np.array((X.loc[b,ms] > 0).mean(axis = 0))
                pex = np.array((X.loc[~b,ms] > 0).mean(axis = 0))
                odr = np.array(-pe).argsort()
                ms_new = []
                pe_new = []
                pex_new = []
                for o in odr:
                    if (pe[o] >= cutoff) & (~np.isnan(pe[o])):
                        ms_new.append(ms[o])

                        pe_new.append(pe[o])
                        pex_new.append(pex[o])
                '''
                pe = pe[~np.isnan(pe)]
                pex = pex[~np.isnan(pex)]
                pe_lst = pe_lst + list(pe)
                pex_lst = pex_lst + list(pex)
                '''

                if len(ms_new) > 0:
                    mkrs_dict[rend[ct]] = ms_new[:min(Npt,len(ms_new))]
                    pe_dict[rend[ct]] = pe_new[:min(Npt,len(ms_new))]
                    pex_dict[rend[ct]] = pex_new[:min(Npt,len(ms_new))]
                else:
                    mkrs_dict[rend[ct]] = ms[:min(Npt,len(ms))]
                    pe_dict[rend[ct]] = list(pe)[:min(Npt,len(ms))]
                    pex_dict[rend[ct]] = list(pex)[:min(Npt,len(ms))]
             
        mkr_lst = []
        pe_lst = []
        pex_lst = []
        cnt2 = 0
        for ct in lst:
            if ct in list(mkr_dict.keys()):
                pe_lst = pe_lst + pe_dict[rend[ct]]
                pex_lst = pex_lst + pex_dict[rend[ct]]
                mkr_lst = mkr_lst + mkrs_dict[rend[ct]]
                cnt2 += len(mkrs_dict[rend[ct]])
            
        if (Npt_tot is not None) & (Npt_tot > 20) & (len(pe_lst) > 0):
            odr = (np.array(pe_lst)).argsort()
            if len(odr) > Npt_tot:
                pe_th = pe_lst[odr[int(len(odr)-Npt_tot)]]
            else:
                pe_th = pe_lst[odr[0]]

            pe_lst = []
            pex_lst = []
            cnt = 0
            for ct in lst:
                if ct in list(mkr_dict.keys()):
                    pe = np.array(pe_dict[rend[ct]]) 
                    b = pe >= pe_th
                    mkrs_dict[rend[ct]] = list(np.array(mkrs_dict[rend[ct]])[b])
                    cnt += len(mkrs_dict[rend[ct]])
                    pe_lst = pe_lst + list(np.array(pe_dict[rend[ct]])[b])
                    pex_lst = pex_lst + list(np.array(pex_dict[rend[ct]])[b])
                
            print('Num markers selected: %i -> %i' % (cnt2, cnt))
            
        mkrs_dict2 = {}
        for m in mkr_dict.keys():
            if (rend is not None) & (m in rend.keys()):
                m = rend[m]                
            if m in list(mkrs_dict.keys()):
                mkrs_dict2[m] = mkrs_dict[m]
            
    return mkrs_dict2, df, pe_lst, pex_lst                                


def get_best_markers(adata, markers_in = None, var_group_col = None, 
                    nz_frac_cutoff = 0.1, 
                    rem_mkrs_common_in_N_groups_or_more = 3, N_cells_min = 20,  
                    N_markers_per_group_max = 15, N_markers_total = 200 ): 

    Npt = N_markers_per_group_max
    Npt_tot = N_markers_total
    show_unassigned = False
    # show = True
    rend = None    
    other_genes = []

    if markers_in is None:
        markers = copy.deepcopy( adata.uns['Celltype_marker_DB']['subset_markers_dict'] )
        var_group_col = 'celltype_subset'
    else:
        markers = copy.deepcopy(markers_in)

    target_lst = list(markers.keys()) 
    target_lst.sort()

    target = ','.join(target_lst)
    genes = list(adata.var.index.values)
    
    mkrs_all, mkr_dict = get_markers_all4(markers, target_lst, 
                                         genes, rem_cmn = False)
    
    target_lst2 = list(mkr_dict.keys())
    y = adata.obs[var_group_col]
    
    if show_unassigned:
        if np.sum(y.isin(['unassigned'])) > 10:
            mkr_dict['unassigned'] = []
            target_lst2 = list(mkr_dict.keys())

    b = y.isin(target_lst2)
    adata_t = adata[b, list(set(mkrs_all).union(other_genes))].copy()
    X = adata_t.to_df()
    y = adata_t.obs[var_group_col]

    mkrs_dict, df, pe_lst, pex_lst = update_markers_dict2(mkrs_all, mkr_dict, X, y, rend, 
                                        cutoff = 0, Npt = Npt*2, Npt_tot = 0)
    
    mkrs_dict = remove_mac_common_markers(mkrs_dict)
    if rend is not None: 
        adata_t.obs[var_group_col] = adata_t.obs[var_group_col].replace(rend)
        
    ## Get number of marker genes for each cell type
    mkall = []
    for key in mkrs_dict.keys():
        mkall = mkall + mkrs_dict[key]
    mkall = list(set(mkall))
    nmkr = dict(zip(mkall, [0]*len(mkall)))
    for key in mkrs_dict.keys():
        for m in mkrs_dict[key]:
            nmkr[m] += 1
            
    ## remove the marker genes appering in 3 or more cell types
    if rem_mkrs_common_in_N_groups_or_more > 0:
        to_del = []
        for key in nmkr.keys():
            if nmkr[key] >= rem_mkrs_common_in_N_groups_or_more: 
                to_del.append(key)

        if len(to_del) > 0:
            for m in to_del:
                for key in mkrs_dict.keys():
                    if m in mkrs_dict[key]:
                        mkrs_dict[key].remove(m)
                        
    ## Select only the cell types that exist in the data and the number of cells >= N_cells_min
    #'''
    ps_cnt = adata_t.obs[var_group_col].value_counts()
    lst_prac = list(ps_cnt.index.values) 
    mkrs_dict2 = {}
    for m in mkrs_dict.keys():
        if m in lst_prac: 
            if ps_cnt[m] >= N_cells_min:
                mkrs_dict2[m] = mkrs_dict[m]
    mkrs_dict = mkrs_dict2        
    #'''
    
    ## Remove cell types for which the number of cells below N_cells_min
    target_lst2 = list(mkrs_dict.keys())
    y = adata_t.obs[var_group_col]
    
    if show_unassigned:
        if np.sum(y.isin(['unassigned'])) > 10:
            mkrs_dict['unassigned'] = []
            target_lst2 = list(mkrs_dict.keys())
    
    if len(target_lst2) == 0:
        return None, None

    #'''
    b = y.isin(target_lst2)
    adata_t = adata_t[b, :]
    if rend is not None: 
        adata_t.obs[var_group_col] = adata_t.obs[var_group_col].replace(rend)
    
    X = adata_t.to_df()
    y = adata_t.obs[var_group_col]
    
    ## Get number of marker genes for each cell type
    mkrs_all = []
    for key in mkrs_dict.keys():
        mkrs_all = mkrs_all + mkrs_dict[key]
    mkrs_all = list(set(mkrs_all))
    
    mkrs_dict, df, pe_lst, pex_lst = update_markers_dict2(mkrs_all, mkrs_dict, X, y, None, 
                                        cutoff = nz_frac_cutoff, Npt = Npt, Npt_tot = Npt_tot)

    lst = list(mkrs_dict.keys())
    for k in lst:
        if len(mkrs_dict[k]) == 0:
            del mkrs_dict[k]
                
    #'''
    if markers_in is None:
        adata_t.obs[var_group_col] = adata_t.obs[var_group_col].astype(str)
        b = adata_t.obs[var_group_col].isin(list(mkrs_dict.keys()))
        adata_t = adata_t[b,:]
    #'''
    return mkrs_dict, adata_t, var_group_col
                                

def plot_marker_exp_inner(adata, markers, var_group_col = 'celltype_subset', 
                    cell_group_col = None, # group_categ_col = None,
                    title = None, title_y_pos = 1.1, title_fs = 14, 
                    text_fs = 12, linewidth = 1.5, 
                    var_group_height = 1.2, var_group_rotation = 0, standard_scale = 'var', 
                    nz_frac_max = 0.5, # nz_frac_cutoff = 0.1, 
                    # rem_mkrs_common_in_N_groups_or_more = 3, N_cells_min = 20,  
                    # N_markers_per_group_max = 15, N_markers_total = 200, 
                    mean_only_expressed = False, 
                    figsize = (20, 4), swap_ax = False, legend = False, add_rect = True,
                    cmap = 'Reds', rect_color = 'royalblue'):

    group_categ_col = var_group_col
    group_col = cell_group_col
    mkrs_dict = markers
    # Npt = N_markers_per_group_max
    # Npt_tot = N_markers_total
    # show_unassigned = False
    show = True
    # rend = None    
    # other_genes = []
    # target_lst = list(markers.keys()) 
    # target_lst.sort()
    
    Lw = linewidth
    hgt = var_group_height
    title_fontsize = title_fs
    
    SCANPY = True
    try:
        import scanpy as sc
    except ImportError:
        SCANPY = False
    
    if (not SCANPY):
        print('ERROR: scanpy not installed. ')   
        return
    
    # target = ','.join(target_lst)
    # genes = list(adata.var.index.values)
        
    mkrs_all = []
    for key in mkrs_dict.keys():
        mkrs_all = mkrs_all + mkrs_dict[key]
    # mkrs_all = list(set(mkrs_all))
    
    adata_t = adata[:, list(set(mkrs_all))]

    sx = len(mkrs_all)
    if group_col is None:
        sy = len(adata_t.obs[var_group_col].unique().tolist())
    else:
        sy = len(adata_t.obs[group_col].unique().tolist())

    if swap_ax or (markers is None):
        figsize = None        
    else:
        if figsize is None:
            figsize = (sx/3.2, 4)
            
        if swap_ax:
            lx = figsize[1]
            ly = figsize[0]
        
            ly = lx*sy/sx
            figsize = (ly, lx)
            title_y_pos = (sx + title_y_pos)/sx
        else:
            lx = figsize[0]
            ly = figsize[1]
        
            ly = lx*sy/sx
            figsize = (lx, ly)
            title_y_pos = (sy + title_y_pos)/sy
    
    if show:
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if group_col is None:
                Type_level = var_group_col
                categ_order = list(mkrs_dict.keys())
                # categ_order.sort()
            else:
                #'''
                var_group_lst = list(mkrs_dict.keys())
                var_group_lst.sort()
                mkrs_dict2 = {}
                for c in var_group_lst:
                    mkrs_dict2[c] = mkrs_dict[c]
                mkrs_dict = mkrs_dict2    
                #'''
                Type_level = group_col
                if group_categ_col is None:
                    categ_order = list(adata_t.obs[Type_level].unique())
                    categ_order.sort()
                else:
                    group_categ_lst = list(adata_t.obs[group_categ_col].unique())
                    group_categ_lst.sort()
                    categ_order = []
                    num_groups_per_group_categ = {}
                    for gc in group_categ_lst:
                        b = adata_t.obs[group_categ_col] == gc
                        lst_tmp = list(adata_t[b,:].obs[Type_level].unique())
                        lst_tmp.sort()

                        # print((gc, np.array(var_group_lst)))
                        if gc in var_group_lst:
                            genes = mkrs_dict[gc]
                        else:
                            genes = mkrs_all
                        Xx = (adata_t[b, genes].to_df() > 0)
                        Xx['group'] = adata_t[b,:].obs[Type_level]                            
                        X = Xx.groupby('group').mean()
                        # display(X)
                        # linked = linkage(X, 'single')
                        # idx_odrd = leaves_list(linked)
                        # lst_tmp = list( np.array(lst_tmp)[idx_odrd][::-1] )
                        X['mean'] = X.mean(axis = 1)
                        lst_tmp = X.sort_values(by = 'mean', ascending = False).index.values.tolist()

                        categ_order = categ_order + lst_tmp
                        num_groups_per_group_categ[gc] = len(lst_tmp)

            # print(categ_order)
            dp = sc.pl.dotplot(adata_t, mkrs_dict, groupby = Type_level, 
                               categories_order = categ_order, 
                               return_fig = True, log = True, figsize = figsize,
                               var_group_rotation = var_group_rotation, show = False, # 
                               standard_scale = standard_scale, cmap = cmap, 
                               mean_only_expressed = mean_only_expressed,
                               dot_max = nz_frac_max, swap_axes = swap_ax )
                               # colorbar_title = 'mean expression', size_title = 'percent cells' ) 
            dp.add_totals() # .style(dot_edge_color='black', dot_edge_lw=0.5).show()
        

        ax_dict = dp.get_axes()    
        ax = ax_dict['mainplot_ax']
        
        if title is not None:
            ax.set_title(title, fontsize = title_fontsize, y = title_y_pos) 
        ax.tick_params(labelsize=text_fs)
        
        ## add Rectangles in main plot
        ylabels = []
        for j, key in enumerate(mkrs_dict.keys()):
            ylabels = ylabels + mkrs_dict[key]
        
        if add_rect:
            if group_col is None: 
                cnt = 0
                ylabels = []
                bar_length = 80
                for j, key in enumerate(mkrs_dict.keys()):
                    L = len(mkrs_dict[key])
                    if swap_ax:
                        ax.add_patch(Rectangle((j, cnt), 1, L, fill = False, edgecolor = rect_color, lw = Lw))
                    else:
                        ax.add_patch(Rectangle((cnt, j), L, 1, fill = False, edgecolor = rect_color, lw = Lw))
                    cnt += L
                    ylabels = ylabels + mkrs_dict[key]
    
                if categ_order is not None:
                    jj = j
                    L_tot = cnt        
                    outer_loops = int(len(categ_order)/len(list(mkrs_dict.keys())))
                    for kk in range(outer_loops-1):
                        cnt = 0
                        for j1, key in enumerate(mkrs_dict.keys()):
                            j = j + 1
                            L = len(mkrs_dict[key])
                            if swap_ax:
                                ax.add_patch(Rectangle((j, cnt), 1, L, fill = False, 
                                                       edgecolor = rect_color, lw = Lw))
                            else:
                                ax.add_patch(Rectangle((cnt, j), L, 1, fill = False, 
                                                       edgecolor = rect_color, lw = Lw))
                            cnt += L
            elif group_categ_col is not None:
                #'''
                cnt_x = 0
                cnt_y = 0
                # ylabels = []
                vg_lst = list(mkrs_dict.keys())
                if set(group_categ_lst).issubset(set(vg_lst)) | set(vg_lst).issubset(set(group_categ_lst)):
                    if set(group_categ_lst).issubset(set(vg_lst)):
                        super_list =vg_lst
                    else:
                        super_list =group_categ_lst
                    for gc in super_list: 
                        if gc in vg_lst:
                            L_x = len(mkrs_dict[gc])
                        else:
                            L_x = 0
                        if gc in group_categ_lst:
                            L_y = num_groups_per_group_categ[gc]
                        else:
                            L_y = 0
                        if swap_ax:
                            ax.add_patch(Rectangle((cnt_y, cnt_x), L_y, L_x, fill = False, edgecolor = rect_color, lw = Lw))
                        else:
                            ax.add_patch(Rectangle((cnt_x, cnt_y), L_x, L_y, fill = False, edgecolor = rect_color, lw = Lw))
                        cnt_x += L_x
                        cnt_y += L_y
                        # ylabels = ylabels + mkrs_dict[key]
                else:
                    cnt = 0
                    width = len(mkrs_all)
                    for gc in (group_categ_lst[:-1]): 
                        cnt += num_groups_per_group_categ[gc]
                        if swap_ax:
                            ax.plot([cnt, cnt], [0, width], rect_color, lw = Lw)
                        else:
                            ax.plot([0, width], [cnt, cnt], rect_color, lw = Lw)
    
                    cnt = 0
                    height = len(categ_order)
                    vg_lst = list(mkrs_dict.keys())
                    for vg in vg_lst[:-1]: 
                        cnt += len(mkrs_dict[vg])
                        if swap_ax:
                            ax.plot([0, height], [cnt, cnt], rect_color, lw = Lw)
                        else:
                            ax.plot([cnt, cnt], [0, height], rect_color, lw = Lw)
                                
        ## color/dot size legend 
        ax2 = ax_dict['color_legend_ax']
        ax3 = ax_dict['size_legend_ax']
        
        if not legend:
            ax2.remove()
            ax3.remove()
        else:
            # pass
            #'''
            if swap_ax == False:
                box = ax2.get_position()
                dx = (box.x1 - box.x0)*0.3
                box.x0 = box.x0 + dx
                box.x1 = box.x1 + dx
                ax2.set_position(box)
                
                box2 = ax3.get_position()
                dx = (box2.x1 - box2.x0)*0.3
                box2.x0 = box2.x0 + dx
                box2.x1 = box2.x1 + dx

                dy = (box2.y1 - box2.y0)
                if box2.y0 > (box.y1 + dy*2):
                    Dy = box2.y0 - (box.y1 + dy*2)
                    box2.y0 = box2.y0 - Dy
                    box2.y1 = box2.y1 - Dy
                else:
                    Dy = (box.y1 + dy*2) - box2.y0
                    box2.y0 = box2.y0 + Dy
                    box2.y1 = box2.y1 + Dy                    
                ax3.set_position(box2)
            #'''

        ## Variable Group plot
        axa = ax_dict['gene_group_ax']
        axa.clear()
        axa.set_frame_on(False)
        axa.grid(False)
        cnt = 0
        gap = 0.2

        n_cells = []
        for ct in mkrs_dict.keys():
            b = adata_t.obs[var_group_col] == ct
            n_cells.append(np.sum(b))
        n_cells = np.array(n_cells)
        p_cells = n_cells/n_cells.sum()

        for j, key in enumerate(mkrs_dict.keys()):
            L = len(mkrs_dict[key])
            '''
            pct = (1000*p_cells[j])
            if pct < 1:
                pct = '<0.1%'
            elif pct < 10:
                pct = '%3.1f' % (pct/10) + '%'
            else:
                pct = '%i' % int(pct/10) + '%'
            #'''    
            if swap_ax:
                axa.plot([hgt, hgt], [cnt+gap, cnt+L-gap], 'k', lw = 1.5) #Lw)
                axa.plot([hgt, 0], [cnt+gap, cnt+gap], 'k', lw = 1.5) #Lw)
                axa.plot([hgt, 0], [cnt+L-gap, cnt+L-gap], 'k', lw = 1.5) #Lw)
                axa.text(hgt*var_group_height, cnt+L/2, ' ' + key, fontsize = text_fs + 1, rotation = 0, ha = 'left', va = 'center')
            else:
                axa.plot([cnt+gap, cnt+L-gap], [hgt, hgt], 'k', lw = 1.5) #Lw)
                axa.plot([cnt+gap, cnt+gap], [hgt, 0], 'k', lw = 1.5) #Lw)
                axa.plot([cnt+L-gap, cnt+L-gap], [hgt, 0], 'k', lw = 1.5) #Lw)
                Ha = 'center'
                if (var_group_rotation > 0) & (var_group_rotation < 90):
                    Ha = 'left'
                elif (var_group_rotation < 0) & (var_group_rotation > -90):
                    Ha = 'right'                    
                axa.text(cnt+L/2, hgt*var_group_height, ' ' + key, fontsize = text_fs + 1, 
                         rotation = var_group_rotation, ha = Ha)
            cnt += L

        ## group extra plot
        axb = ax_dict['group_extra_ax']
        
        if swap_ax == False:
            pass
        else:
            box_main = ax.get_position()
            box = axb.get_position()
            box.y1 = box_main.y0 - (box.y1 - box.y0)
            box.y0 = box_main.y0
            axb.set_position(box)
        
        axb.clear()
        axb.set_frame_on(False)
        axb.get_xaxis().set_visible(False)
        axb.get_yaxis().set_visible(False)
        
        n_cells2 = []
        if categ_order is None:
            categ_order = list(mkrs_dict.keys())
            
        for ct in categ_order:
            b = adata_t.obs[Type_level] == ct
            n_cells2.append(np.sum(b))
        n_cells2 = np.array(n_cells2)
        p_cells2 = np.sqrt(n_cells2)
        # p_cells2 = p_cells2 - np.min(p_cells2*0.9)
        # p_cells2 = n_cells2/n_cells2.sum()
        p_cells2 = p_cells2/np.max(p_cells2)
        
        for j, key in enumerate(categ_order):
            if swap_ax:
                y = p_cells2[j]
                axb.add_patch(Rectangle((j+0.2, 0), 0.6, y, fill = True, 
                                        facecolor = 'firebrick', edgecolor = 'black', lw = 1.5)) #Lw))
                axb.text( j+0.5, y, ' %i ' % n_cells2[j], rotation = 90, ha = 'center', va = 'top', fontsize = text_fs)
            else:
                y = p_cells2[j]
                axb.add_patch(Rectangle((0, j+0.2), y, 0.6, fill = True, 
                                        facecolor = 'firebrick', edgecolor = 'black', lw = 1.5)) #Lw))
                axb.text( y, j+0.5, ' %i ' % n_cells2[j], rotation = 0, ha = 'left', va = 'center', fontsize = text_fs)
        
        ## Set x/y ticks again
        if swap_ax:
            ax.set_yticks( ticks = list(np.arange(len(ylabels))+0.5))
            ax.set_yticklabels(ylabels)
            ax.xaxis.set_ticks_position('top')
            ax.set_xticks( ticks = list(np.arange(len(categ_order))+0.5))
            ax.set_xticklabels(categ_order)
        else:
            ax.set_xticks( ticks = list(np.arange(len(ylabels))+0.5))
            ax.set_xticklabels(ylabels)
            ax.yaxis.set_ticks_position('left')
            ax.set_yticks( ticks = list(np.arange(len(categ_order))+0.5))
            ax.set_yticklabels(categ_order)
                
    plt.show()
    return 
                                                                

def plot_marker_exp(adata, markers = None, celltype_selection = None, var_group_col = None, cell_group_col = None,
                    N_cells_per_group_min = 20, N_markers_per_group_max = 15, N_markers_total = 200, 
                    title = None, title_y_pos = 1.1, title_fs = 14, text_fs = 12, linewidth = 1.5, 
                    var_group_height = 1.2, var_group_rotation = 0, standard_scale = 'var', 
                    nz_frac_max = 0.5, nz_frac_cutoff = 0.1, rem_mkrs_common_in_N_groups_or_more = 3,
                    mean_only_expressed = False, legend = False, figsize = (20, 4), swap_ax = False, 
                    add_rect = True, cmap = 'Reds', linecolor = 'royalblue' ):

    N_cells_min = N_cells_per_group_min
    if var_group_col is not None: 
        adata.obs[var_group_col] = adata.obs[var_group_col].astype(str)

    b_pass = False
    if markers is None:
        adata_s = adata[:,:].copy()
        b_pass = True
    elif celltype_selection is not None:
        if celltype_selection in list(adata.uns['DEG_grouping_vars'].keys()):
            deg_base = adata.uns['analysis_parameters']['CCI_DEG_BASE']
            b = adata.obs[deg_base] == celltype_selection
            adata_s = adata[b,:].copy()

            if (var_group_col is None) | (cell_group_col is None):
                var_group_col = adata_s.uns['DEG_grouping_vars'][celltype_selection]['condition col']
                cell_group_col = adata_s.uns['DEG_grouping_vars'][celltype_selection]['sample col']
                b_pass = True
            elif (var_group_col in list(adata.obs.columns.values)) & (cell_group_col in list(adata.obs.columns.values)):
                adata_s = adata[:,:]
                b_pass = True
        elif ('tumor' in celltype_selection.lower()) | ('cancer' in celltype_selection.lower()):
            b = adata.obs['tumor_origin_ind']
            adata_s = adata[b,:].copy()
            pcnt = adata_s.obs['celltype_major'].value_counts()
            target_celltype = None
            for i in pcnt.index:
                if (i != 'unassigned'):
                    target_celltype = i
                    break
            if target_celltype is not None:
                if target_celltype in list(adata.uns['DEG_grouping_vars'].keys()):
                    celltype_selection = target_celltype
                    var_group_col = adata_s.uns['DEG_grouping_vars'][celltype_selection]['condition col']
                    cell_group_col = adata_s.uns['DEG_grouping_vars'][celltype_selection]['sample col']
                    b_pass = True
                
    if not b_pass:
        if (var_group_col is not None) & (cell_group_col is not None):
            if (var_group_col in list(adata.obs.columns.values)) & (cell_group_col in list(adata.obs.columns.values)):
                adata_s = adata[:,:].copy()
                b_pass = True
            
    if not b_pass:
        print('ERROR: You need to specify either \'celltype_selection\' or \'var_group_col\' & \'cell_group_col\'.')
        return None
        
    if cell_group_col is not None: 
        adata_s.obs[cell_group_col] = adata_s.obs[cell_group_col].astype(str)

        ## Select samples with its No. of cells greater than 40
        pcnt = adata_s.obs[cell_group_col].value_counts()
        b = pcnt >= N_cells_min
        plst = list(pcnt.index.values[b])
        b = adata_s.obs[cell_group_col].isin(plst)
        adata_s = adata_s[b,:]
    
    selected_mkr_dict, adata_sss, var_group_col = get_best_markers( adata_s, 
                      markers_in = markers, var_group_col = var_group_col,  
                      nz_frac_cutoff = nz_frac_cutoff, N_cells_min = N_cells_min,
                      rem_mkrs_common_in_N_groups_or_more = rem_mkrs_common_in_N_groups_or_more, 
                      N_markers_per_group_max = N_markers_per_group_max, 
                      N_markers_total = N_markers_total )

    '''
    if cell_group_col is not None:
        lst = list(selected_mkr_dict.keys())
        for k in lst:
            if len(selected_mkr_dict[k]) == 0:
                del selected_mkr_dict[k]
    '''
    
    rv = plot_marker_exp_inner( adata_sss, markers = selected_mkr_dict, var_group_col = var_group_col, 
                      cell_group_col = cell_group_col, # group_categ_col = group_categ_col,
                      title = title, title_y_pos = title_y_pos, title_fs = title_fs,
                      text_fs = text_fs, linewidth = linewidth, standard_scale = standard_scale,
                      var_group_rotation = var_group_rotation, var_group_height = var_group_height,
                      nz_frac_max = nz_frac_max, figsize = figsize, swap_ax = swap_ax, 
                      mean_only_expressed = mean_only_expressed, 
                      legend = legend, add_rect = add_rect, cmap = cmap, rect_color = linecolor )
    return rv


def plot_deg( df_deg_dct, reference = 'log2_FC', n_genes_to_show = 30, pval_cutoff = 0.05, 
              figsize = (6,4), dpi = 100, text_fs = 10, title_fs = 12, label_fs = 11, 
              tick_fs = 10, ncols = 2, wspace = 0.15, hspace = 0.2, 
              deg_stat_dct = None, show_log_pv = True ):

    nr, nc = int(np.ceil(len(df_deg_dct.keys())/ncols)), int(ncols) # len(df_deg_dct.keys())
    fig, axes = plt.subplots(figsize = (figsize[0]*nc,figsize[1]*nr), nrows=nr, ncols=nc, # constrained_layout=True, 
                             gridspec_kw={'width_ratios': [1]*nc}, dpi = dpi)
    fig.tight_layout() 
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, 
                        wspace=wspace, hspace=hspace)

    for j, key in enumerate(df_deg_dct.keys()):
        if reference == 'nz_pct_score':
            b = df_deg_dct[key]['nz_pct_pval'] <= pval_cutoff
        else:
            b = df_deg_dct[key]['pval'] <= pval_cutoff
        if np.sum(b) > 0:
            dfs = df_deg_dct[key].loc[b,:].sort_values(reference, ascending = False)
            dfs = dfs.iloc[:min(n_genes_to_show, np.sum(b))]
    
            plt.subplot(nr,nc,j+1)
            # plt.figure(figsize = (6,4), dpi = 100)
            X = list(np.arange(dfs.shape[0]))
            Y = list(dfs[reference])
            plt.plot(X, Y)
            m = (np.max(Y)-np.min(Y))
            plt.ylim([np.min(Y)-m*0.4, np.max(Y) + m*0.5])
            tlst = list(dfs.index.values)
            for x, y, t in zip(X, Y, tlst):
                plt.text(x, y, '  %s' % (t), rotation = 90, fontsize = text_fs)
                if show_log_pv:
                    lpv =  -np.log10(dfs.loc[t,'pval_adj'])
                    plt.text(x, y, '(%3.1f) ' % (lpv), rotation = 90, va = 'top', fontsize = text_fs)
            if deg_stat_dct is None:
                plt.title(key, fontsize = title_fs)
            else:
                s = ' ('
                for kk in deg_stat_dct[key].keys():
                    s = s + '%s: %i, ' % (kk, deg_stat_dct[key][kk])
                s = '%s)' % s[:-2]
                plt.title(key + s, fontsize = title_fs)
                
            plt.xlabel('Genes', fontsize = label_fs)
            plt.yticks(fontsize=tick_fs)
            plt.xticks(fontsize=tick_fs)
            if j%nc == 0: plt.ylabel(reference, fontsize = label_fs)
            plt.grid('on')

    if nc*nr > len(df_deg_dct.keys()):
        for j in range(nc*nr-len(df_deg_dct.keys())):
            k = j + len(df_deg_dct.keys()) + 1
            ax = plt.subplot(nr,nc,k)
            ax.axis('off')

    plt.show()
    return


def plot_gsa_result( df_res, items_to_plot, dpi = 100, bar_width = 1,
                  title = None, title_pos = (0.5, 1), title_fs = 16, title_ha = 'center', 
                  label_fs = 10, tick_fs = 8, wspace=0.1, hspace=0.25, Ax = None, 
                  facecolor = 'firebrick', edgecolor = 'black'):

    if 'NES' not in list(df_res.columns.values):
        items_to_plot.remove('NES')
        
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ## draw result
        # sc.settings.set_figure_params(figsize = (4,(df_res.shape[0]*1.1 + 8)/9), dpi=100)
        plt.rcParams['figure.figsize'] = (4,(df_res.shape[0]*1.1 + 8)/9)      
        plt.rcParams['figure.dpi'] = dpi             

        nr, nc = 1, len(items_to_plot)
        fig, axes = plt.subplots(nrows=nr, ncols=nc, constrained_layout=False, dpi = dpi)
        fig.tight_layout() # Or equivalently,  "plt.tight_layout()"
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, 
                            wspace=wspace, hspace=hspace)
        if title is not None: 
            fig.suptitle(title, x = title_pos[0], y = title_pos[1], 
                         fontsize = title_fs, ha = title_ha)

        ylabel = 'Term'

        for k, x in enumerate(items_to_plot): # , '-log(q-val)-enr', 'NES-pr']):
            plt.subplot(1,nc,k+1)
            xlabel = x
            logpv_max = max( np.ceil( df_res[xlabel].max() ), 2 )
            ax = sns.barplot(data = df_res, y = ylabel, x = xlabel, 
                             facecolor = facecolor, orient = 'h', 
                             edgecolor = edgecolor, linewidth = 1, ax = Ax )

            if bar_width < 1:
                for patch in ax.patches:
                    current_height = patch.get_height()
                    # patch.set_y(patch.get_y() + current_height * bar_width/4)  
                    patch.set_height(current_height * bar_width)             
    
            # plt.xticks(fontsize = tick_fs)
            ax.tick_params(axis='both', which='major', labelsize = tick_fs)
            ax.set_xlabel(xlabel, fontsize = label_fs)
            if k == 0:
                ax.set_ylabel(ylabel, fontsize = label_fs)
            else:
                plt.yticks([])
                ax.set_ylabel(None)
            if x == 'NES':
                plt.xlim([-logpv_max, logpv_max])
            else:
                plt.xlim([0, logpv_max])

        plt.show()
    return True


def plot_gsa_bar_( df_res, pval_cutoff = 1e-2, nes_cutoff = 0, dpi = 100, N_max_to_show = 30,
                  title = None, title_pos = (0.5, 1), title_fs = 16, title_ha = 'center', 
                  label_fs = 10, tick_fs = 8, wspace=0.1, hspace=0.25, Ax = None,
                  items_to_plot = ['-log(p-val)', 'NES', '-log(q-val)'], bar_width = 1,
                  facecolor = 'firebrick', edgecolor = 'black' ):

    ## p-value cutoff 조건에 맞는 term들만 선택
    neg_log_p_cutoff = -np.log10(pval_cutoff)
    df = df_res.copy(deep = True)
    df = df.loc[df['-log(p-val)'] >= neg_log_p_cutoff ]
    if 'NES' in list(df.columns.values):
        df = df.loc[df['NES'] >= nes_cutoff ]
    df = df.sort_values(by = '-log(p-val)', ascending = False).iloc[:min(df.shape[0], N_max_to_show)]
    terms_sel = list(df.index.values)
    
    plot_gsa_result( df, copy.deepcopy(items_to_plot), dpi, bar_width,
                  title, title_pos, title_fs, title_ha, 
                  label_fs, tick_fs, wspace, hspace, Ax,
                  facecolor = facecolor, edgecolor = edgecolor )
    return df


def plot_gsa_bar( df_res, pval_cutoff = 1e-2, nes_cutoff = 0, dpi = 100, N_max_to_show = 30,
                  title = None, title_pos = (0.5, 1), title_fs = 16, title_ha = 'center', 
                  label_fs = 10, tick_fs = 8, wspace=0.1, hspace=0.25, Ax = None,
                  bar_width = 1, items_to_plot = ['-log(p-val)', 'NES', '-log(q-val)'],
                  facecolor = 'firebrick', edgecolor = 'black' ):
    
    if isinstance( df_res, pd.DataFrame ):
        df = plot_gsa_bar_( df_res, pval_cutoff = pval_cutoff, 
                            nes_cutoff = nes_cutoff, N_max_to_show = N_max_to_show,
                            title = title, title_pos = title_pos, title_fs = title_fs, title_ha = title_ha, 
                            label_fs = label_fs, tick_fs = tick_fs, wspace=wspace, hspace=hspace, Ax = Ax,
                            bar_width = bar_width, dpi = dpi, items_to_plot = items_to_plot,
                            facecolor = facecolor, edgecolor = edgecolor )
        return df
    elif isinstance( df_res, dict ):
        df_sel = {}
        for key in df_res.keys():        
            if df_res[key].shape[0] > 0:
                df = plot_gsa_bar_( df_res[key], pval_cutoff = pval_cutoff, 
                                    nes_cutoff = nes_cutoff, N_max_to_show = N_max_to_show,
                            title = key, title_pos = title_pos, title_fs = title_fs, title_ha = title_ha, 
                            label_fs = label_fs, tick_fs = tick_fs, wspace=wspace, hspace=hspace, Ax = Ax,
                            bar_width = bar_width, dpi = dpi, items_to_plot = items_to_plot,
                            facecolor = facecolor, edgecolor = edgecolor )
                df_sel[key] = df
        return df_sel
    else:
        return None
                

import matplotlib.pyplot as plt
import matplotlib as mpl

def get_gsa_summary( gsa_res, max_log_p = 10 ):
    
    df_gse_all = {}
    gsa_res_keys = gsa_res.keys()
    for ck in gsa_res_keys:
        df_dct = gsa_res[ck]
        for cs in df_dct.keys():
            if len(gsa_res_keys) == 1:
                case = '%s' % (cs)
            else:
                case = '%s: %s' % (ck, cs)
            df_gse_all[case] = df_dct[cs]

    case_lst = list(df_gse_all.keys())
    pws = []
    for key in df_gse_all.keys():
        df = df_gse_all[key]
        pws = list(set(pws).union(list(df.index.values)))

    pws.sort(reverse = True)

    dfc_qv = pd.DataFrame(0, index = pws, columns = case_lst, dtype = float)
    dfc_es = pd.DataFrame(0, index = pws, columns = case_lst, dtype = float)
    cnt_es = 0

    for case in df_gse_all.keys():

        df = df_gse_all[case]

        col1 = '%s' % case
        col2 = '%s' % case

        dfc_qv.loc[:,col1] = 0
        dfc_es.loc[:,col2] = 0

        b = ~df['-log(p-val)'].isnull()
        dfc_qv.loc[list(df.index.values[b]), col1] = list(df.loc[b, '-log(p-val)'])
        if 'NES' in list(df.columns.values):
            b = ~df['NES'].isnull()
            cnt_es += np.sum(b)
            dfc_es.loc[list(df.index[b]), col2] = list(df.loc[b, 'NES'])

    # display(dfc_qv.head())

    pw_sel = pws

    if cnt_es > 0:
        b = dfc_es.max(axis = 1) > 0
        df_qv = dfc_qv.loc[b,:] 
        df_es = dfc_es.loc[b,:] 
    else:
        df_qv = dfc_qv
        df_es = None

    df_qv = df_qv.clip(upper = max_log_p)
    
    return df_qv, df_es


def plot_gsa_dot( gsa_res, pval_cutoff = 1e-2,
                  title = 'Test', title_fs = 14, 
                  tick_fs = 10, xtick_rot = 90, xtick_ha = 'center',
                  label_fs = 10, legend_fs = 10, swap_ax = True, 
                  figsize = None, dpi = 100, dot_size = 14, 
                  cbar_frac = 0.05, cbar_aspect = 20, cmap = 'Reds' ):

    neg_log_p_cutoff = -np.log10(pval_cutoff)
    if isinstance( gsa_res, dict ):
        key_t = list(gsa_res.keys())[0]
        if isinstance( gsa_res[key_t], pd.DataFrame ):
            gsa_res_t = {'AAA': filter_gsa_result( gsa_res, neg_log_p_cutoff )}
        elif isinstance( gsa_res[key_t], dict ):
            gsa_res_t = {}
            for key in gsa_res.keys():
                gsa_res_t[key] = filter_gsa_result( gsa_res[key], neg_log_p_cutoff )
        else:
            print('ERROR: The input seems not suitably formatted. ')
            return None
    else:
        print('ERROR: The input seems not suitably formatted. ')
        return None
        
    df_qv, df_es = get_gsa_summary(gsa_res_t, max_log_p = 10)
    
    df1 = df_qv
    df2 = df_es
    alabel = 'Cases'
    n = df1.shape[0]

    mx_pnt_size = dot_size
    mx_pv = np.ceil(df1.max().max())
    ssf = mx_pnt_size/mx_pv
    
    mn, mx = 0, 1
    if df2 is not None:
        mn, mx = np.floor(df2.min().min()), np.ceil(df2.max().max())
        cbar_title = 'NES'
    else:
        mn, mx = np.floor(df1.min().min()), np.ceil(df1.max().max())
        cbar_title = '-log10(P)'
        
    norm = mpl.colors.Normalize(vmin=mn, vmax=mx)

    # plt.figure(figsize = (2+1, 2*df1.shape[0]/df1.shape[1]))
    if figsize is None:
        sf = 1/6
        if swap_ax:
            xs = (df1.shape[0] + 2) 
            ys = (df1.shape[1] + 2)
        else:
            xs = (df1.shape[1] + 2) 
            ys = (df1.shape[0] + 2)
            
        figsize = (sf*xs, sf*ys)
        fig, ax = plt.subplots(figsize = figsize, dpi = dpi) 
    else:
        fig, ax = plt.subplots(figsize = figsize, dpi = dpi) # figsize = (sf*xs, sf*ys)) 
    # ax = plt.figure(figsize = figsize)

    x = []
    y = []
    ss = []
    cc = []
    for j, c in enumerate(list(df1.columns.values)):
        if swap_ax:
            y = y + [j]*n
            x = x + list(np.arange(n))
        else:
            x = x + [j]*n
            y = y + list(np.arange(n))
        ss = ss + list(df1[c]*ssf)
        if df2 is None:
            cc = cc + list(df1[c])
        else:
            cc = cc + list(df2[c])

    p = ax.scatter( x, y, s = ss, c = cc, cmap = cmap )

    # plt.colorbar(p,cax=ax)
    ax.grid('off')  
    ax.set_title(title, fontsize = title_fs)

    # Set number of ticks for x-axis
    if swap_ax:
        plt.ylabel(alabel, fontsize = label_fs)
        ix, iy, yt_label, xt_label, fr = 0, 1, df1.columns.values, df1.index.values, 1 
    else:
        plt.xlabel(alabel, fontsize = label_fs)
        ix, iy, yt_label, xt_label, fr = 1, 0, df1.index.values, df1.columns.values, 0.1

    plt.ylim([-1, df1.shape[iy]])
    plt.xlim([-1, df1.shape[ix]])

    x = np.arange(df1.shape[ix])
    ax.set_xticks(x)
    # Set ticks labels for x-axis
    x_ticks_labels = list(xt_label)
    ax.set_xticklabels(x_ticks_labels, rotation=xtick_rot, ha = xtick_ha, fontsize=tick_fs)

    # Set number of ticks for x-axis
    y = np.arange(df1.shape[iy])
    ax.set_yticks(y)
    # Set ticks labels for x-axis
    y_ticks_labels = list(yt_label)
    a = ax.set_yticklabels(y_ticks_labels, rotation=0, fontsize=tick_fs)

    # Adding the colorbar
    cmap = p.cmap
    if swap_ax:
        lgap = 0.01
        frac = cbar_frac*0.05*figsize[0]/figsize[1]
        # cbaxes = fig.add_axes([0.91, 0.6, 0.1*df1.shape[1]/df1.shape[0], 0.25]) 
        cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),ax=ax, pad = frac*2, #cbar_gap,
                            fraction = frac, aspect = cbar_aspect, # shrink = cbar_shrink,
                            location = 'top', anchor = (1,1)) #, cax = cbaxes)
            
        # if df2 is not None:
        cbar.set_label(cbar_title, fontsize = legend_fs)
        for t in cbar.ax.get_xticklabels():
            t.set_fontsize(tick_fs)
    else:
        lgap = 0.02 
        frac = cbar_frac*0.05*figsize[1]/figsize[0]
        r = df1.shape[1]/df1.shape[0]
        # cbaxes = fig.add_axes([1, 1, 0.1*(1-df1.shape[1]/30), 0.1]) 
        cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),ax=ax, pad = frac*2, #cbar_gap, 
                            fraction = frac, aspect = cbar_aspect, 
                            location = 'right', anchor = (0,0)) #, cax = cbaxes)
            
        # if df2 is not None:
        cbar.set_label(cbar_title, fontsize = legend_fs)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(tick_fs)

    #'''
    if swap_ax:
        nn = 5 # list(np.arange(1,mx_pv,2)) 
        kw = dict(prop="sizes", num=nn, fmt="{x:1.0f}", func=lambda s: s/ssf, color = 'grey')
        legend = ax.legend(*p.legend_elements(**kw), title = '-log(P)',
                       fontsize = legend_fs, title_fontsize=legend_fs,
                       loc = 'upper left', bbox_to_anchor = (1+lgap, 1) )
    else:
        nn = 5 # int(mx_pv)
        kw = dict(prop="sizes", num=nn, fmt="{x:1.0f}", func=lambda s: s/ssf, color = 'grey')
        legend = ax.legend(*p.legend_elements(**kw), title = '-log(P)',
                       fontsize = legend_fs, title_fontsize=legend_fs,
                       loc = 'upper left', bbox_to_anchor = (1+lgap, 1) )
    #'''
    plt.show()
    return


def plot_gsa_all( gsa_res, 
                  title = 'Test', title_fs = 14, 
                  tick_fs = 10, xtick_rot = 90, xtick_ha = 'center',
                  label_fs = 10, legend_fs = 10, swap_ax = True, 
                  figsize = None, dot_size = 14, cbar_frac = 0.2, cbar_aspect = 20,
                  cmap = 'Reds' ):
             
    plot_gsa_dot( gsa_res, 
                  title, title_fs, 
                  tick_fs, xtick_rot, xtick_ha,
                  label_fs, legend_fs, swap_ax, 
                  figsize, dot_size, cbar_frac, cbar_aspect, cmap )    
    return


###############################
### CNV related UI function ###

def find_genes_in_genomic_spots( adata_s, spots, spot_ext = 0 ):

    spot_lst = []
    if isinstance(spots, int):
        spot_lst = [spots]
    elif isinstance(spots, list) | isinstance(spots, np.ndarray):
        spot_lst = list(spots)

    s_max = adata_s.obsm['X_cnv'].shape[1]
    genes = {}
    for s in spot_lst:
        slst = []
        for i in np.arange(-spot_ext, spot_ext+1, 1 ):
            si = s + i
            if si >= 0:
                slst.append(si)
            if si <= (s_max-1):
                slst.append(si)
        b = adata_s.var['spot_no'].isin(slst)
        genes[s] = adata_s.var.index.values[b]

    return genes


def find_chrm_of_genomic_spots( adata_s, spots ):

    spot_lst = []
    if isinstance(spots, int):
        spot_lst = [spots]
    elif isinstance(spots, list) | isinstance(spots, np.ndarray):
        spot_lst = list(spots)

    genes = {}
    for s in spot_lst:
        b = adata_s.var['spot_no'].isin([s])
        genes[s] = adata_s.var['chr'][b].value_counts().index.values[0]

    return genes


def find_genomic_spots_of_cnv_peaks( adata_s, group_col = None, width = 5, std_scale = 1, q = None, spot_ext = 1 ): #
    
    if group_col is None:
        ## Use q-quantile CNV to find peaks
        if q is None:
            mean_cnv = pd.DataFrame( adata_s.obsm['X_cnv'].todense() ).mean() # quantile(q)
        else:
            mean_cnv = pd.DataFrame( adata_s.obsm['X_cnv'].todense() ).quantile(q)
            
        std = mean_cnv.std()*std_scale
        peaks, peak_info = signal.find_peaks(mean_cnv, height = std, width = width)

        genes_in_gspots = find_genes_in_genomic_spots( adata_s, peaks, spot_ext )
        return genes_in_gspots

    elif group_col in list(adata_s.obs.columns.values):

        genes = {}
        lst = list(adata_s.obs[group_col].unique())
        for g in lst:
            b = adata_s.obs[group_col] == g
            adata_ss = adata_s[b,:]
            
            ## Use q-quantile CNV to find peaks
            if q is None:
                mean_cnv = pd.DataFrame( adata_ss.obsm['X_cnv'].todense() ).mean() # quantile(q)
            else:
                mean_cnv = pd.DataFrame( adata_ss.obsm['X_cnv'].todense() ).quantile(q)
            std = mean_cnv.std()*std_scale
            peaks, peak_info = signal.find_peaks(mean_cnv, height = std, width = width)

            genes_in_gspots = find_genes_in_genomic_spots( adata_ss, peaks, spot_ext )
            genes[g] = genes_in_gspots
            
        return genes
    else:
        return None

    return 


def get_band_from_a_spot( spot, adata, g2cgloc ):

    gene_first = None
    gene_last = None
    dct = find_genes_in_genomic_spots(adata, list(spot), spot_ext = 0)
    # dct = spots_dct
    

    if g2cgloc is not None:
        g2cgloc_keys = list(g2cgloc.keys())
    else:
        g2cgloc_keys = []
        for k in dct.keys():
            glst = dct[k]
            g2cgloc_keys = g2cgloc_keys + glst
    
    b = False
    genes_lst = []
    for k in dct.keys():
        glst = dct[k]
        for g in glst:
            if g in list(g2cgloc_keys):
                if not b:
                    gene_first = g
                    b = True
                if g not in genes_lst:
                    genes_lst.append(g)
                # break
        # if b: break

    if gene_first is not None:
        b = False
        for k in reversed( list(dct.keys()) ):
            glst = dct[k]
            for g in reversed(glst):
                if g in list(g2cgloc_keys):
                    gene_last = g
                    b = True
                    break
            if b: break

    if (gene_first is not None) & (g2cgloc is not None):
        s = '%s:%s' % (g2cgloc[gene_first], g2cgloc[gene_last])
        band_lst = []
        for g in genes_lst:
            bnd = g2cgloc[g]
            if bnd not in band_lst:
                band_lst.append(bnd)
    else:
        s = 'Unknown band'
        band_lst = []

    return s, np.array(genes_lst), np.array(band_lst)
    

def get_band_from_spot_list( spot_llst, adata, g2cgloc ):

    slst = []
    glst = []
    blst = []
    for lst in spot_llst:
        s, genes_lst, band_lst = get_band_from_a_spot( lst, adata, g2cgloc )
        slst.append(s)
        glst.append(genes_lst)
        blst.append(band_lst)

    return slst, glst, blst


def get_mean_and_std_from_gmm_250318( gmm ):
    
    mt = gmm.means_.max(axis = 0)
    idx_t = gmm.means_.argmax(axis = 0)
    vt = gmm.covariances_[idx_t, range(len(mt))]
    st = np.sqrt(vt) #/len(idx_t))

    return mt, st

def break_regions( loci, n_ext, lmax ):
    
    lst = []
    s = [loci[0]]
    if n_ext > 0:
        for j in range(n_ext):
            if s[0]-1 < 0: break
            else:
                s = [s[0]-1] + s
            
    for i in loci[1:]:
        if i == (s[-1]+1):
            s = s + [i]
        else:
            if n_ext > 0:
                for j in range(n_ext):
                    if s[-1]+1 >= lmax: break
                    else:
                        s = s + [s[-1]+1]
            lst.append(np.array(s))
            s = [i]
            if n_ext > 0:
                for j in range(n_ext):
                    if s[0]-1 < 0: break
                    else:
                        s = [s[0]-1] + s
            
    if len(s) > 0:
        if n_ext > 0:
            for j in range(n_ext):
                if s[-1]+1 >= lmax: break
                else:
                    s = s + [s[-1]+1]
        lst.append(np.array(s))
    return lst


def get_mean_and_std_from_gmm( gmm ):
    
    mt = gmm.means_.max(axis = 0)
    idx_t = gmm.means_.argmax(axis = 0)
    vt = gmm.covariances_[idx_t, range(len(mt))]
    st = np.sqrt(vt) #/len(idx_t))
    wt = gmm.weights_[idx_t]

    return mt, st, wt


def get_cnv_gain_dec(mt, st, mn, sn, std_scale, t_gain_min):

    z = (mt - mn)/(st + sn)    
    # bx = ((mt - st*std_scale) > (mn + sn*std_scale)) & (mt >= t_gain_min) 
    bx = (z >= std_scale) & (mt >= t_gain_min)
    return bx


def find_signif_CNV_gain_regions_( adata, # target, 
                                  gmm_ncomp_t = 4, gmm_ncomp_n = 2, gmm_ncomp_t_per_sample = 2, 
                                  cov_type = 'diag', reg_covar = 1e-3,
                                  std_scale = 1, t_gain_min = 0.05, sample_col = 'sample', cond_col = 'condition',
                                  n_cells_min = 50, n_samples_min = 2, n_ext = 2, med_filter_len = 5, N_spots_min = 10 ):

    ## adata is assumed to contain only tumor cells
    if n_samples_min < 1:
        b1 = (adata.obs['ploidy_dec'] == 'Aneuploid') 
        pcnt = adata[b1,:].obs[sample_col].value_counts()
        bx = pcnt >= n_cells_min
        ilst = list( pcnt.index.values[bx] )
        b2 = adata.obs[sample_col].isin( ilst )
        b = b1 & b2
        cond_lst = list( adata[b,:].obs[cond_col].unique() )
        
        ns_mins = {}
        for c in cond_lst:
            b = adata.obs[cond_col] == c
            slst_t = list( adata.obs.loc[b, sample_col].unique() )
            ns_mins[c] = len(slst_t)

        n_samples_min = max( 2, np.min(list(ns_mins.values()))*n_samples_min )
        # print(ns_mins, n_samples_min)
                
    b = adata.obs['tumor_origin_ind']
    pcnt = adata.obs.loc[b, 'celltype_major'].value_counts()
    target = pcnt.index.values[0]
    if target == 'unassigned':
        target = pcnt.index.values[1]
    
    X_cnv = np.array(adata.obsm['X_cnv'].todense())
    b = adata.obs['ploidy_dec'] == 'Aneuploid'
    
    bt = (adata.obs['celltype_for_cci'] == 'Aneuploid %s' % target)
    gmm_tumor = mixture.GaussianMixture(n_components = int(gmm_ncomp_t), covariance_type = cov_type, 
                                        random_state = 0, reg_covar = reg_covar)
    gmm_tumor.fit( X_cnv[bt,:] )
    
    bn = (adata.obs['celltype_for_cci'] == 'Diploid %s' % target) | (adata.obs['celltype_for_cci'] == target)
    gmm_normal = mixture.GaussianMixture(n_components = int(gmm_ncomp_n), covariance_type = cov_type, 
                                        random_state = 0, reg_covar = reg_covar)
    gmm_normal.fit( X_cnv[bn,:] )

    n_t = np.sum(bt)
    n_n = np.sum(bn)
    
    mt, st, wt = get_mean_and_std_from_gmm( gmm_tumor )
    mn, sn, wn = get_mean_and_std_from_gmm( gmm_normal )
    
    # z = (mt - mn)/(st + sn)    
    # bx = ((mt - st*std_scale) > (mn + sn*std_scale)) & (mt >= t_gain_min) 
    #'''
    bx = get_cnv_gain_dec(mt, st, mn, sn, std_scale, t_gain_min)
    bx = signal.medfilt(bx.astype(int), med_filter_len).astype(bool)
    
    spot_lst = list(np.arange(len(mt))[bx])
    #'''

    llst = {}
    pcnt = None
    if (sample_col is not None) & (sample_col in list(adata.obs.columns.values)):
        slst = list( adata.obs[sample_col].unique() )
        spot_lst_all = []
        df_z = pd.DataFrame(index = slst, columns = range(X_cnv.shape[1]))
        df_z.loc[:,:] = 0
        for s in slst:
        
            bt = (adata.obs['celltype_for_cci'] == 'Aneuploid %s' % target) & (adata.obs[sample_col] == s)
            if np.sum(bt) >= n_cells_min:
                ## intentionally used 'gmm_ncomp_n' for aneuploid cells
                gmm_tumor_sample = mixture.GaussianMixture(n_components = int(gmm_ncomp_t_per_sample), 
                                                    covariance_type = cov_type, 
                                                    random_state = 0, reg_covar = reg_covar)
                gmm_tumor_sample.fit( X_cnv[bt,:] )
                mta, sta, wta = get_mean_and_std_from_gmm( gmm_tumor_sample )
                
                z = (mta - mn)/(sta + sn)            
                # b = ((mta - sta*std_scale) > (mn + sn*std_scale)) & (mta >= t_gain_min) # (z > 0.5) & (mt >= 0.08)
                b = get_cnv_gain_dec(mta, sta, mn, sn, std_scale, t_gain_min)
                if med_filter_len > 1:
                    b = signal.medfilt(b.astype(int), med_filter_len).astype(bool)

                df_z.loc[s,:] = list(z*b)
                spot_lst_all = spot_lst_all + list(np.arange(len(mta))[b])
    
        spot_lst_all = pd.Series(spot_lst_all, name = 'spot')
        pcnt = spot_lst_all.value_counts()
        # b = pcnt >= n_samples_min
        # spot_lst_c = list(pcnt.index.values[b])

        #'''
        n_samples_min_org = n_samples_min
        nM = 10
        for i in range(nM):
            n_samples_min = n_samples_min_org*(nM - i)/nM
            bz = (df_z > 0).sum() >= n_samples_min
            spot_lst_c = list(df_z.columns.values[bz])
        
            spot_lst = spot_lst_c # list(set(spot_lst).intersection(spot_lst_c))
            spot_lst.sort()
    
            if len(spot_lst) > 0:
                bx[:] = False
                bx[spot_lst] = True
                if med_filter_len > 1:
                    bx = signal.medfilt(bx.astype(int), med_filter_len).astype(bool)
                spot_lst = list(np.arange(len(mt))[bx])
                if len(spot_lst) > 0:
                    llst = break_regions( spot_lst, n_ext = n_ext, lmax = X_cnv.shape[1] )
                    
            if len(llst) >= N_spots_min:
                break
            n_samples_min = max(2, n_samples_min)            

        print('INFO: n_samples_min: %i -> %i ' % (n_samples_min_org, n_samples_min))
            
    # if ('gene_to_band_map' in list(adata.uns.keys())) & (llst is not None):
    if (llst is not None):
        # g2cgloc = adata.uns['gene_to_band_map']
        b = ~adata.var['cytogenetic_band'].isnull()
        glst = list(adata.var.index.values[b])
        blst = list(adata.var['cytogenetic_band'].values[b])
        g2cgloc = dict(zip(glst, blst))

        bname_lst, genes_llst, band_llst = get_band_from_spot_list( llst, adata, g2cgloc )
        
        spot_llst = dict(zip(bname_lst, llst))
        band_llst = dict(zip(bname_lst, band_llst))
        gene_llst = dict(zip(bname_lst, genes_llst))
    else:
        spot_llst = llst
        band_llst = None
        gene_llst = None
        

    dct_r = {}
    dct_r['genes'] = gene_llst
    dct_r['bands'] = band_llst
    dct_r['spots'] = spot_llst
    dct_r['gmm (Aneuploid)'] = gmm_tumor
    dct_r['gmm (Diploid)'] = gmm_normal
    dct_r['N_cells_used'] = {'Aneuploid': n_t, 'Diploid': n_n}
    dct_r['dfZ'] = df_z

    if pcnt is not None:
        cnt = np.zeros([len(llst)])
        for s in spot_lst:
            for j, lst in enumerate(llst):
                if (s in lst) & (s in list(pcnt.index.values)):
                    cnt[j] += pcnt[s]
                    
        for j, lst in enumerate(llst):
            cnt[j] = cnt[j]/len(lst)

        # if 'gene_to_band_map' in list(adata.uns.keys()):
        if (llst is not None):
            dct_r['sample_count'] = dict(zip(bname_lst, cnt.round(2)))
        else:
            dct_r['sample_count'] = cnt.round(2)

    return dct_r

def find_signif_CNV_gain_regions( adata_in, groupby = 'sample_ext_for_deg', 
                                  N_cells_min = 50, N_cells_max = 0,
                                  gmm_ncomp_t = 3, gmm_ncomp_n = 1, gmm_ncomp_t_per_sample = 2, 
                                  cov_type = 'diag', reg_covar = 1e-3,
                                  std_scale = 1, t_gain_min = 0.05, sample_col = 'sample',
                                  n_samples_min = 0.5, n_ext = 2, med_filter_len = 5, N_spots_min = 8 ):

    if groupby not in list( adata_in.obs.columns.values ):
        print('ERROR: %s not in the obs.columns. ' % groupby )
        return None
    else:
        pcnt = adata_in.obs[groupby].value_counts()
        if (N_cells_max > 0) & (N_cells_max < 1):
            N_cells_max = int(pcnt.quantile(N_cells_max))
            if (N_cells_min > 0) & (N_cells_min < 1): 
                N_cells_min = int(N_cells_max*N_cells_min)
            print('N_cells_max: %i, %i (%i, %i) ' % (N_cells_max, N_cells_min, pcnt[0], pcnt[-1]))
            
        bp = pcnt >= N_cells_min
        b = adata_in.obs[groupby].isin(list(pcnt.index.values[bp]))
        adata = adata_in[b,:].copy()
    
        if N_cells_max > 0:
            ## Resample cells to balance cell counts across samples 
            slst = adata.obs[groupby].unique()
            idx_all = adata.obs.index.values
            idx_sel = []
            for s in slst:
                b = adata.obs[groupby] == s
                
                if np.sum(b) <= N_cells_max:
                    idx_sel = idx_sel + list(idx_all[b])
                else:
                    idx_sel = idx_sel + random.sample(list(idx_all[b]), N_cells_max)
            
            adata = adata[idx_sel,:]

    results = find_signif_CNV_gain_regions_( adata, 
                                             gmm_ncomp_t = gmm_ncomp_t, gmm_ncomp_n = gmm_ncomp_n, 
                                             gmm_ncomp_t_per_sample = gmm_ncomp_t_per_sample,
                                             cov_type = cov_type, reg_covar = reg_covar,
                                             std_scale = std_scale, t_gain_min = t_gain_min, sample_col = sample_col,
                                             n_cells_min = N_cells_min, n_samples_min = n_samples_min, 
                                             n_ext = n_ext, med_filter_len = med_filter_len, N_spots_min = N_spots_min )

    df = check_cnv_hit( results['spots'], adata, 
                        gmm_ncomp_t = gmm_ncomp_t, gmm_ncomp_n = gmm_ncomp_n, 
                        sample_col = sample_col, std_scale = std_scale, t_gain_min = t_gain_min, 
                        n_cells_min = N_cells_min, med_filter_len = med_filter_len )
    results['cnv_peaks_pos'] = df
    
    return results
        

def check_cnv_hit( cnv_spot_lst, adata, gmm_ncomp_t = 4, gmm_ncomp_n = 2, sample_col = 'sample',
                   cov_type = 'diag', reg_covar = 1e-3, std_scale = 1, t_gain_min = 0.05, 
                   n_cells_min = 50, n_ext = 1, med_filter_len = 5 ):

    b = adata.obs['tumor_origin_ind']
    pcnt = adata.obs.loc[b, 'celltype_major'].value_counts()
    target = pcnt.index.values[0]
    if target == 'unassigned':
        target = pcnt.index.values[1]
    
    X_cnv = np.array(adata.obsm['X_cnv'].todense())

    bn = (adata.obs['celltype_for_cci'] == 'Diploid %s' % target) | (adata.obs['celltype_for_cci'] == target)
    gmm_normal = mixture.GaussianMixture(n_components = int(gmm_ncomp_n), covariance_type = cov_type, 
                                        random_state = 0, reg_covar = reg_covar)
    gmm_normal.fit( X_cnv[bn,:] )
    mn, sn, wn = get_mean_and_std_from_gmm( gmm_normal )

    slst = list( adata.obs[sample_col].unique() )

    if isinstance( cnv_spot_lst, list ):
        s_llst = cnv_spot_lst
        df = pd.DataFrame( columns = range(len(s_llst)), dtype = int )
    else:
        s_llst = list(cnv_spot_lst.values())
        nlst = list(cnv_spot_lst.keys())
        df = pd.DataFrame( columns = nlst, dtype = int )
    
    spot_lst_all = []
    for s in slst:
    
        bt = (adata.obs['celltype_for_cci'] == 'Aneuploid %s' % target) & (adata.obs[sample_col] == s)
        if np.sum(bt) >= n_cells_min:
            ## intentionally used 'gmm_ncomp_n' for aneuploid cells
            gmm_tumor_sample = mixture.GaussianMixture(n_components = int(gmm_ncomp_t), 
                                                covariance_type = cov_type, 
                                                random_state = 0, reg_covar = reg_covar)
            gmm_tumor_sample.fit( X_cnv[bt,:] )
            mta, sta, wta = get_mean_and_std_from_gmm( gmm_tumor_sample )

            z = (mta - mn)/(sta + sn)            
            # b = ((mta - sta*std_scale) > (mn + sn*std_scale)) & (mta >= t_gain_min) # (z > 0.5) & (mt >= 0.08)
            b = get_cnv_gain_dec(mta, sta, mn, sn, std_scale, t_gain_min)
            if med_filter_len >1:
                b = signal.medfilt(b.astype(int), med_filter_len).astype(bool)
            
            if np.sum(b) > 0:
                llst = break_regions( list(np.arange(len(mta))[b]), n_ext = n_ext, lmax = X_cnv.shape[1] )
    
                icnt = []
                z_ave = []
                for j, w in enumerate(s_llst):
                    cnt = 0
                    zs = 0
                    for t in llst:
                        c = list(set(list(w)).intersection(list(t)))
                        if len(c) > 0:
                            cnt = 1
                            zst = np.mean(z[list(w)])
                            if zst > zs:
                                zs = zst
                    icnt.append(cnt)
                    z_ave.append(zs)
    
                df.loc[s,:] = z_ave # icnt
            else:
                df.loc[s,:] = 0

    if isinstance( cnv_spot_lst, list ):
        rngs = []
        for lst in s_llst:
            s = '%i-%i' % (lst[0], lst[-1])
            rngs.append(s)

        idx = df.columns.values
        rend = dict(zip(idx, rngs))
        df.rename( columns = rend, inplace = True)

    return df # .astype(int)


def get_col_colors( n, cmap_name = 'tab10'):
    
    cmap = plt.cm.get_cmap(cmap_name, n)
    clrs = [mpl.colors.to_hex(cmap(i)) for i in range(n)]
    return clrs


def plot_cnv_stat( adata, x_lower, x_upper, gmm_tumor, gmm_normal,
                   title_fs = 12, label_fs = 11, legend_fs = 9,
                   tick_fs = 9, xtick_rot = -90, xtick_ha = 'center', 
                   std_scale = 1, figsize = (8,3), ax = None, cmap_name = 'tab10', 
                   grid = True, text_pos_adj = 0.6, rng_ext = 12, 
                   known_markers_list = [], title = None ):

    mt, st, wt = get_mean_and_std_from_gmm( gmm_tumor )
    mn, sn, wn = get_mean_and_std_from_gmm( gmm_normal )

    M = rng_ext
    sw = std_scale
    x_lower_e = x_lower - M
    x_upper_e = x_upper + M+1
        
    dct = find_genes_in_genomic_spots(adata, list(np.arange(adata.obsm['X_cnv'].shape[1])), spot_ext = 0)
    
    bold_blue = "\033[1;34m"  # 1: Bold, 34: Blue
    reset = "\033[0m"
    
    x_e = np.arange(x_lower_e, x_upper_e)
    
    xx = []
    for i in range(x_lower, x_upper+1):
        glst = dct[i]
        s = '%4i (' % i
        for g in glst:
            if g in known_markers_list:
                s = s + r'$\bf{%s}$, ' % g
            else:
                s = s + '%s, ' % g
        s = s[:-2] + ')'
        xx.append(s)

    colors = get_col_colors( 10, cmap_name = cmap_name )
    
    if ax is None:
        fig, axes = plt.subplots(figsize = figsize, dpi=100, nrows=1, ncols=1, constrained_layout=False)
        fig.tight_layout() 
        ax = axes
    
    ax.plot( x_e, mt[x_lower_e:x_upper_e], color = colors[0], label = 'mean CNV (Aneuploid)' )
    ax.plot( x_e, mn[x_lower_e:x_upper_e], color = colors[1], label = 'mean CNV (Diploid)' )
    
    ax.fill_between(x_e, 
                     mt[x_lower_e:x_upper_e] - st[x_lower_e:x_upper_e]*sw, 
                     mt[x_lower_e:x_upper_e] + st[x_lower_e:x_upper_e]*sw, 
                     color = colors[0], alpha=.2, label = 'mean CNV $\pm$ $\sigma$ (Aneuploid)')
    
    ax.fill_between(x_e, 
                     mn[x_lower_e:x_upper_e] - sn[x_lower_e:x_upper_e]*sw, 
                     mn[x_lower_e:x_upper_e] + sn[x_lower_e:x_upper_e]*sw, 
                     color = colors[1], alpha=.2, label = 'mean CNV $\pm$ $\sigma$ (Diploid)')
    
    ylim = plt.gca().get_ylim()
    xlim = plt.gca().get_xlim()
    # plt.fill_between(x, ylim[0], ylim[1], color = colors[2], alpha=.2)
    ax.fill_between([x_lower-0.5, x_upper+0.5], ylim[0], ylim[1], color = colors[2], alpha=.2, label = 'Region of signif. gain')
    
    
    ax.legend(fontsize = legend_fs, loc = 'upper left')
    
    ax.set_xlabel('Genomic spot', fontsize = label_fs)
    ax.set_ylabel('CNV', fontsize = label_fs)
    if title is None:
        ax.set_title('Genomic spots around %i - %i' % (x_lower, x_upper), fontsize = title_fs )
    else:
        ax.set_title(title, fontsize = title_fs )
    
    # plt.plot( np.arange(x_lower, x_upper)[b[x_lower:x_upper]], 0.25*(b[x_lower:x_upper])[b[x_lower:x_upper]], 'r+' )

    #'''
    if xtick_rot == 0:
        ax.tick_params(axis='x', which='major', labelsize=tick_fs, rotation = xtick_rot)
    else:
        ax.set_xticks( x_e, x_e, rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
    #'''
    ax.tick_params(axis='y', labelsize=tick_fs)

    ss = r'$\bf{Spot}$ $\bf{(Genes)}$:'
    ss = ss + '\n'
    for xt in xx:
        ss = ss + '%s\n' % xt
    ax.text( xlim[0], ylim[0] - (ylim[1]-ylim[0])*text_pos_adj, ss, fontsize = tick_fs, va = 'top' )
    if grid: ax.grid(True)
    
    return ax


from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def plot_cnv_hit( df, title = None, title_fs = 13, label_fs = 12, tick_fs = 10, 
                  wspace = 0.1, dpi = 100, ylabel = 'Genomic region', bin_size = 0.22,
                  cmap = None ):

    nr, nc = 1, 2

    hspace = wspace
    Nr = (df.sum(axis = 0) > 0).sum()
    Ns = df.shape[0]
    fs = ( bin_size*Ns*1.2, bin_size*Nr )
    w = fs[1]
    width_ratios = [fs[0], 1.2]
    aa = (width_ratios[0]+width_ratios[1])/width_ratios[0]
    figsize = (w*aa*fs[0]/fs[1], w)
    
    fig, axes = plt.subplots(nrows=nr, ncols=nc, constrained_layout=False, dpi = dpi, 
                             gridspec_kw={'width_ratios': width_ratios}, figsize = figsize)
    fig.tight_layout() 
    wspace = wspace*12/Ns
    # hspace = 0.1
    
    if title is not None: 
        fig.suptitle(title, x = 0.5, y = 1 + 0.05*(25/Nr), fontsize = title_fs, ha = 'center')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=wspace, hspace=hspace)
    
    ax = axes[0]
    cax = inset_axes(ax,
                     width="4%",  # width: 40% of parent_bbox width
                     height="20%",  # height: 10% of parent_bbox height
                     loc='lower left',
                     bbox_to_anchor=(-0.08, 0, 1, 1),
                     bbox_transform=ax.transAxes,
                     borderpad=0 )
    
    g = sns.heatmap( df.transpose(), # row_cluster = False, col_cluster = False,
                       annot = True,
                       annot_kws = {'size': 8}, fmt = '.1f',
                       cbar_ax = cax,
                       cbar_kws = dict(use_gridspec=True, orientation = 'vertical', 
                                       location = 'left', shrink = 0.3),
                       linewidth=0.5, vmax = 1, ax = ax,
                       yticklabels=False, cmap = cmap)
    
    # g.set_title( 'Average z-score in the region ($z_{max}$ = 1)', fontsize = title_fs )
    ax.tick_params( axis = 'both', labelsize = tick_fs ) 
    a = ax.set_ylabel(ylabel, fontsize = label_fs)
    
    #'''
    ax = axes[1]
    bar_values = ((df[ reversed(list(df.columns.values)) ] > 0).mean(axis = 0))
    ax = bar_values.plot.barh(fontsize = 10, ax = ax)
    ax.set_xlim([0,1])
    ax.grid()
    # ax.set_title(title, fontsize = title_fs)
    ax.set_xlabel('Frequency', fontsize = label_fs)
    ndiv = 5
    ax.set_xticks( np.arange(ndiv+1)/ndiv, np.arange(ndiv+1)/ndiv, fontsize = tick_fs, rotation = 90 ) 
    ax.tick_params( axis = 'y', labelsize = tick_fs ) 
    ax.yaxis.tick_right()
    dd = np.round( bar_values.max() + 0.4, 1 )
    ax.set_xlim( [0, dd])
    label_lst = [' %3.2f' % a for a in list(bar_values.round(2))]
    a = ax.bar_label(ax.containers[0], labels=label_lst, rotation = 0, fontsize = tick_fs-2)

    return axes

