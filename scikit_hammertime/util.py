"""
Script: util.py
===============

Description:
------------
    
    utilities for dealing with data

Usage:
------

    python preprocess.py -i $DATA_DIR -o data.df

##################
Jay Hack
jhack@stanford.edu
Fall 2014
##################
"""
import os
import pickle as pkl
import pandas as pd

def load_data(num_dfs=1, data_dir='/data/aers/formatted', verbose=True):
    """
        loads and concatenates the specified number of dataframes 
    """
    if verbose:
        print '-----> Loading data (%d dataframes)' % num_dfs

    df_paths = [os.path.join(data_dir, p) for p in os.listdir(data_dir) if p.endswith('.df')]
    dfs = [pkl.load(open(p, 'r')) for p in df_paths[:num_dfs]]
    data = pd.concat(dfs, axis=0)
    return data


def load_drug_names(path='/data/aers/formatted/new_drug_names.pkl', verbose=True):
    if verbose:
        print '-----> Loading drugnames (%s)' % path
    
    return pkl.load(open(path, 'r'))



