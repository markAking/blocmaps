var selected_building = false,
    buildings = [];

var pedPercentage = function(ped){
  var min = 20000,
      max = 300000;
  return (ped - min) / (max - min);
};

var pedColors = function(ped, l){
  ped = Math.ceil(parseFloat(ped));
  var h = Math.ceil( (1.0 - pedPercentage(ped)) * 150 );
  if(isNaN(h)){
    return "#CCC";
  } else {
    return color2color( "hsl("+h+",100%,"+l+"%)" );
  }
};

var numberWithCommas = function(x) {
  x = Math.floor(x);
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

/*
 * ## Key codes for object positioning ##
 * Cursor keys: move
 * +/- : scale
 * w/s : elevate
 * a/d : rotate
 *
 * Pressing Alt the same time accelerates
 */
var positionOnMap = function(obj) {
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
};

if (typeof obj !== 'undefined') positionOnMap(obj);