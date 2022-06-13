# -*- coding: utf-8 -*-
"""
Created on Thu May 19 19:06:04 2022

@author: BlueSpark
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from bokeh.plotting import figure
from bokeh.models.formatters import DatetimeTickFormatter
# st.set_page_config(layout="wide")

base_url = r"http://127.0.0.1:81/"

# @st.cache
def fetch_county():
    url = base_url + "county_building"
    response = requests.get(url).json()
    if response['response'] == 'Success':
        data = response['data']
    else:
        data =[]
    return data

st.title('Commercial Building Energy Forecast')

st.write("This is a web application to allow user to import data and performing\
         forecasting. The application is using prophet package.")

with st.expander("Upload Data to Server"):
    url_post = base_url + r"historical/csv"
    uploaded_files_0 = st.file_uploader("Choose a CSV file for building energy", accept_multiple_files=True)
    uploaded_files_1 = st.file_uploader("Choose a CSV file for county building list", accept_multiple_files=True)
    uploaded_files_2 = st.file_uploader("Choose a CSV file for county weather data", accept_multiple_files=True)

    submit_up = st.button("Upload")
    if submit_up:
        for uploaded_file in uploaded_files_0:
             bytes_data = uploaded_file.read()
             st.write("filename:", uploaded_file.name)
             file= {"file":bytes_data}
             test2 = requests.post(url_post, params={"file_type":"0"},files =file)
             st.write("Upload "+test2.json()["response"])
        for uploaded_file in uploaded_files_1:
             bytes_data = uploaded_file.read()
             st.write("filename:", uploaded_file.name)
             file= {"file":bytes_data}
             test2 = requests.post(url_post, params={"file_type":"1"},files =file)
             st.write("Upload "+test2.json()["response"])
        for uploaded_file in uploaded_files_2:
             bytes_data = uploaded_file.read()
             st.write("filename:", uploaded_file.name)
             file= {"file":bytes_data}
             test2 = requests.post(url_post, params={"file_type":"2"},files =file)
             st.write("Upload "+test2.json()["response"])
        data= fetch_county()
        if 'county' not in st.session_state:
            if len(data)>0:
                st.session_state['county'] = pd.DataFrame(data)
            else:
                st.session_state['county'] = ""

if 'building_list' not in st.session_state:
    st.session_state['building_list'] = []

if 'count' not in st.session_state:
    st.session_state['count'] = 0

data= fetch_county()

# df_county = pd.DataFrame([
#         {"county_id": "County1","building_id":1},
#         {"county_id": "County1","building_id":2},
#         {"county_id": "County1","building_id":3},
#         {"county_id": "County2","building_id":45},
#         ])

if 'county' not in st.session_state:
    if len(data)>0:
        st.session_state['county'] = pd.DataFrame(data)
    else:
        st.session_state['county'] = ""
    # st.session_state['county'] = pd.DataFrame([
    #     {"county_id": "County1","building_id":1},
    #     {"county_id": "County1","building_id":2},
    #     {"county_id": "County1","building_id":3},
    #     {"county_id": "County2","building_id":45},
    #     ])

if 'flag' not in st.session_state:
    st.session_state['flag'] = 0


col1, col2, col3, col4 = st.columns([5,5,1,1])
with col1:
    if len(st.session_state['county']) >0:
        option1 = st.selectbox(
              'County',
              tuple(set(st.session_state['county'].county_id)))
    else:
        option1 = st.selectbox(
              'County',
              (""))

with col2:
    if option1:
        list_build=list(st.session_state.county['building_id'][st.session_state.county['county_id']==option1])
    else:
        if len(st.session_state['county']) >0:
            list_build=st.session_state.county['building_id'].iloc[0]
        else:
            list_build=""
    option2 = st.selectbox(
        'Building List',
        options=list_build)
with col3:
    st.write("")
    st.write("")
    add_building =  st.button("+")
    
with col4:
    st.write("")
    st.write("")
    remove_building =  st.button("-")
    
if add_building:
    new_item = {"County":option1, "Building": option2}
    if new_item not in st.session_state['building_list']:
        st.session_state['building_list'].append(new_item)
    st.session_state['count'] =1
if remove_building:
    if len(st.session_state['building_list'])>0:
        st.session_state['building_list'].pop(-1)
    if len(st.session_state['building_list']) ==0:
        st.session_state['count'] =0
        
if st.session_state['count'] >0:
    df = pd.DataFrame(st.session_state['building_list'])
    st.table(df) 

tcol1, tcol2, tcol3 = st.columns(3)
with tcol1:
    days_to_forecast = st.number_input('Days to Forecast', min_value=1, step=1, value=3)
    # st.write(days_to_forecast)
with tcol2:
    st.write("")
    st.write("")
    use_center = st.checkbox('Cluster Based Method')
    # st.write(use_center)
with tcol3:
    st.write("")
    st.write("")
    submit = st.button("Forecast")
if submit:
    buildList = [each['Building'] for each in st.session_state['building_list']]
    url = base_url+ 'forecast'
    response = requests.get(url,params={"buildList":str(buildList), "days_in_future":int(days_to_forecast),"use_center":use_center}).json()['forecast']
    
    # for i in range(len(st.session_state['building_list'])):
        # chart_data= pd.DataFrame(np.random.randn(20), columns=[str(i)])
        # st.line_chart(chart_data)
    for each in response:
        x = [datetime.strptime(item, '%a, %d %b %Y %H:%M:%S %Z') for item in each['time']]
        y = each['energy']
        z= each['energy_hist']
        label = each['building_id']
        # fig, ax = plt.subplots()
        # ax.plot(x,y,label=label)
        # st.pyplot(fig)
        p = figure(
         title='Building '+ str(label) + ' Energy',
         x_axis_label='time',
         y_axis_label='kWh')
        future_points = int(days_to_forecast)*24*4
        p.line(x, y, legend_label='Forecast', line_width=2, line_dash='dashed',line_color='red')
        p.line(x[0:len(z)], z, legend_label= 'Historical', line_width=2)
        p.xaxis.formatter = DatetimeTickFormatter(
                hours=["%m-%d %H:%M"],
                days=["%Y-%m-%d"],
                months=["%Y-%m"],
                years=["%Y"]
            )
        st.bokeh_chart(p, use_container_width=True)

        

    