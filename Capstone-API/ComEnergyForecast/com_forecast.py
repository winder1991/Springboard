# -*- coding: utf-8 -*-
"""
Created on Sat May 14 20:34:38 2022

@author: BlueSpark
"""
import pandas as pd
import pickle
from prophet import Prophet
import warnings
import math
import matplotlib.pyplot as plt
import os
import csv
from bokeh.plotting import figure, show

model_path =r"..\model\\"
global __df_centers
global __df_sample_timestamp
global __df_timestamp
global __df_std
global __tuned_param

with open(model_path+'com_cluster_centers.pickle', 'rb') as f:
    __df_centers = pickle.load(f)

with open(model_path + 'timestamp.pickle', 'rb') as f:
    __df_sample_timestamp = pickle.load(f)
    __df_timestamp = __df_sample_timestamp

with open(model_path+'com_cluster_stdev.pickle', 'rb') as f:
    __df_std=pickle.load(f)

with open(model_path+'prophet_tuned_parameters.pickle', 'rb') as f:
    __tuned_param=pickle.load(f)

def predict_cluster (timestamp,  energy):
    if len(timestamp) < 35039:
        new_ts = [ts.replace(year=2018) for ts in timestamp]
    else:
        new_ts = [ts.replace(year=2018) for ts in timestamp[0:35039]]
    with open(model_path+'timestamp.pickle', 'rb') as f:
        df_timestamp = pickle.load(f)
    energy_indices = [list(df_timestamp).index(ts) for ts in new_ts if ts in list(df_timestamp)]
    deviations =[]
    if len(energy_indices) == len (energy):
        for center in __df_centers['center']:
            center_value = [center[i] for i in energy_indices]
            dev_energy = [(i-j)**2 for (i,j) in zip(energy, center_value)]
            deviations.append(sum(dev_energy)/len(center_value))
    else:
        new_energy = [energy[i] for i in range(len(timestamp)) if timestamp[i] in list(df_timestamp)]
        for center in __df_centers['center']:
            center_value = [center[i] for i in energy_indices]
            dev_energy = [(i-j)**2 for (i,j) in zip(new_energy, center_value)]
            deviations.append(sum(dev_energy)/len(center_value))
    cluster_index = deviations.index(min(deviations))
    dev = [math.sqrt(min(deviations))]
    return __df_centers['clusters'].iloc[cluster_index], dev

def is_summer(ds):
    date = pd.to_datetime(ds)
    return (date.month >5 and date.month <11)

def adjust_time(current_datetime, num_year):

    time_loc = len(__df_sample_timestamp)
    if __df_sample_timestamp[len(__df_sample_timestamp)-1] == current_datetime.replace(year=2019):
        current_year = current_datetime.year
        __df_sample_timestamp[len(__df_sample_timestamp)-1].replace(year=current_year)
        current_all_year =[each.replace(year=(current_year-1)) for each in __df_sample_timestamp if each != current_datetime]
        current_all_year.append(current_datetime)
    else:
        end_date = current_datetime.replace(year=2018)
        current_year = current_datetime.year
        time_loc = list(__df_sample_timestamp).index(end_date)
        second_half_time = list(__df_sample_timestamp)[0:(time_loc+1)]
        first_half_time = list(__df_sample_timestamp)[(time_loc+1):]
        first_half_time = [each.replace(year=(each.year-1)) for each in first_half_time]
        first_half_time.extend(second_half_time)
        diff = current_year - 2018
        current_all_year = [each.replace(year=(each.year+diff)) for each in first_half_time]
    current_temp =[]
    for num in range(num_year):
        num_new = num_year -num-1
        if num_new !=0:
            current_temp.extend([each.replace(year=(each.year-num_new)) for each in current_all_year])
        else:
            current_temp.extend(current_all_year)
    return current_temp.copy(), time_loc

