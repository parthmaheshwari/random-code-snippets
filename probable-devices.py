#script 1, returns anomaly time, phase and ccms id

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pylab import rcParams
import numpy as np
from requests import get,post


def send_anomaly(ccmsId,timestamp,phase):
    ccmsId = 'sjpl'
    probable_poles = get(url = 'http://192.168.43.252:1337/fetchCcmsAggregation',params = {'ccmsId':ccmsId,'phase':phase})
    poles_df = pd.DataFrame(probable_poles.json())
    poles_df['Remaining_Hours'] = poles_df['currLifeTime'] - poles_df['runtime']
    poles_df['ccmsId'] = ccmsId
    poles_df['timestamp'] = timestamp
    poles_df['phase'] = phase
    poles_df['anomalyId'] = 'abcd' #to be self generated
    poles_df = poles_df.sort('Remaining_Hours')
    poles_json = poles_df.head(5).to_json(orient='index')
    print(poles_json)
    # post(url = 'http://192.168.43.252:1337/generateInsights', data = poles_json)


def update_runtime(ccmsId,timestamp):

    #script 2, returns runtime of a ccms every day
    daily_consumption = pd.read_excel('DailyConsumption (4).xlsx')
    daily_consumption = daily_consumption[['Timestamp','ON Load Duration']]
    daily_consumption = daily_consumption.set_index('Timestamp')
    daily_consumption = daily_consumption.sort_index()
    dcjson = daily_consumption.to_json(orient = 'records')
    post(url = '', data = dcjson)

# currently reads a locally saved excel sheet, requires an extention to run on realtime json data
raw_report = pd.read_excel('Instant Raw Report (11).xlsx')
raw_report['Timestamp'] = pd.to_datetime(raw_report['Timestamp'])
raw_report = raw_report.set_index('Timestamp')
raw_report = raw_report.sort_index()
raw_report['MovingAverage_R Phase kW'] = raw_report['R Phase kW'].rolling(5).mean()
raw_report['MovingAverage_Y Phase kW'] = raw_report['Y Phase kW'].rolling(5).mean()
raw_report['MovingAverage_B Phase kW'] = raw_report['B Phase kW'].rolling(5).mean()
raw_report['Prev_R_kW'] = raw_report['R Phase kW'].shift(1)
raw_report['Prev_R1_kW'] = raw_report['R Phase kW'].shift(2)
raw_report['Prev_Y_kW'] = raw_report['Y Phase kW'].shift(1)
raw_report['Prev_Y1_kW'] = raw_report['Y Phase kW'].shift(2)
raw_report['Prev_B_kW'] = raw_report['B Phase kW'].shift(1)
raw_report['Prev_B1_kW'] = raw_report['B Phase kW'].shift(2)
# raw_report['Prev_R2_kW']
# raw_report[['R Phase kW','Prev_R_kW','Prev_R1_kW','MovingAverage_R Phase kW','Y Phase kW','Prev_Y_kW','Prev_Y1_kW','MovingAverage_Y Phase kW','B Phase kW','Prev_B_kW','Prev_B1_kW','MovingAverage_B Phase kW']]
raw_report.replace(0, np.nan, inplace=True)
mov_avg_r = np.nan
mov_avg_y = np.nan
mov_avg_b = np.nan

for index, row in raw_report.iterrows():
    if mov_avg_r - row['R Phase kW'] > 0.1 and mov_avg_r - row['Prev_R_kW'] > 0.1 and mov_avg_r - row['Prev_R1_kW'] > 0.1:
         send_anomaly(row['CCMS ID'],row['timestamp'],'r')
# #         print('anomaly r',index)
    if mov_avg_y - row['Y Phase kW'] > 0.1 and mov_avg_r - row['Prev_Y_kW'] > 0.1 and mov_avg_r - row['Prev_Y1_kW'] > 0.1:
         send_anomaly(row['CCMS ID'],row['timestamp'],'y')
#           print('anomaly y',index)
    if mov_avg_b - row['B Phase kW'] > 0.1 and mov_avg_r - row['Prev_B_kW'] > 0.1 and mov_avg_r - row['Prev_B1_kW'] > 0.1:
        send_anomaly(row['CCMS ID'],row['timestamp'],'b')
#         print('anomaly b',index)    
    
    mov_avg_r = row['MovingAverage_R Phase kW']
    mov_avg_y = row['MovingAverage_Y Phase kW']
    mov_avg_b = row['MovingAverage_B Phase kW']
    
