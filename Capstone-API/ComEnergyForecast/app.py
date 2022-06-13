# -*- coding: utf-8 -*-
"""
Created on Tue May 10 20:31:55 2022

@author: BlueSpark
"""
from flask import Flask, request, jsonify
from helper import listify, update_county, unique_update, update_energy, update_weather
from datetime import datetime
import os
from os.path import join, dirname, realpath
from pymongo import MongoClient
from pymongo import UpdateOne
import pandas as pd
from com_forecast import predict_load_seasonality

app = Flask(__name__)

app.config["DB_path"] ='../data'
app.config["mongo_connection"] ='mongodb://localhost:27081'

client = MongoClient(app.config["mongo_connection"])


def initiate(client,test=False):
    db = client.ComEnergy
    collection_name = db.list_collection_names()
    if "energy" not in collection_name:
        db.create_collection('energy', timeseries={ 'timeField': 'time', 'metaField': 'building_id' })
    if "weather" not in collection_name:
        db.create_collection('weather', timeseries = {'timeField': 'time', 'metaField': 'county_id'})
    if "county" not in collection_name:
        db.create_collection('county')
        db.county.create_index("building_id", unique=True)
    if test:
        test_folder= r'../test/'
        energy_files =[test_folder+f for f in os.listdir(r'..\test') if 'building_energy_' in f]
        weather_files = [test_folder+f for f in os.listdir(r'..\test') if 'county_weatherG' in f]
        county_file = test_folder+'county_building_sample.csv'
        for each in energy_files:
            update_energy(db, each)
        for each in weather_files:
            update_weather(db, each)
        update_county(db, county_file)     
    return db

@app.route('/')
def index():
    return "Welcome to Commercial Building Energy Forecast API"

@app.route('/forecast',methods = ['GET'])
def get_forecast():
    if request.method == 'GET':
        db = initiate(client)
        # ABC = parser.parse_args()
        print(request.args.get('buildList'),request.args.get('days_in_future'),request.args.get('use_center'))
        days_in_future = int(request.args.get('days_in_future'))
        print(days_in_future)
        use_center = bool(request.args.get('use_center'))
        print(request.args.get('buildList'))
        buildList = listify(request.args.get('buildList'))
        print(buildList)
        countyList =[]
        energyList =[]
        tempList =[]
        humidList =[]
        for each in buildList:
            query_build ={"building_id":each}
            find_county = list(db['county'].find(query_build))
            # print(find_county)
            if len(find_county)>0:
                query_weather = {"county_id":find_county[0]['county_id']}
                find_weather = list(db['weather'].find(query_weather))
                if len(find_weather)>0:
                    query_energy = {"building_id": each}
                    find_energy = pd.DataFrame(db['energy'].find(query_energy))
                    if len(find_energy)>0:
                        time = list(find_energy["time"])
                        countyList.append(find_county[0]['county_id'])
                        energyList.append(list(find_energy['kW']))
                    else:
                        return jsonify({'response': 'Error: Could not find energy data for this building.'})
                else:
                    return jsonify({'response': 'Error: Weather data does not exist for this building.'})
            else:
                return jsonify({'response': 'Error: County data could not be found for this building.'})
        if len(countyList)>0:
            new_countyList= []
            for i in range(len(countyList)):
                if i>0:
                    if countyList[i] not in countyList[0:i]:
                        new_countyList.append(countyList[i])
                else:
                    new_countyList.append(countyList[i])
            for each_county in new_countyList:
                time_start = time[0]
                time_end = time[-1] + pd.Timedelta(str(days_in_future)+' days')
                query_weather_time = {"county_id":each_county, "time":{"$lte":time_end, "$gte":time_start}}
                find_weather = pd.DataFrame(db['weather'].find(query_weather_time))
                if len(find_weather)>0:
                    tempList.append(list(find_weather['temperature']))
                    humidList.append(list(find_weather['humidity']))
                else:
                    return jsonify({'response': 'Error: No valid weather data exist for county '+ each_county+'.'})
        forecast = predict_load_seasonality(time, buildList, countyList, energyList, tempList, humidList, days_in_future, 
                                            use_center=use_center, use_center_trigger_num=2)
        results =[]
        for i in range(len(buildList)):
            results.append({"building_id":buildList[i], "time": list(forecast[i][0]['ds']),'energy':list(forecast[i][0]['yhat']), 
                            'energy_hist':list(forecast[i][1])})
        # results =[{"test":["a","c"],"test2":["b"]},
        #           {"test":["c"], "test2":["d"]}]
        return jsonify({"response":"Success","forecast":results})