def predict_load_seasonality (timestamp, building_ids, counties, energy, temperature, humidity, days_in_future, use_center=False, use_center_trigger_num=10, num_year=10):
    future_loading=[]
    unique_counties =list(set(counties))
    if use_center and len(building_ids)>use_center_trigger_num :
        labels =[]
        devs=[]
        min_maxes=[]
        for i in range(len(building_ids)):
            if building_ids[i] in list(__df_std['bldg_id']):
                cluster = __df_std['cluster_id'][__df_std['bldg_id']==building_ids[i]].iloc[0]
                dev = __df_std['std'][__df_std['bldg_id']==building_ids[i]].iloc[0]
                min_max = __df_std['min_max'][__df_std['bldg_id']==building_ids[i]].iloc[0]
            else:
                cluster, dev = predict_cluster(timestamp, energy[i])
                min_max = [min(energy[i]), max(energy[i])]
            labels.append(cluster)
            devs.append(dev)
            min_maxes.append(min_max)
        df_cluster_items = pd.DataFrame({"cluster_id":labels, "county":counties, "std":devs,"min_max":min_maxes})
        set_cluster_county = list(set(list(zip(labels, counties))))
        forecasts =[]
        ts_new = timestamp[-1].replace(year=2018)
        length = len(__df_timestamp[__df_timestamp<ts_new])
        new_time, time_loc = adjust_time(timestamp[-1], num_year)
        for each in set_cluster_county:
            center = __df_centers['center'][__df_centers['clusters']==each[0]].iloc[0]
            if length >= len(timestamp):
                center_value = center[(length-len(timestamp)):length]
            else:
                diff = len(temperature) - length
                center_value_rear = center[0:length]
                center_value_front = center[-length]
                center_value = center_value_front.extend(center_value_rear)
            temp_index = unique_counties.index(each[1])
            temp_hist = temperature[temp_index][0:len(timestamp)]
            new_value=[]
            if time_loc != len(center):
                temp = list(center)[(time_loc+1):] + list(center)[0:(time_loc+1)]
                center = temp
            for i in range(num_year):
                new_value.extend(center)
            df_input= pd.DataFrame({"ds":new_time, 'y':new_value})
            df_input['summer'] = df_input['ds'].apply(is_summer)
            df_input['winter'] = ~df_input['ds'].apply(is_summer)
            param = __df_centers['param'][__df_centers['clusters']==each[0]].iloc[0]
            m = Prophet(changepoint_prior_scale=param['changepoint_prior_scale'], seasonality_prior_scale=param['seasonality_prior_scale'], 
                        weekly_seasonality=False, yearly_seasonality =param['yearly_seasonality'])
            m.add_seasonality(name='weekly_on_summer', period=7, fourier_order=__tuned_param[0]['weekly_seasonality'].iloc[0], condition_name='summer')
            m.add_seasonality(name='weekly_on_winter', period=7, fourier_order=__tuned_param[0]['weekly_seasonality'].iloc[0], condition_name='winter')
            m.fit(df_input)
            future= m.make_future_dataframe(periods=days_in_future*24*4,freq="15min")
            future['summer'] = future['ds'].apply(is_summer)
            future['winter'] = ~future['ds'].apply(is_summer)
            forecast = m.predict(future)
            forecasts.append(forecast)
        for i in range(len(building_ids)):
            min_max_i = df_cluster_items['min_max'].iloc[i]
            energy_min = min_max_i[0]
            energy_max = min_max_i[1]
            normal_energy = [(e- energy_min)/(energy_max-energy_min) for e in energy[i]]
            current_cs =(df_cluster_items['cluster_id'].iloc[i], df_cluster_items['county'].iloc[i])
            set_id = set_cluster_county.index(current_cs)
            forecast_i = forecasts[set_id][(len(new_time)-len(timestamp)):].copy()
            old_predict = forecast_i['yhat'][0:len(timestamp)]
            sign = [i-j for (i,j) in zip(normal_energy, old_predict)]
            day_points =24*4
            days = 7
            if (days_in_future<= 7):
                if len(timestamp)> (24*4*7):
                    days = 7
                else:
                    days = int(len(sign)/day_points)
            temp_sign = sign[-day_points*days:]
            new_dev = [0]* day_points
            for i in range(len(temp_sign)):
                new_dev[i%day_points] = new_dev[i%day_points]+temp_sign[i]
            new_dev = [each_dev/days for each_dev in new_dev]
            sign.extend(new_dev*days_in_future)
            forecast_i['yhat'] = [i+j for (i,j) in zip(list(forecast_i['yhat']),sign)]
            forecast_i[['yhat', 'yhat_lower', 'yhat_upper']]= forecast_i[['yhat', 'yhat_lower', 'yhat_upper']]*(min_max_i[1]-min_max_i[0])+min_max_i[0]
            future_loading.append((forecast_i, energy[i]))
    else:
        # with open(model_path+'com_cluster_centers.pickle', 'rb') as f:
        #     df_centers=pickle.load(f)
        # with open(model_path+'com_cluster_stdev.pickle', 'rb') as f:
        #     df_std=pickle.load(f)
        for i in range(len(building_ids)):
            energy_min = min(energy[i])
            energy_max = max(energy[i])
            unique_counties =list(set(counties))
            normal_energy = [(e- energy_min)/(energy_max-energy_min) for e in energy[i]]
            temp_index = unique_counties.index(counties[i])
            temp_hist = temperature[temp_index][0:len(timestamp)]
            df_input = pd.DataFrame({'ds':timestamp, 'y':normal_energy,'Temperature':temp_hist})
            if building_ids[i] in list(__df_std['bldg_id']):
                cluster = __df_std['cluster_id'][__df_std['bldg_id']==building_ids[i]].iloc[0]
            else:
                cluster, dev = predict_cluster(timestamp, energy[i])
            param = __df_centers['param'][__df_centers['clusters']==cluster].iloc[0]
            m = Prophet(seasonality_mode='multiplicative')
            m.add_regressor('Temperature')
            m.fit(df_input)
            future= m.make_future_dataframe(periods=days_in_future*24*4,freq="15min")
            future['Temperature'] = temperature[temp_index]
            forecast = m.predict(future)
            forecast[['yhat', 'yhat_lower', 'yhat_upper']]= forecast[['yhat', 'yhat_lower', 'yhat_upper']]*(energy_max-energy_min)+energy_min
            future_loading.append((forecast, energy[i]))
    return future_loading.copy()

