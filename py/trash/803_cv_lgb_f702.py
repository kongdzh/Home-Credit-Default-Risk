#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 07:35:01 2018

@author: Kazuki
"""

import gc, os
from tqdm import tqdm
import pandas as pd
import sys
sys.path.append(f'/home/{os.environ.get("USER")}/PythonLibrary')
import lgbextension as ex
import lightgbm as lgb
from multiprocessing import cpu_count, Pool
#from glob import glob
import count
import utils, utils_cat
utils.start(__file__)
#==============================================================================

SEED = 71

HEAD = 500

param = {
         'objective': 'binary',
         'metric': 'auc',
         'learning_rate': 0.01,
         'max_depth': 6,
         'num_leaves': 63,
         'max_bin': 255,
         
         'min_child_weight': 10,
         'min_data_in_leaf': 150,
         'reg_lambda': 0.5,  # L2 regularization term on weights.
         'reg_alpha': 0.5,  # L1 regularization term on weights.
         
         'colsample_bytree': 0.9,
         'subsample': 0.9,
#         'nthread': 32,
         'nthread': cpu_count(),
         'bagging_freq': 1,
         'verbose':-1,
         'seed': SEED
         }

# =============================================================================
# load
# =============================================================================
imp = pd.read_csv('LOG/imp_801_imp_lgb_onlyMe.py-2.csv')
imp['split'] /= imp['split'].max()
imp['gain'] /= imp['gain'].max()
imp['total'] = imp['split'] + imp['gain']
imp.sort_values('total', ascending=False, inplace=True)

#imp = imp[~imp.feature.str.startswith('f702')]
#imp = imp[~imp.feature.str.startswith('f01')]

use_files = (imp.head(HEAD).feature + '.f').tolist()

files = utils.get_use_files(use_files, True)

X = pd.concat([
                pd.read_feather(f) for f in tqdm(files, mininterval=60)
               ], axis=1)
y = utils.read_pickles('../data/label').TARGET


if X.columns.duplicated().sum()>0:
    raise Exception(f'duplicated!: { X.columns[X.columns.duplicated()] }')
print('no dup :) ')
print(f'X.shape {X.shape}')

gc.collect()

CAT = list( set(X.columns)&set(utils_cat.ALL))

# =============================================================================
# cv
# =============================================================================
dtrain = lgb.Dataset(X, y, categorical_feature=CAT )
gc.collect()

ret = lgb.cv(param, dtrain, 9999, nfold=5,
             early_stopping_rounds=100, verbose_eval=50,
             seed=SEED)

result = f"CV auc-mean(all): {ret['auc-mean'][-1]}"
print(result)

utils.send_line(result)


# =============================================================================
# cv
# =============================================================================
col = [c for c in X.columns if c.startswith('f702') or c.startswith('f01')]
dtrain = lgb.Dataset(X.drop(col, axis=1), y, categorical_feature=CAT )
gc.collect()

ret = lgb.cv(param, dtrain, 9999, nfold=5,
             early_stopping_rounds=100, verbose_eval=50,
             seed=SEED)

result = f"CV auc-mean(drop all): {ret['auc-mean'][-1]}"
print(result)

utils.send_line(result)

# =============================================================================
# cv
# =============================================================================
col = [c for c in X.columns if c.startswith('f01')]
dtrain = lgb.Dataset(X.drop(col, axis=1), y, categorical_feature=CAT )
gc.collect()

ret = lgb.cv(param, dtrain, 9999, nfold=5,
             early_stopping_rounds=100, verbose_eval=50,
             seed=SEED)

result = f"CV auc-mean(drop f01): {ret['auc-mean'][-1]}"
print(result)

utils.send_line(result)

# =============================================================================
# cv
# =============================================================================
col = [c for c in X.columns if c.startswith('f702') ]
dtrain = lgb.Dataset(X.drop(col, axis=1), y, categorical_feature=CAT )
gc.collect()

ret = lgb.cv(param, dtrain, 9999, nfold=5,
             early_stopping_rounds=100, verbose_eval=50,
             seed=SEED)

result = f"CV auc-mean(drop f702): {ret['auc-mean'][-1]}"
print(result)

utils.send_line(result)

#==============================================================================
utils.end(__file__)
#utils.stop_instance()



