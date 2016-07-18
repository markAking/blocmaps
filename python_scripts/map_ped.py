import pandas as pd
from sklearn import svm
from sklearn.cross_validation import train_test_split
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
import math

df = pd.read_csv('../data/BlocPower Energy Efficiency Assessment Data.csv')
dfHDD = pd.read_csv('../data/HDD-Features.csv')

dfD = df.drop_duplicates(subset='Unnamed: 0') 
# get features names as a list
colnames = dfD[['Unnamed: 0']]['Unnamed: 0'].tolist()
# get the rest of the matrix and transpose
tr = np.asarray(dfD[dfD.columns[1:3000]].transpose())
# construct a dataframe with rows as buildings and columns as features
dfnew = pd.DataFrame(tr, columns=colnames)
df2 = dfnew
y = df2['UTSUM_Electricity_Usage']

import re

yhat = []
for v in y:
    try:
        lnum = re.findall('\d+', v)
        if (len(lnum)==2):
            num = float(lnum[0]+lnum[1])
        else:
            num = float(lnum[0])
        yhat.append(num)
    except:
        yhat.append(v)

energy = np.asarray(yhat)
#energy
x = df2['INFO_Year of Construction']

x1=[]
for v in x:
    try:
        num = 2016.0 - float(v)
        x1.append(num)
    except:
        x1.append(np.nan)


age = np.asarray(x1)
#age
x = df2['INFO_Number of Stories']

x1 = []
for v in x:
    x1.append(float(v))


num_stories = np.asarray(x1)
#num_stories

x = df2['INFO_Total Square Feet'] 

x1 = []
for v in x:
    va = float(v.replace(',',''))
    if (va==0):
        x1.append(np.nan)
    else:
        x1.append(va)

sq_feet = np.asarray(x1) 
#sq_feet

x = df2['INFO_Conditioned Square Feet'] 

x1 = []
for v in x:
    va = float(v.replace(',',''))
    if (va==0):
        x1.append(np.nan)
    else:
        x1.append(va)

sq_feet_c = np.asarray(x1) # using log(sq_feet)
#sq_feet_c

x = df2['INFO_Type of Facility']

x1=[]
for v in x:
    vv = 1.0 if v == 'Worship Facility' else 0.0
    x1.append(vv)   
worship_facility = np.asarray(x1)

x1=[]
for v in x:
    v.replace('M ixed Use','Mixed Use')
    vv = 1.0 if v == 'Mixed Use' else 0.0
    x1.append(vv)   
mixed_use_facility = np.asarray(x1)

x1=[]
for v in x:
    vv = 1.0 if v == 'Office' else 0.0
    x1.append(vv)   
office_facility = np.asarray(x1)

#worship_facility
x = df2['PLEI_1_Quantity']

x1=[]
for v in x:
    try:
        vv = int(v)
    except:
        vv = v
    x1.append(vv)

plei_1 = np.asarray(x1)
#plei_1
x = df2['PLEI_2_Quantity']

x1=[]
for v in x:
    try:
        vv = int(v)
    except:
        vv = v
    x1.append(vv)

plei_2 = np.asarray(x1) 
#plei_2
x = df2['PLEI_3_Quantity']

x1=[]
for v in x:
    try:
        vv = float(v)
    except:
        vv = np.nan
    x1.append(vv)

plei_3 = np.asarray(x1) 
#plei_3


x = df2['PLEI_4_Quantity']

x1=[]
for v in x:
    try:
        vv = float(v)
    except:
        vv = np.nan
    x1.append(vv)

plei_4 = np.asarray(x1) 
#plei_4

x = df2['PLEI_5_Quantity']

x1=[]
for v in x:
    try:
        vv = float(v)
    except:
        vv = np.nan
    x1.append(vv)

plei_5 = np.asarray(x1) 
#plei_5
x = df2['ECMCER_1_Annual Electric Savings(kWh)']

x1=[]
for v in x:
    x1.append(float(str(v).replace(',','')))

savings = np.asarray(x1)
#savings

domestic_gas = np.asarray(dfHDD['domestic_gas'])
heating_gas = np.asarray(dfHDD['heating_gas'])

mm = np.matrix([energy,age,num_stories,sq_feet,
                worship_facility,mixed_use_facility,office_facility,
                plei_1,plei_2,plei_3,plei_4,plei_5,domestic_gas])

mm = np.matrix([energy,age,num_stories,sq_feet,
                plei_1+plei_3,domestic_gas,heating_gas])

matrix = np.transpose(mm) 

# build feature matrix
feat = pd.DataFrame(data=matrix)
featMax = feat.max()

# fill missing values with average
feat = feat.fillna(feat.mean())

X=feat.iloc[:,[1,2,3]]
Y=feat.iloc[:,[0]]

from sklearn import linear_model
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split

#data=pd.read_csv("../data/pluto/BK.csv",low_memory=False)
#data=pd.read_csv("../data/pluto/BX.csv",low_memory=False)
#data=pd.read_csv("../data/pluto/MN.csv",low_memory=False)
#data=pd.read_csv("../data/pluto/QN.csv",low_memory=False)
data=pd.read_csv("../data/pluto/SI.csv",low_memory=False)
#data=pd.concat((data_1,data_2,data_3,data_4,data_5),axis=0)
data.head()
data_pred=data.loc[:,["LandUse","LotArea",'YearBuilt','NumFloors','XCoord','YCoord']]
data_pred=data_pred.dropna()
data_pred=data_pred[data_pred.YearBuilt!=0]
data_pred.index=range(len(data_pred))
data_pred.loc[:,"age"]=data_pred.YearBuilt.apply(lambda x:2016-x)
data_pred.columns

dd=data_pred.loc[:,["LandUse","age","NumFloors","LotArea","XCoord","YCoord"]]
ddd=dd[dd.LandUse==5]
ddd.index=range(len(ddd))

X_feature=ddd.loc[:,["age","NumFloors","LotArea"]]
lm=linear_model.LinearRegression()
lm.fit(X,Y)
ddd.loc[:,"ped_energy"]=lm.predict(X_feature)

ddd=ddd[(ddd.ped_energy<300000)&(ddd.ped_energy>20000)]
ddd.index=range(len(ddd))

import urllib2
import sys, os
import json
from pandas.io.json import json_normalize
from pprint import pprint
import pymongo
from pymongo import MongoClient
import math
from math import pi,cos,sin,log,exp,atan

zoom = 15

def long2tile(lon):
	return int((lon+180)/360*math.pow(2,zoom))

def lat2tile(lat):
	return int((1-math.log(math.tan(lat*math.pi/180) + 1/math.cos(lat*math.pi/180))/math.pi)/2 *math.pow(2,zoom))

client = MongoClient("mongodb://blocpower:h3s.w8^8@ds015325.mlab.com:15325/blocmaps")
db = client['blocmaps']

with open('../data/landuse_05.json') as data_file:    
	curdata = json.load(data_file)

	for prop in curdata['features']:
		ped = ddd.loc[(ddd["XCoord"] == prop['properties']['XCoord']) & (ddd["YCoord"] == prop['properties']['YCoord']), "ped_energy"].values
		ped = str(ped).strip('[]')
		if ped:
			print ped
			prop['properties'][u'ped_energy'] = ped

			key = {'_id':prop['id']}
			feature = {
				"properties":prop['properties']
			}
			result = db.nyc.update_one(key, {"$set": feature}, upsert=True)

