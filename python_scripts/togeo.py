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

with open('../backup/rochester.geojson') as tile_template:
	geo_data = json.load(tile_template)
print len(geo_data["features"])

with open('../backup/rochester_geo.json') as tile_template:
	tile_data = json.load(tile_template)
print len(tile_data["features"])

total = len(tile_data["features"])
recordcount = 0

for item in range(0,total):
	building = tile_data['features'][item]
	_id = building['_id'] - 1
	offsetA = 6 - len(str(_id))
	offsetB = 5 - len(str(_id))
	geo_idA = "ID_"
	geo_idA += "0"*offsetA+str(_id)
	geo_idB = "ID_"
	geo_idB += "0"*offsetB+str(_id)
	if building['tile_x'] == 0:
		recordcount += 1
		print str(recordcount)
	 	for geo in geo_data['features']:
			if geo['id'] == geo_idA or  geo['id'] == geo_idB:

				print str(recordcount) +"|"+geo['id']

				if geo['geometry']['type'] == 'GeometryCollection':
					lon = geo['geometry']['geometries'][0]['coordinates'][0][0][0]
					lat = geo['geometry']['geometries'][0]['coordinates'][0][0][1]
				else:
					lon = geo['geometry']['coordinates'][0][0][0]
					lat = geo['geometry']['coordinates'][0][0][1]

				if (isinstance(lon, list)):
					lat = lon[1]
					lon = lon [0]

				building['tile_x'] = long2tile(lon)
				building['tile_y'] = lat2tile(lat)
				building['geometry'] = geo['geometry']
				print building['tile_x']
				break


#"ID_035402"
#with open('../backup/rochester_geo.json', 'w') as outfile:
#	json.dump(tile_data, outfile)