def save_test_csv(test, timestamp, days_in_future):
    for i in range(len(test['building'])):
        with open('../test/building_energy_'+test['building'][i]+'.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'building_id', 'kW'])
            for j in range(len(test['energy'][i])):
                writer.writerow([timestamp[j].isoformat()+'Z', test['building'][i], test['energy'][i][j]] )
    with open('../test/county_building_sample.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['county','building_id'])
        for i in range(len(test['building'])):
            writer.writerow([test['county_list'][i], test['building'][i] ])
    new_county = list(set(test['county_list']))
    new_time = timestamp.copy()
    for step in range(days_in_future*24*4):
        new_time.append(new_time[-1]+pd.Timedelta('0 days 00:15:00'))
    for i in range(len(new_county)):
        with open('../test/county_weather'+new_county[i]+'.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'county', 'temperature', 'humidity'])
            for j in range(len(test['temperature'][i])):
                writer.writerow([new_time[j].isoformat()+'Z', new_county[i], test['temperature'][i][j], test['humidity'][i][j]] )


# from https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])
        


if __name__=='__main__':
    with open(model_path+'test_sample_week.pickle', 'rb') as f:
        test = pickle.load(f)
    with open(model_path+'timestamp.pickle', 'rb') as f:
        df_timestamp = pickle.load(f)
    timestamp = df_timestamp[2000:(2000+30*24*4)]
    days_in_future=7
    # save_test_csv(test, list(timestamp), days_in_future)
    with warnings.catch_warnings(record=True) as w:
        with suppress_stdout_stderr():
            forecasts = predict_load_seasonality (list(timestamp), test['building'][0:1], test['county_list'][0:1], test['energy'][0:1], test['temperature'][0:1], test['humidity'][0:1], days_in_future, use_center=True, use_center_trigger_num=0 )
    # fig, axs = plt.subplots(len(test['building'][0:2]), 1)
    # fig.set_size_inches(18.5, 20.5)
    # for i in range(len(test['building'][0:1])):
    #     axs[i].plot(forecasts[i]['ds'], forecasts[i]['yhat'])
    #     axs[i].axvline(x=list(timestamp)[-1])
    #     axs[i].plot(forecasts[i]['ds'],test['energy'][i]+test['f_energy'][i] )
    p = figure(
     title='simple line example',
     x_axis_label='time',
     y_axis_label='kWh')
    x= forecasts[0]['ds']
    y= forecasts[0]['yhat']
    z= test['energy'][0]
    p = figure(
     title='Test Line',
     x_axis_label='time',
     y_axis_label='kWh')

    p.line(x, y, legend_label='Forecast', line_width=2, line_dash='dashed',line_color='red')
    p.line(x[0:len(z)], z, legend_label='Historical', line_width=2)
    show(p)
