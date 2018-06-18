#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 02:09:55 2018

@author: Kazuki


based on
https://www.kaggle.com/jsaguiar/updated-0-792-lb-lightgbm-with-simple-features/code
"""

import numpy as np
import pandas as pd
import gc
import os
from multiprocessing import Pool, cpu_count
NTHREAD = cpu_count()
import utils
utils.start(__file__)
#==============================================================================
PREF = 'pos_202_'

KEY = 'SK_ID_CURR'

month_start = -12*1 # -96
month_end   = -12*0 # -96

os.system(f'rm ../feature/t*_{PREF}*')
# =============================================================================
# 
# =============================================================================
pos = utils.read_pickles('../data/POS_CASH_balance')
pos = pos[pos['MONTHS_BALANCE'].between(month_start, month_end)]


num_aggregations = {
    # TODO: optimize stats
    'MONTHS_BALANCE': ['max', 'mean', 'min', 'size'],
    'SK_DPD': ['max', 'mean'],
    'SK_DPD_DEF': ['max', 'mean']
}

col_cat = ['NAME_CONTRACT_STATUS']

train = utils.load_train([KEY])
test = utils.load_test([KEY])

# =============================================================================
# 
# =============================================================================
def aggregate():
    
    df = pos
    
    li = []
    for c1 in df.columns:
        for c2 in col_cat:
            if c1.startswith(c2+'_'):
                li.append(c1)
                break
    
    cat_aggregations = {}
    for cat in li:
        cat_aggregations[cat] = ['mean', 'sum']
    
    df_agg = df.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
    df_agg.columns = pd.Index([e[0] + "_" + e[1] for e in df_agg.columns.tolist()])
    df_agg.reset_index(inplace=True)
    
    tmp = pd.merge(train, df_agg, on=KEY, how='left').drop(KEY, axis=1)
    utils.to_feature(tmp.add_prefix(PREF), '../feature/train')
    
    tmp = pd.merge(test, df_agg, on=KEY, how='left').drop(KEY, axis=1)
    utils.to_feature(tmp.add_prefix(PREF),  '../feature/test')
    
    return


# =============================================================================
# main
# =============================================================================

#argss = [
#        ['NAME_CONTRACT_STATUS', 'Approved', 'approved_'],
#        ['NAME_CONTRACT_STATUS', 'Approved', 'refused_'],
#        ['active',    1, 'active_'],
#        ['completed', 1, 'completed_'],
#        ]
#
#pool = Pool(NTHREAD)
#callback = pool.map(aggregate, argss)
#pool.close()

aggregate()



#==============================================================================
utils.end(__file__)
