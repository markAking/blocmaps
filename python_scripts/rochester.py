import urllib2
from dbfread import DBF
import json
from pandas.io.json import json_normalize
import sys, os
import math
from math import pi,cos,sin,log,exp,atan
import shutil

zoom = 15
tile_size = 256
#Initial Extent: [-8647542.47, 5333848.22] - [-8630955.64, 5343804.14]
#43.269045, -77.701632, 43.269045, -77.701632
#North Latitude: 43.267614 South Latitude: 43.103318 East Longitude: -77.531374 West Longitude: -77.701632
#WSEN
#bbox=(-74.255735,43.103318,-73.700272,43.267614)
#NESW
bbox=(43.267614,-77.531374,43.103318,-77.701632)
DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi
building = {};

def long2tile(lon):
	return int((lon+180)/360*math.pow(2,zoom))

def lat2tile(lat):
	return int((1-math.log(math.tan(lat*math.pi/180) + 1/math.cos(lat*math.pi/180))/math.pi)/2 *math.pow(2,zoom))

def scraper(sbl):
	url = "http://maps.cityofrochester.gov/arcgis/rest/services/App_PropertyInformation/ROC_Parcel_Query_SDE/MapServer/0/query?where=PARCELID%%3D%%27%s%%27&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&outFields=OBJECTID&returnGeometry=true&returnTrueCurves=false&f=pjson" % sbl
	#print url
	response = urllib2.urlopen(url)
	return json.load(response)

#with open('../data/tile.json') as tile_template:
with open('../backup/rochester.json') as tile_template:
	tile_data = json.load(tile_template)

recordcount = 0
for record in DBF('../data/pluto/rochester.dbf'):
	if recordcount > 64000:
		sbl = record['SBL20']
		data = scraper(sbl)
		if len(data['features']) >= 1:
			_id = data['features'][0]['attributes']['OBJECTID']

			feature = {
				"_id": _id,
				"tile_x":0,
				"tile_y":0,
				"type":"Feature",
				"geometry":{},
				"properties": {
					"PARCELID": record['SBL20'],
					"OBJECTID": _id,
					"NumFloors": record['STORIES'],
					"age": record['YEARBUILT'],
					"sqft": record['SQFT']
				}
			}
			tile_data['features'].append(feature)
			if recordcount % 1000 == 0:
				with open('../backup/rochester.json', 'w') as outfile:
					json.dump(tile_data, outfile)

			print record['SBL20']+"|"+str(recordcount)+"|"+ str(_id)

	recordcount=recordcount+1
	
	
with open('../backup/rochester.json', 'w') as outfile:
	json.dump(tile_data, outfile)
#SBL20
#04628000010050120000
#PARCELID
#http://maps.cityofrochester.gov/arcgis/rest/services/App_PropertyInformation/ROC_Parcel_Query_SDE/MapServer/0/query?where=PARCELID%3D%2704628000010050120000%27&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=OBJECTID&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=10&f=pjson
#http://maps.cityofrochester.gov/arcgis/rest/services/App_PropertyInformation/ROC_Parcel_Query_SDE/MapServer/0/query?where=PARCELID%3D%2704628000010050120000%27&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&outFields=OBJECTID&returnGeometry=true&returnTrueCurves=true&f=pjson
