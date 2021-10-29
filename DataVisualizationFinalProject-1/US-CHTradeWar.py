# -*- coding: utf-8 -*-
"""
Created on Tue May 28 20:08:30 2019

@author: Winder
"""
import pandas as pd
import numpy as np
import sqlite3
import csv
from datetime import datetime
from scipy.stats import pearsonr

root="F:\\Data Science\\Homeworks\\1-Visualization Final Project\\"
fileNameInf= "PositiveNegativeIndex.xlsx"
fileNameDJI= "DJI 5 Years.csv"
AllData=pd.ExcelFile(root+fileNameInf)
dataPre = pd.read_excel (AllData,'Pre Events') 
dataWar = pd.read_excel (AllData,'Trade War Events') 
#df = pd.DataFrame(data, columns= [''])

dataDJI=pd.read_csv(root+fileNameDJI)
dataDJIArray=[]
dataInfRef=pd.DataFrame(dataWar,columns=['Date','Influence'])
dataDJIProcess=pd.DataFrame(dataDJI,columns=['Date','Open','Close'])
#print(dataInfRef.loc[1,:])


for date in dataInfRef.loc[:,'Date']:
    for date2 in dataDJIProcess.loc[:,'Date']:
       if date==datetime.strptime(date2,'%Y-%m-%d'):
           idx1=dataDJIProcess.index[dataDJIProcess['Date']==date2]
           value1=(dataDJIProcess.iloc[idx1]['Close']-dataDJIProcess.iloc[idx1]['Open'])/dataDJIProcess.iloc[idx1]['Open']
           idx2=dataInfRef.index[dataInfRef['Date']==date]
           value2=dataInfRef.loc[idx2,'Influence']
           if value1.iloc[0]*value2.iloc[0]>0:
               dataDJIArray.append([date2,value1.iloc[0]])

           
#get the new data DJI with changes           
dataDJINew=pd.DataFrame(np.array(dataDJIArray),columns=['Date','Change'])

#function to extract the required date in csv file and construct with Date and Change
def extractAndConstruct(dataRef,dataInput,comp):
    dataArray=[]
    for date in dataRef.loc[:,'Date']:
        for date2 in dataInput.loc[:,'Date']:
            if date==date2:
                idx1=dataInput.index[dataInput['Date']==date2]
                value1=(dataInput.iloc[idx1]['Close']-dataInput.iloc[idx1]['Open'])/dataInput.iloc[idx1]['Open']
                dataArray.append([comp,date2,value1.iloc[0]])
#    dataNew=pd.DataFrame(np.array(dataArray),columns=['Date','Change'])
    return dataArray

BasicMaterial=["APD","BBL","BHP","DD-PA","DD-PB","DWDP","ECL","LIN","RIO","VALE"]
Energy=["BP","CVX","EC","PBR","PBR-A","PTR","RDS-A","RDS-B","TOT","XOM"]
HealthCare=["ABBV","ABT","JNJ","MDT","MRK","NVO","NVS","PFE","TMO","UNH"]
Utility=["AEP","D","DUK","EXC","NEE","SO","SRE","SRE-PA","NGG","DCUD"]
dataBasicMaterial=[]
dataEnergy=[]
dataHealthCare=[]
dataUtility=[]
for comp in BasicMaterial:
    dataCompExtract=[]
    csvInput=pd.read_csv(root+"Basic Materials\\"+comp+".csv")
    dataComp=pd.DataFrame(csvInput,columns=['Date','Open','Close'])
    dataCompExtract=extractAndConstruct(dataDJINew,dataComp,comp)
    dataBasicMaterial=dataBasicMaterial+dataCompExtract

for comp in Energy:
    dataCompExtract=[]
    csvInput=pd.read_csv(root+"Energy\\"+comp+".csv")
    dataComp=pd.DataFrame(csvInput,columns=['Date','Open','Close'])
    dataCompExtract=extractAndConstruct(dataDJINew,dataComp,comp)
    dataEnergy=dataEnergy+dataCompExtract

for comp in HealthCare:
    dataCompExtract=[]
    csvInput=pd.read_csv(root+"HealthCare\\"+comp+".csv")
    dataComp=pd.DataFrame(csvInput,columns=['Date','Open','Close'])
    dataCompExtract=extractAndConstruct(dataDJINew,dataComp,comp)
    dataHealthCare=dataHealthCare+dataCompExtract

for comp in Utility:
    dataCompExtract=[]
    csvInput=pd.read_csv(root+"Utilities\\"+comp+".csv")
    dataComp=pd.DataFrame(csvInput,columns=['Date','Open','Close'])
    dataCompExtract=extractAndConstruct(dataDJINew,dataComp,comp)
    dataUtility=dataUtility+dataCompExtract
    
