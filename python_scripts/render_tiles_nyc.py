import json
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

client = MongoClient("mongodb://blocpower:h3s.w8^8@ds013916.mlab.com:13916/blocmaps")
db = client['blocmaps']

def render_tiles(maxZoom=20):
	gprj = GoogleProjection(maxZoom+1) 
	ll0 = (bbox[0],bbox[3])
	ll1 = (bbox[2],bbox[1])

	px0 = gprj.fromLLtoPixel(ll0,zoom)
	px1 = gprj.fromLLtoPixel(ll1,zoom)
	
	if not os.path.isdir('../static/tile'):
		os.mkdir('../static/tile')
	if not os.path.isdir('../static/tile/15'):
		os.mkdir('../static/tile/15')

	for x in range(int(px0[0]/256.0),int(px1[0]/256.0)+1):
		if (x < 0) or (x >= 2**zoom):
			continue
		tile_x = "%s" % x

		if not os.path.isdir('../static/tile/15/' + tile_x):
			os.mkdir('../static/tile/15/' + tile_x)

		for y in range(int(px0[1]/256.0),int(px1[1]/256.0)+1):
			if (y < 0) or (y >= 2**zoom):
				continue
			tile_y = "%s" % y

			records = db.nyc.count({"tile_x": x, "tile_y": y})
			if records > 1:
				print records
				with open('../data/tile.json') as tile_template:
					tile_data = json.load(tile_template)

				tiles = db.nyc.find({"tile_x": x, "tile_y": y})
			
				for tile in tiles:
					tile[u'id']=tile['_id']
					tile_data['features'].append(tile)

				with open('../static/tile/15/'+ tile_x + '/' + tile_y + '.json', 'w') as outfile:
					json.dump(tile_data, outfile)
				print tile_y

render_tiles()