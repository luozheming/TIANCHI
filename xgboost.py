#http://blog.csdn.net/u011089523/article/details/72812019   XGboost学习

#https://www.cnblogs.com/mfryf/p/6293814.html  xgboost调参

#XGboost代码
import xgboost as xgb
import pandas as pd 
import numpy as np
from random import shuffle
data=pd.read_csv('/home/lmi/data/weather_predict/wind_predict.csv')

#对数据进行二分类
data.loc[data.wind_true<20,'wind_true']=0
data.loc[data.wind_true>=20,'wind_true']=1

#打乱数据,并对数据进行7:3的分类
shuffle(data_analysis)
p=0.7#将数据进行7:3的训练测试数集划分
X_train=data_analysis[:int(len(data_analysis)*p),:]
X_test=data_analysis[int(len(data_analysis)*p):,:]

dtrain=xgb.DMatrix(X_train[:,:15], label=X_train[:,15])
dtest=xgb.DMatrix(X_test[:,:15], label=X_test[:,15])
# specify parameters via map
param = {'max_depth':2, 'eta':1, 'silent':1, 'objective':'binary:logistic','booster':'gbtree',
'objective':'reg:logistic'} # 类别数，与 multisoftmax 并用 
num_round = 200
bst = xgb.train(param, dtrain, num_round)
# make prediction
preds = bst.predict(dtest)
labels = dtest.get_label()
print ('error=%f' % ( sum(1 for i in range(len(preds)) if int(preds[i]>0.5)!=labels[i]) /float(len(preds))))  
print ('correct=%f' % ( sum(1 for i in range(len(preds)) if int(preds[i]>0.5)==labels[i]) /float(len(preds))))


##结果:error=0.011883
#correct=0.988117