dfBasicMaterial=pd.DataFrame(np.array(dataBasicMaterial),columns=['Company','Date','Change'])
dfEnergy=pd.DataFrame(np.array(dataEnergy),columns=['Company','Date','Change'])
dfHealthCare=pd.DataFrame(np.array(dataHealthCare),columns=['Company','Date','Change'])
dfUtility=pd.DataFrame(np.array(dataUtility),columns=['Company','Date','Change'])

# summarize and calculate the average percentage per industry
def avgPerIndustry(dataRef,dataInput):
    avg=[]
    for each in dataRef:
        dfDateChange=dataInput['Change'].loc[dataInput['Date']==each[0]]
        meanDateChange=dfDateChange.apply(pd.to_numeric, args=('coerce',)).mean(axis=0)
        avg.append([each[0],meanDateChange])
    return avg

dataBMOnly=avgPerIndustry(dataDJIArray,dfBasicMaterial)
dataEOnly=avgPerIndustry(dataDJIArray,dfEnergy)
dataHCOnly=avgPerIndustry(dataDJIArray,dfHealthCare)
dataUOnly=avgPerIndustry(dataDJIArray,dfUtility)

# Pearson correlation coefficient
ref=[ row[1] for row in dataDJIArray ]
changeBM=[ row[1] for row in dataBMOnly ]
changeE=[ row[1] for row in dataEOnly]
changeHC=[ row[1] for row in dataHCOnly]
changeU=[ row[1] for row in dataUOnly]
cDJI_BM=pearsonr(ref,changeBM)
cDJI_E=pearsonr(ref,changeE)
cDJI_HC=pearsonr(ref,changeHC)
cDJI_U=pearsonr(ref,changeU)    

dataAllArray={'Industry':['BasicMaterial','Energy','HealthCare','Utility'],
              'Pearson Coefficient':[cDJI_BM[0],cDJI_E[0],cDJI_HC[0],cDJI_U[0]]}
dfAll=pd.DataFrame(dataAllArray)
# based on result, Utility has the weakest correlation with DJI, thus try to find the least correlation company
UtilityIndustryCorrelation=[]
for comp in Utility:
    dataArray=dfUtility['Change'].loc[dfUtility['Company']==comp]
    correlation=pearsonr(ref,dataArray.astype(np.float))
    UtilityIndustryCorrelation.append([comp,correlation[0]])
    
dfUtilityIndustries=pd.DataFrame(np.array(UtilityIndustryCorrelation),columns=['Company','Pearson Coefficient']) 
minPearsonCo=min(dfUtilityIndustries['Pearson Coefficient'].astype(np.float),key=abs)
print(dfUtilityIndustries.loc[dfUtilityIndustries['Pearson Coefficient']==str(minPearsonCo)])

                

    
sqlDB="stocks"
sqlDBPath=root+sqlDB
conn = sqlite3.connect( sqlDBPath )

sqlCreateTable = """ CREATE TABLE DJI(
"Date" datetime,
"Change" float(24)
); 
CREATE TABLE CH_USInfluence(
"Date" datetime,
"Influence" float(24)
); 
CREATE TABLE DJIOriginal(
"Date" datetime,
"Open" float(24),
"Close" float(24)
); 
CREATE TABLE BasicMaterial(
"Company" varchar(255),
"Date" datetime,
"Change" float(24)
);
CREATE TABLE Energy(
"Company" varchar(255),
"Date" datetime,
"Change" float(24)
);
CREATE TABLE HealthCare(
"Company" varchar(255),
"Date" datetime,
"Change" float(24)
);
CREATE TABLE Utility(
"Company" varchar(255),
"Date" datetime,
"Change" float(24)
);
CREATE TABLE Pearson_Industries(
"Industry" varchar(255),
"Pearson Coefficient" float(24)
);
CREATE TABLE Pearson_UtilityCompanies(
"Company" varchar(255),
"Pearson Coefficient" float(24)
);"""

c = conn.cursor()
#c.executescript(sqlCreateTable)
conn.commit()
dataInfRef['Date']=dataInfRef['Date'].astype(np.str)
dataDJIProcess.to_sql( 'DJIOriginal', conn, index = False, if_exists = 'replace')
dataDJINew.to_sql( 'DJI', conn, index = False, if_exists = 'replace')
dataInfRef.to_sql( 'CH_USInfluence', conn, index = False, if_exists = 'replace')
dfBasicMaterial.to_sql( 'BasicMaterial', conn, index = False, if_exists = 'replace')
dfEnergy.to_sql( 'Energy', conn, index = False, if_exists = 'replace')
dfHealthCare.to_sql( 'HealthCare', conn, index = False, if_exists = 'replace')
dfUtility.to_sql( 'Utility', conn, index = False, if_exists = 'replace')
dfUtilityIndustries.to_sql( 'Pearson_UtilityCompanies', conn, index = False, if_exists = 'replace')
dfAll.to_sql( 'Pearson_Industries', conn, index = False, if_exists = 'replace')


