import logging
import logging.handlers

from wsgiref.simple_server import make_server


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

welcome = """
<!DOCTYPE html>
<html>
<head>
  <title>OSM Buildings</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <style>
    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
    }

    #map {
      width: 100%;
      height: 100%;
    }

    .control {
      position: absolute;
      left: 0;
      z-index: 1000;
    }

    .control.tilt {
      top: 0;
    }

    .control.rotation {
      top: 45px;
    }

    .control.zoom {
      top: 90px;
    }

    .control.zoom button{
      font-weight: normal;
    }

    .control button {
      width: 30px;
      height: 30px;
      margin: 15px 0 0 15px;
      border: 1px solid #999999;
      background: #ffffff;
      opacity: 0.6;
      border-radius: 5px;
      box-shadow: 0 0 5px #666666;
      font-weight: bold;
      text-align: center;
    }

    .control button:hover {
      opacity: 1;
      cursor: pointer;
    }
    .heatindex{
      position: absolute;
      left: 0;
      top: 150px;
      z-index: 1100;
      margin: 0 15px;
    }
    .temp{
      width: 60px;
      height: 300px;
      position: relative;
      padding: 10px;
      background: linear-gradient(to bottom, 
        hsl(160,100%,50%) 0%,
        hsl(128,100%,50%) 20%,
        hsl(96,100%,50%) 40%,
        hsl(64,100%,50%) 60%,
        hsl(32,100%,50%) 80%,
        hsl(1,100%,50%) 100%);
    }
    .high{
      position: absolute;
      top: 5px;
    }
    .low{
      position: absolute;
      bottom: 5px;
    }
  </style>
  <link rel="stylesheet" href="dist/OSMBuildings/OSMBuildings.css">
  <script src="src/color2color.min.js"></script>
  <script src="test/loader.js"></script>
</head>

<body>
<!--<div id="map" style="position:absolute;top:100px"></div>-->
<div id="map"></div>

<div id="label" style="width:10px;height:10px;position:absolute;z-Index:1000;border:3px solid red;"></div>



<div class="control tilt">
  <button class="dec">&#8601;</button>
  <button class="inc">&#8599;</button>
</div>

<div class="control rotation">
  <button class="inc">&#8630;</button>
  <button class="dec">&#8631;</button>
</div>

<div class="control zoom">
  <button class="dec">-</button>
  <button class="inc">+</button>
</div>

<div class="heatindex">
  <div class="temp">
    <div class="high">300000</div>
    <div class="low">20000</div>
  </div>
</div>

<script>
  // SET temperature //

  // START map //
  var map = new GLMap('map', {
    position: { latitude:40.69924, longitude:-74.01692 },
    //bounds: { n:52.52050, e:13.41050, s:52.52000, w:13.41000 },
    zoom: 16,
    minZoom: 12,
    maxZoom: 20,
    // disabled: true, // disables user input
    state: true // stores map position, zoom etc. in url
  });

  //***************************************************************************

  var osmb = new OSMBuildings({
    baseURL: './OSMBuildings',
    minZoom: 12,
    maxZoom: 22,
    showBackfaces: false, 
    fastMode: true,
    effects: ['shadows'],
    attribution: '© 3D <a href="https://osmbuildings.org/copyright/">OSM Buildings</a>'
  }).addTo(map);

  osmb.addMapTiles(
    'https://{s}.tiles.mapbox.com/v3/osmbuildings.kbpalbpk/{z}/{x}/{y}.png',
    {
      attribution: '© Data <a href="http://openstreetmap.org/copyright/">OpenStreetMap</a> · © Map <a href="http://mapbox.com">Mapbox</a>'
    }
  );

  var selector = function(id, data) {
    return id % 2 === 0;
  };

  function showEven(duration) {
    osmb.show(selector, duration || 1000);
  }

  function hideEven(duration) {
    osmb.hide(selector, duration || 1000);
  }

  var colorByHeightAvailable = function(id, properties) {
    if (!properties.levels && !properties.height) {
      properties.color = "red";
    } else if (!properties.height) {
      properties.color = "lime";
    } else {
      properties.color = "green";
    }
    
    properties.roofColor = properties.color;
  };

  var colorByHeight = function(id, properties) {
    var height = parseFloat(properties.height) || (parseFloat(properties.levels)* 3.5) || 0;

    if (height < 20)
      properties.color = "#CCCCCC";
    else if (height < 30)
      properties.color = "purple";
    else if (height < 60)
      properties.color = "#CC4444";
    else 
      properties.color = "orange";
      
    properties.roofColor = properties.color;
  };

  var mapSetup = function(id, properties) {
    //age = 2016-parseFloat(properties.YearBuilt);
    var ped = Math.ceil(parseFloat(properties.ped_energy));
    var min = 20000;
    var max = 300000;
    var percentage = (ped - min) / (max - min);
    var h = Math.ceil( (1.0 - percentage) * 150 );
    properties.height = parseFloat(properties.NumFloors )* 3.5;

    if(isNaN(h)){
      var color = "#CCC";
    } else {
      var color = color2color( "hsl("+h+",100%,50%)" );
    }
    properties.color = color
    //console.log(properties.color)
    properties.roofColor = properties.color;
  };
  
  // osmb.addGeoJSONTiles('https://{s}.data.osmbuildings.org/0.2/anonymous/tile/{z}/{x}/{y}.json',{
  //   modifier: colorByHeight,
  //   color: '#CCCCCC'
  // });


  osmb.addGeoJSONTiles('test/data/osm_ped.json', {modifier: mapSetup});

  //var obj = osmb.addOBJ('../../OBJ2GeoJSON/data/2015-09/o4/o4-nach90.obj', { latitude:52.51941, longitude:13.50445 }, { color: '#00ccff' });
  //osmb.addGeoJSON('../../OBJ2GeoJSON/data/geojson C/o2-nach90.geo.json', { color: '#00ccff' });

  var label = document.getElementById('label');
//  map.on('change', function() {
//    var pos = osmb.project(52.52, 13.37, 50);
//    label.style.left = Math.round(pos.x) + 'px';
//    label.style.top = Math.round(pos.y) + 'px';
//  });

  map.on('pointermove', function(e) {
    osmb.getTarget(e.detail.x, e.detail.y, function(id) {
      if (id) {
        document.body.style.cursor = 'pointer';
        osmb.highlight(id, '#f08000');
      } else {
        document.body.style.cursor = 'default';
        osmb.highlight(null);
      }
   });
  });

//  map.on('pointermove', function(e) {
//    obj.position = osmb.unproject(e.detail.x, e.detail.y);
//  });
//

//  map.on('pointerdown', function(e) {
//    var id = osmb.getTarget(e.detail.x, e.detail.y, function(id) {
//      console.log(id);
//    });
//  });

  //*************************************************************************

  //  osmb.on('idle', function() {
  //    console.log('IDLE');
  //  });
  //
  //  osmb.on('busy', function() {
  //    console.log('BUSY');
  //  });

  //*************************************************************************

  /*
   * ## Key codes for object positioning ##
   * Cursor keys: move
   * +/- : scale
   * w/s : elevate
   * a/d : rotate
   *
   * Pressing Alt the same time accelerates
   */
  function positionOnMap(obj) {
    document.addEventListener('keydown', function(e) {
      var transInc = e.altKey ? 0.0002 : 0.00002;
      var scaleInc = e.altKey ? 0.1 : 0.01;
      var rotaInc = e.altKey ? 10 : 1;
      var eleInc = e.altKey ? 10 : 1;

      switch (e.which) {
        case 37: obj.position.longitude -= transInc; break;
        case 39: obj.position.longitude += transInc; break;
        case 38: obj.position.latitude += transInc; break;
        case 40: obj.position.latitude -= transInc; break;
        case 187: obj.scale += scaleInc; break;
        case 189: obj.scale -= scaleInc; break;
        case 65: obj.rotation += rotaInc; break;
        case 68: obj.rotation -= rotaInc; break;
        case 87: obj.elevation += eleInc; break;
        case 83: obj.elevation -= eleInc; break;
        default: return;
      }
      console.log(JSON.stringify({
        position:{
          latitude:parseFloat(obj.position.latitude.toFixed(5)),
          longitude:parseFloat(obj.position.longitude.toFixed(5))
        },
        elevation:parseFloat(obj.elevation.toFixed(2)),
        scale:parseFloat(obj.scale.toFixed(2)),
        rotation:parseInt(obj.rotation, 10)
      }));
    });
  }

  //*************************************************************************

  if (typeof obj !== 'undefined') positionOnMap(obj);

  var controlButtons = document.querySelectorAll('.control button');

  for (var i = 0, il = controlButtons.length; i < il; i++) {
    controlButtons[i].addEventListener('click', function(e) {
      var button = this;
      var parentClassList = button.parentNode.classList;
      var direction = button.classList.contains('inc') ? 1 : -1;
      var increment;
      var property;

      if (parentClassList.contains('tilt')) {
        property = 'Tilt';
        increment = direction*10;
      }
      if (parentClassList.contains('rotation')) {
        property = 'Rotation';
        increment = direction*10;
      }
      if (parentClassList.contains('zoom')) {
        property = 'Zoom';
        increment = direction*1;
      }
      if (property) {
        map['set'+ property](map['get'+ property]()+increment);
      }
    });
  }
</script>
</body>
</html>
"""

def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    if method == 'POST':
        try:
            if path == '/':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size).decode()
                logger.info("Received message: %s" % request_body)
            elif path == '/scheduled':
                logger.info("Received task %s scheduled at %s", environ['HTTP_X_AWS_SQSD_TASKNAME'], environ['HTTP_X_AWS_SQSD_SCHEDULED_AT'])
        except (TypeError, ValueError):
            logger.warning('Error retrieving request body for async work.')
        response = ''
    else:
        response = welcome
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    return [response]


if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
