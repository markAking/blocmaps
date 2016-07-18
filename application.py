import sys, os
sys.stdout = sys.stderr

import logging
import logging.handlers

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

def openMongo():
	client = MongoClient("mongodb://blocpower:h3s.w8^8@ds015325.mlab.com:15325/blocmaps")
	return client['blocmaps']

class Root(object):
	def index(self, lat=None, lon=None, tilt=None, zoom=None, rotation=None ):
		return open(os.path.join(current_dir, u'index.html'))
	index.exposed = True
	
class Building_Detail(object):
	exposed = True
	@cherrypy.tools.accept(media='text/plain')
	def GET(self, lat, lon, tilt, zoom):
		return building_id

	def POST(self, id=0):
		db = openMongo()
		cursor  = db.nyc.find({"_id": int(id)})
		for document in cursor:
			return json.dumps(document['properties'])

webapp = Root()
webapp.building_detail = Building_Detail()
application = cherrypy.Application(webapp, script_name=None, config=conf)
#logger.warning