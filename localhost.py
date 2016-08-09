import urllib2
import json
import sys, os
import pymongo
from pymongo import MongoClient

import cherrypy
import webbrowser

cherrypy.config.update({'server.socket_host': 'blocmaps','server.socket_port': 80, })

def arcgis(building_id):
	url = 'http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=1=1&objectIds=%s&outFields=*&outSR=4326&f=geojson' % building_id
	response = urllib2.urlopen(url)
	return json.load(response)

def arcgis_rochester(building_id):
	url = 'http://maps.cityofrochester.gov/arcgis/rest/services/App_PropertyInformation/ROC_Parcel_Query_SDE/MapServer/0/query??where=1=1&objectIds=%s&outFields=*&f=pjson' % building_id
	response = urllib2.urlopen(url)
	return json.load(response)

def openMongo():
	client = MongoClient("mongodb://blocpower:h3s.w8^8@ds015325.mlab.com:15325/blocmaps")
	return client['blocmaps']

class Root(object):
	@cherrypy.expose
	def index(self, lat=None, lon=None, tilt=None, zoom=None, rotation=None ):
		return open(os.path.join(current_dir, u'index.html'))

class Rochester(object):
	@cherrypy.expose
	def index(self, lat=None, lon=None, tilt=None, zoom=None, rotation=None ):
		return open(os.path.join(current_dir, u'rochester.html'))

class Building_Detail(object):
	exposed = True
	@cherrypy.tools.accept(media='text/plain')
	def GET(self, lat, lon, tilt, zoom):
		return building_id

	def POST(self, id=0):
		db = openMongo()
		cursor  = db.nyc.find({"_id": int(id)})
		data = arcgis(id)
		for document in cursor:
			if document['properties'].has_key('ped_energy'):
				data['features'][0]['properties'][u'ped_energy'] = document['properties']['ped_energy']
			return json.dumps(data['features'][0]['properties'])

class Rochester_Detail(object):
	exposed = True
	@cherrypy.tools.accept(media='text/plain')
	def GET(self, lat, lon, tilt, zoom):
		return building_id

	def POST(self, id=0):
		data = arcgis_rochester(id)
		return json.dumps(data['features'][0]['attributes'])
     
if __name__ == '__main__':
	current_dir = os.path.abspath(os.path.dirname(__file__))
	conf = {
		'/': {
			"request.dispatch": cherrypy.dispatch.VirtualHost(**{"blocmaps:80": "/"})
		},
		'/building_detail': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'application/json')],
		},
		'/rochester_detail': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'application/json')],
		},
		'/styles': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': os.path.join(current_dir, 'styles')
		},
		'/src': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': os.path.join(current_dir, 'src')
		},
		'/tile': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': os.path.join(current_dir, 'tile')
		},
	}
	webapp = Root()
	webapp.rochester = Rochester()
	webapp.building_detail = Building_Detail()
	webapp.rochester_detail = Rochester_Detail()
	cherrypy.quickstart(webapp, '/', config=conf)
