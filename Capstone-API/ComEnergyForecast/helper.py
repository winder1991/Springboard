# -*- coding: utf-8 -*-
"""
Created on Wed May 11 19:19:22 2022

@author: BlueSpark
"""
from datetime import datetime
import csv
from pymongo import UpdateOne, InsertOne
from pymongo import MongoClient

def listify(context, data_type = "int"):
    if ',' in context:
        items = context.split(',')
        items[0] = items[0][1:]
        items[-1] = items[-1][:-1]
        if data_type == "int":
            items = [int(each) for each in items]
        elif data_type =='float':
            items = [float(each) for each in items]
        elif data_type == "datetime":
            items = [datetime.strptime(each, "%Y-%m-%dT%H:%M:%SZ") for each in items]
        else:
            items = [each.strip() for each in items]
    else:
        if data_type == "int":
            items = [int(context[1:-1])]
        elif data_type =='float':
            items = [float(context[1:-1])]
        elif data_type == "datetime":
            items = datetime.strptime(context[1:-1], "%Y-%m-%dT%H:%M:%SZ")
        else:
            items = [context[1:-1]]
    return items

def update_county(db, csv_file_path):
    # print("start")
    with open(csv_file_path, 'r') as file:
        csvreader = csv.reader(file)
        cols = next(csvreader)
        cols = [each.strip() for each in cols]
        lines = []
        if ('building_id' in cols) and ('county' in cols):
            building_id_index = cols.index('building_id')
            county_index = cols.index('county')
            for line in csvreader:
                # print("building_id:",line[building_id_index],"county_id:",line[county_index])
                if len(line)>0:
                    lines.append(UpdateOne({"building_id":int(line[building_id_index])},
                                           {"$set":{"county_id":line[county_index]}},
                                           upsert=True
                                           ))
            if len(lines)>0:
                db.county.bulk_write(lines)
            else:
                print("File Empty or All records are dupliactes in the file compare to data in database")
        else:
            print("Write Failed: Please make sure the columns name have 'building_id' and 'county'")

def update_energy(db, csv_file_path):
    # print("start")
    with open(csv_file_path, 'r') as file:
        csvreader = csv.reader(file)
        cols = next(csvreader)
        cols = [each.strip() for each in cols]
        lines = []
        if ('building_id' in cols) and ('time' in cols) and ('kW' in cols):
            building_id_index = cols.index('building_id')
            time_index = cols.index('time')
            kW_index =cols.index('kW')
            # print(building_id_index, time_index, kW_index)
            for line in csvreader:
                # print("building_id:",line[building_id_index],"county_id:",line[county_index])
                if len(line)>0:
                    building_id = int(line[building_id_index])
                    time = datetime.strptime(line[time_index], "%Y-%m-%dT%H:%M:%SZ")
                    if unique_update(db, 'energy', {"time":time,"building_id":building_id}):
                        lines.append(InsertOne({"time":time,"building_id":building_id,"kW": float(line[kW_index])}))
            if len(lines)>0:
                db.energy.bulk_write(lines)
            else:
                print("File Empty or All records are dupliactes in the file compare to data in database")
        else:
            print("Write Failed: Please make sure the columns name have 'building_id', 'time' and 'kW'")

def update_weather(db, csv_file_path):
    # print("start")
    with open(csv_file_path, 'r') as file:
        csvreader = csv.reader(file)
        cols = next(csvreader)
        cols = [each.strip() for each in cols]
        lines = []
        if ('county' in cols) and ('time' in cols) and ('temperature' in cols) and ('humidity' in cols):
            county_id_index = cols.index('county')
            time_index = cols.index('time')
            temp_index =cols.index('temperature')
            humid_index = cols.index('humidity')
            for line in csvreader:
                # print("building_id:",line[building_id_index],"county_id:",line[county_index])
                if len(line)>0:
                    county_id = line[county_id_index]
                    time = datetime.strptime(line[time_index], "%Y-%m-%dT%H:%M:%SZ")
                    temp = float(line[temp_index])
                    humid = float(line[humid_index])
                    if unique_update(db, 'weather', {"time":time,"county_id":county_id}):
                        lines.append(InsertOne({"time":time,"county_id":county_id,"temperature": temp, "humidity": humid}))
            if len(lines)>0:
                db.weather.bulk_write(lines)
            else:
                print("File Empty or All records are dupliactes in the file compare to data in database")
        else:
            print("Write Failed: Please make sure the columns name have 'county', 'time', 'temperature' and 'humidity'")

def unique_update(db,collection,query):
    if len(list(db[collection].find(query)))>0:
        flag = False
    else:
        flag = True
    return flag
    

if __name__=='__main__':
    test1 = listify("[1,2,3,4]")
    if (test1 == [1,2,3,4]):
        print("Test int pass", test1)
    else:
        print("Test int fail", test1)
    test2 = listify("[12.1,2,-31,0.5]",'float')
    if (test2 == [12.1,2,-31,0.5]):
        print("Test float pass", test2)
    else:
        print("Test float fail", test2)
    test3 = listify('[2022-05-11T12:15:00Z,2022-05-11T12:30:00Z]','datetime')
    if (test3 == [datetime(2022, 5, 11, 12, 15),datetime(2022, 5, 11, 12, 30)]):
        print("Test datetime pass", test3)
    else:
        print("Test datetime fail", test3)
    test4 = listify("[1]")
    if (test4 ==[1]):
        print("Test 1 item pass", test4)
    else:
        print("Test 1 item fail", test4)
    
    
    filepath = r"..\test\county_building.csv"
    client = MongoClient('mongodb://localhost:27081')
    db = client.ComEnergy
    print("File county test1:")
    update_county(db, filepath)
    filepath2 = r"..\test\county_building_errorcolumn.csv"
    print("File county test2:")
    update_county(db, filepath2)
    
    print('Test if found True:')
    time1= datetime.strptime("2022-05-11T12:30:00Z", "%Y-%m-%dT%H:%M:%SZ")
    query = {"time": time1, "county_id":"G123"}
    print(unique_update(db, "weather", query))
    print('Test if found False:')
    time2= datetime.strptime("2022-05-11T12:15:00Z", "%Y-%m-%dT%H:%M:%SZ")
    query2 = {"time": time2, "county_id":"G123"}
    print(unique_update(db, "weather", query2))
    
    filepath3 = r"..\test\building_energy.csv"
    print("File energy test1:")
    update_energy(db, filepath3)
    filepath3 = r"..\test\building_energy_1447.csv"
    print("File energy test2:")
    update_energy(db, filepath3)
    
    filepath4 = r"..\test\county_weather.csv"
    print("File weather test1:")
    update_weather(db, filepath4)