import urllib2
import json
from pandas.io.json import json_normalize
import sys, os
import math
from math import pi,cos,sin,log,exp,atan
import pymongo
from pymongo import MongoClient

zoom = 15
tile_size = 256
bbox=(-74.2533588736031,40.4989409997375,-73.6994027507486,40.9113726506172)
DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

def minmax (a,b,c):
	a = max(a,b)
	a = min(a,c)
	return a

class GoogleProjection:
	def __init__(self,levels=18):
		self.Bc = []
		self.Cc = []
		self.zc = []
		self.Ac = []
		c = 256
		for d in range(0,levels):
			e = c/2;
			self.Bc.append(c/360.0)
			self.Cc.append(c/(2 * pi))
			self.zc.append((e,e))
			self.Ac.append(c)
			c *= 2
				
	def fromLLtoPixel(self,ll,zoom):
		d = self.zc[zoom]
		e = round(d[0] + ll[0] * self.Bc[zoom])
		f = minmax(sin(DEG_TO_RAD * ll[1]),-0.9999,0.9999)
		g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
		return (e,g)
	 
	def fromPixelToLL(self,px,zoom):
		e = self.zc[zoom]
		f = (px[0] - e[0])/self.Bc[zoom]
		g = (px[1] - e[1])/-self.Cc[zoom]
		h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
		return (f,h)

def long2tile(lon):
	return int((lon+180)/360*math.pow(2,zoom))

def lat2tile(lat):
	return int((1-math.log(math.tan(lat*math.pi/180) + 1/math.cos(lat*math.pi/180))/math.pi)/2 *math.pow(2,zoom))

def render_tiles(maxZoom=20):
	gprj = GoogleProjection(maxZoom+1) 
	zoom = 15
	ll0 = (bbox[0],bbox[3])
	ll1 = (bbox[2],bbox[1])

	px0 = gprj.fromLLtoPixel(ll0,zoom)
	px1 = gprj.fromLLtoPixel(ll1,zoom)
	
	c = 0 
	for x in range(int(px0[0]/256.0),int(px1[0]/256.0)+1):
		if (x < 0) or (x >= 2**zoom):
			continue
		str_x = "%s" % x
		for y in range(int(px0[1]/256.0),int(px1[1]/256.0)+1):
			if (y < 0) or (y >= 2**zoom):
				continue
			str_y = "%s" % y
			c=c+1
	print c


offset = 0
client = MongoClient("mongodb://blocpower:h3s.w8^8@ds015325.mlab.com:15325/blocmaps")
db = client['blocmaps']

def scraper(offset):
	url = "http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=LandUse%%3D1+AND+YearBuilt%%21%%3D0+AND+XCoord%%21%%3D0&outFields=*&resultOffset=%d&resultRecordCount=2000&outSR=4326&f=geojson" % offset

	response = urllib2.urlopen(url)
	data = json.load(response)
	total = len(data['features'])
	print total
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
				"tile_x":long2tile(lon),
				"tile_y":lat2tile(lat),
				"XCoord":building['properties']['XCoord'],
				"YCoord":building['properties']['YCoord'],
				'LandUse':building['properties']['LandUse'],
				"type":"Feature",
				"geometry":building['geometry'],
				"properties":{
					'NumFloors':building['properties']['NumFloors'],
					'LandUse':building['properties']['LandUse'],
					'OBJECTID':building['properties']['OBJECTID'],
				}
			}
			result = db.nyc.update_one(key, {"$set": feature}, upsert=True)

		offset = offset+2000
		print offset
		scraper(offset)

scraper(offset)