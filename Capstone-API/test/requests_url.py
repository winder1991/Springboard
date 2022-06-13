# -*- coding: utf-8 -*-
"""
Created on Fri May 20 20:40:31 2022

@author: BlueSpark
"""
import requests

url=r"http://127.0.0.1:81/forecast"
buildList=str([1447])
days_in_future=3
use_center=False
# test = requests.get(url, params={"buildList":buildList, "days_in_future":days_in_future,"use_center":use_center})

url_post = r"http://127.0.0.1:81//historical/csv"
file_energy =r"C:\MLBootCamp\Springboard\Flask_API\Flask_API_Forecast\test\building_energy_1447.csv"
with open(file_energy,'rb') as payload:
    file= {"file":payload}
    test2 = requests.post(url_post, params={"file_type":"0"},files =file)