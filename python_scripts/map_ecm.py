import urllib2
import json
import sys, os
import math
from math import pi,cos,sin,log,exp,atan
import pymongo
from pymongo import MongoClient
import pandas as pd


zoom = 15
def long2tile(lon):
	return int((lon+180)/360*math.pow(2,zoom))

def lat2tile(lat):
	return int((1-math.log(math.tan(lat*math.pi/180) + 1/math.cos(lat*math.pi/180))/math.pi)/2 *math.pow(2,zoom))

def getfromPluto(bbl):
	url = "http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=BBL+%%3D+%s&outFields=*&&resultRecordCount=1&outSR=4326&f=geojson" % (bbl)
	response = urllib2.urlopen(url)
	data = json.load(response)
	total = len(data['features'])
	if total >= 1:
		for item in range(0,total):
			building = data['features'][item]
			lon = building['geometry']['coordinates'][0][0][0]
			lat = building['geometry']['coordinates'][0][0][1]

			if (isinstance(lon, list)):
				lat = lon[1]
				lon = lon [0]

			key = {'_id':building['id']}
			feature = {
				"bbl":building['properties']['BBL'],
				"tile_x":long2tile(lon),
				"tile_y":lat2tile(lat),
				"XCoord":building['properties']['XCoord'],
				"YCoord":building['properties']['YCoord'],
				"type":"Feature",
				"geometry":building['geometry'],
				"properties":{
					'NumFloors':building['properties']['NumFloors'],
					'LandUse':building['properties']['LandUse'],
					'OBJECTID':building['properties']['OBJECTID'],
				}
			}
			db.nyc.update_one(key, {"$set": feature}, upsert=True)
			return db.nyc.find_one(key)
	else:
		return False

# ---- Column Keys ----- 
#% of Annual Energy Cost = percent
#Annual ROI after incentives = roi
#Cost
#Description
#Estimated Annual Savings = eas
#Life Cycle Savings after Incentive = lifecycle
#Payback (Years) = payback
#Payback after NYSERDA incentive (Years) = payback_NYSERDA
#Potential NYSERDA incentive = potential_NYSERDA
#SIR after incentive = sir
#Total Annual Gallons of Oil Reduced = oil
#Total Annual Therms Reduced = therms
#Total Annual kWh Reduction = kwh
#Total kW Reduction = kw
#address
#Input.borough
#Input.address
#Answer.bbl
#Answer.x
#Answer.y

data_ecm = pd.read_csv("../data/type_TRC_bbl.csv")
data_ecm.drop(data_ecm.columns[[0]], axis=1, inplace=True)
prev_bbl= 0

client = MongoClient("mongodb://blocpower:h3s.w8^8@ds013916.mlab.com:13916/blocmaps")
db = client['blocmaps']
building = False
ecm = []

for i, row in data_ecm.iterrows():
	BBL = row['Answer.bbl']
	if not math.isnan(BBL):
		BBL = int(BBL)
		if prev_bbl != BBL:
			ecm = []
			# Check our DB first if it does not exist then we pull it from Pluto
			record = db.nyc.count({"XCoord": row['Answer.x'], "YCoord": row['Answer.y']})

			if record >= 1:
				building = db.nyc.find_one({"XCoord": row['Answer.x'], "YCoord": row['Answer.y']})
			else:
				building = getfromPluto(BBL)

		if building:
			key = {'_id':building['_id']}
		else:
			print "Not found"
			print row['address']

		#remove garbage
		del row['address']
		del row['Input.borough']
		del row['Input.address']
		del row['Answer.bbl']
		del row['Answer.x']
		del row['Answer.y']
		ecm_data = row.to_json()

		ecm.append(ecm_data)
		db.nyc.update_one(key, {"$set": {"properties.ecm": ecm}})
		print BBL
	prev_bbl = BBL



