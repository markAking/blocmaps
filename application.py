import sys, os
sys.stdout = sys.stderr

import logging
import logging.handlers
import urllib2
import json
import pymongo
from pymongo import MongoClient

import atexit
import threading
import cherrypy

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/opt/python/log/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
		cherrypy.engine.start(blocking=False)
		atexit.register(cherrypy.engine.stop)

current_dir = os.path.abspath(os.path.dirname(__file__))
conf = {
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
		'tools.staticdir.dir': os.path.join(current_dir, 'static/styles')
	},
	'/src': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.join(current_dir, 'static/src')
	},
	'/tile': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.join(current_dir, 'static/tile')
	},
}

def arcgis(building_id):
	url = 'http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=1=1&objectIds=%s&outFields=*&outSR=4326&f=geojson' % building_id
	response = urllib2.urlopen(url)
	return json.load(response)

def arcgis_rochester(building_id):
	url = 'http://maps.cityofrochester.gov/arcgis/rest/services/App_PropertyInformation/ROC_Parcel_Query_SDE/MapServer/0/query??where=1=1&objectIds=%s&outFields=*&f=pjson' % building_id
	response = urllib2.urlopen(url)
	return json.load(response)

def openMongo():
	client = MongoClient("mongodb://blocpower:h3s.w8^8@ds013916.mlab.com:13916/blocmaps")
	return client['blocmaps']

class Root(object):
	def index(self, lat=None, lon=None, tilt=None, zoom=None, rotation=None ):
		return open(os.path.join(current_dir, u'index.html'))
	index.exposed = True

class Rochester(object):
	def index(self, lat=None, lon=None, tilt=None, zoom=None, rotation=None ):
		return open(os.path.join(current_dir, u'rochester.html'))
	index.exposed = True

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

			if document['properties'].has_key('ecm'):
				data['features'][0]['properties'][u'ecm'] = document['properties']['ecm']
				
			return json.dumps(data['features'][0]['properties'])

class Rochester_Detail(object):
	exposed = True
	@cherrypy.tools.accept(media='text/plain')
	def GET(self, lat, lon, tilt, zoom):
		return building_id

	def POST(self, id=0):
		data = arcgis_rochester(id)
		return json.dumps(data['features'][0]['attributes'])

webapp = Root()
webapp.rochester = Rochester()
webapp.building_detail = Building_Detail()
webapp.rochester_detail = Rochester_Detail()
application = cherrypy.Application(webapp, script_name=None, config=conf)
#logger.warning