@app.route('/county_building',methods = ['GET'])
def get_county_building():
    db = initiate(client)
    results = []
    if request.method =='GET':
        counties = db.county.find()
        results = [{"building_id":each["building_id"], "county_id": each['county_id']} for each in counties]
    # return jsonify({"response":"Success", "data": counties})
    if len(results)>0:
        return jsonify({"response":"Success","data":results})
    else:
        return jsonify({"response":"Failed. Please make sure county building list exist"})



@app.route('/historical',methods =['POST'])
def post_historical():
    is_batch = int(request.args.get('is_batch'))
    db = initiate(client)
    print(is_batch)
    if request.method == 'POST':
        if is_batch == 1:
            building_id = listify(request.form['building_id'])
            time = listify(request.form['time'],'datetime')
            P = listify(request.form['kW'],'float')
            temp = listify(request.form['temperature'],'float')
            humid = listify(request.form['humidity'],'float')
            county = listify(request.form['county'],'string')
            energy_docs= [{"building_id":i, "time":j,"kW":k} for (i,j,k) in zip(building_id, time, P) 
                          if unique_update(db, 'energy', {"building_id":i, "time":j})]
            county_docs= [UpdateOne({"building_id":j}, {"$set":{"county_id":i, "building_id":j}},upsert=True)
                          for (i,j) in zip(county, building_id)]
            weather_docs= [{"county_id":i, "time":j, "tempeature":p, "humidity":q} 
                            for (i,j,p,q) in zip(county, time, temp, humid)
                            if unique_update(db, 'weather', {"county_id":i, "time":j})]
            if len(energy_docs)>0:
                db.energy.insert_many(energy_docs)
            if len(weather_docs)>0:
                db.weather.insert_many(weather_docs)
            if len(county_docs)>0:
                db.county.bulk_write(county_docs)
        else:
            building_id = int(request.form['building_id'])
            time = datetime.strptime(request.form['time'],"%Y-%m-%dT%H:%M:%SZ")
            P = float(request.form['kW'])
            temp = float(request.form['temperature'])
            humid = float(request.form['humidity'])
            county = request.form['county'].strip()
            if unique_update(db, 'energy', {"building_id":building_id, "time":time}):
                db.energy.insert_one({"building_id":building_id,
                                      "time":time,
                                      "kW":P})
            if unique_update(db, 'weather', {"county_id":county, "time":time}):
                db.weather.insert_one({"county_id":county,
                                       "temperature": temp,
                                       "humidity":humid,
                                       "time":time})
            db.county.update_one({"building_id":building_id},
                                 {"$set":{"county_id":county,"building_id":building_id}},
                                 upsert=True)
        # print(building_id,time, P, temp, humid,county)
        return jsonify({"response":"Success"})

@app.route('/historical/csv', methods=['POST'])
def post_historical_file():
    file = request.files['file']
    db = initiate(client)
    filetype = int(request.args.get('file_type'))
    print(file.filename)
    if file.filename !='':
        filepath = app.config['DB_path']+ '/'+file.filename
        if os.path.exists(app.config['DB_path']):
            file.save(filepath)
        else:
            os.makedirs(app.config['DB_path'])
            file.save(filepath)
        if filetype == 0:
            update_energy(db, filepath)
        elif filetype == 1:
            update_county(db, filepath)
        elif filetype == 2:
            update_weather(db, filepath)
        else:
            print("invalid file type")
    return jsonify({"response":"Success"})

@app.route('/cleardb', methods=['DELETE'])
def clear_mongo():
    if request.method == 'DELETE':
        client.drop_database("ComEnergy")
        return jsonify({"response":"database dropped"})

@app.route('/test', methods=['POST'])
def test_file_import():
    if request.method == 'POST':
        db = initiate(client, test=True)
        return jsonify({"response":"Test File Inserted"})
    
app.run(host='0.0.0.0', port=81)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=81)
