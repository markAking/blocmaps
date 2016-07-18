import json
import sys, os
import pymongo
from pymongo import MongoClient

import cherrypy
import webbrowser

cherrypy.config.update({'server.socket_host': 'blocmaps','server.socket_port': 80, })

def openMongo():
	client = MongoClient("mongodb://blocpower:h3s.w8^8@ds015325.mlab.com:15325/blocmaps")
	return client['blocmaps']

class Root(object):
	@cherrypy.expose
	def index(self, lat=None, lon=None, tilt=None, zoom=None, rotation=None ):
		return open(os.path.join(current_dir, u'index.html'))

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
	webapp.building_detail = Building_Detail()
	cherrypy.quickstart(webapp, '/', config=conf)
