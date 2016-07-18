import urllib2
import json
from pandas.io.json import json_normalize

offset = 0

def scraper(offset):
	url = "http://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=LandUse%%3D5+AND+YearBuilt%%21%%3D0+AND+XCoord%%21%%3D0&outFields=*&resultOffset=%d&resultRecordCount=2000&outSR=4326&f=geojson" % offset

	response = urllib2.urlopen(url)
	data = json.load(response)

	print len(data['features'])
	if len(data['features']) >= 1:
		with open('data/landuse.json') as data_file:    
			cur_data = json.load(data_file)
			cur_data['features'].append(data['features'])

		with open('data/landuse.json', 'w') as outfile:
			json.dump(cur_data, outfile)

		offset = offset+2000
		print offset
		scraper(offset)
	if len(data['features']) == 0:
		with open('data/landuse.json') as data_file:
			data = json.load(data_file)
			print len(data['features'])

			with open('data/landuse_05.json') as data_file
				cur_data = json.load(data_file)
				for group in data['features']: 
					for prop in group:
						cur_data['features'].append(prop)

				with open('data/landuse_05.json', 'w') as outfile:
					json.dump(cur_data, outfile)

scraper(offset)