from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import urllib2
import json
import pymongo
from pymongo import MongoClient
from django.http import JsonResponse


def arcgis(building_id):
	url = 'http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=1=1&objectIds=%s&outFields=*&outSR=4326&f=geojson' % building_id
	response = urllib2.urlopen(url)
	return json.load(response)

def openMongo():
	client = MongoClient("mongodb://blocpower:h3s.w8^8@ds013916.mlab.com:13916/blocmaps")
	return client['blocmaps']

def index(request):
	template = loader.get_template('nyc.html')
	context = {
		'City': 'NYC',
	}
	return HttpResponse(template.render(context, request))

def building_detail(request):
	bld_id = request.POST['id']
	db = openMongo()
	cursor  = db.nyc.find({"_id": int(bld_id)})
	data = arcgis(bld_id)
	for document in cursor:
		if document['properties'].has_key('ped_energy'):
			data['features'][0]['properties'][u'ped_energy'] = document['properties']['ped_energy']

		if document['properties'].has_key('ecm'):
			data['features'][0]['properties'][u'ecm'] = document['properties']['ecm']
		return JsonResponse(data['features'][0]['properties'])

