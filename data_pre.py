import pandas as pd
import numpy as np
weather_predict=pd.read_csv('d:/lzm/ForecastDataforTraining/ForecastDataforTraining.csv')
#对于之前的CSV文件进行整理。
data=pd.read_csv('d:/lzm/In-situMeasurementforTraining.csv')

test=[0 for i in range(10)]
for i in range(10):
    test[i]=weather_predict[(weather_predict.realization==i+1)&(weather_predict.hour>=9)&(weather_predict.hour<=20)]
    test[i].columns=['xid', 'yid', 'date_id', 'hour','realization','wind_'+str(i+1)]
    test[i]=test[i].drop(['realization'],axis=1)


result=test[0]
for i in range(1,10):
    result=pd.merge(result,test[i],how='left',on=['xid', 'yid', 'date_id', 'hour'])


final_report=pd.merge(result,data,how='left',on=['xid', 'yid', 'date_id', 'hour'])
final_report.to_csv('d:/lzm/wind_predict')