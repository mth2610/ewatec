$(document).ready(function () {
  // using jQuery
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');

  var _getAllFilesFromFolder = function (dir) {

    var filesystem = require("fs");
    var results = [];

    filesystem.readdirSync(dir).forEach(function (file) {

      file = dir + '/' + file;
      var stat = filesystem.statSync(file);

      if (stat && stat.isDirectory()) {
        results = results.concat(_getAllFilesFromFolder(file))
      } else results.push(file);

    });

    return results;

  };


  var longlat = [];


  var stations_source = new ol.source.GeoJSON({
    projection: 'EPSG:4326',
        url: '/api/sites/?format=json',
    // url: '/media/geojson/stations.js',
  });

  //  var stations_source = new ol.source.Vector({
  //    projection: 'EPSG:4326',
  //    url: '/media/geojson/stations.js',
  //    format: new ol.format.GeoJSON()
  //  });

  var stations_style = function () {
    var img = new ol.style.Circle({
      fill: new ol.style.Fill({
        color: 'rgba(250,5,5,1)'
      }),
      radius: 5,
      stroke: new ol.style.Stroke({
        color: 'rgba(250,5,5,1)',
        width: 1,
      })
    });
    var textStroke = new ol.style.Stroke({
      color: '#fff',
      width: 3
    });
    var textFill = new ol.style.Fill({
      color: '#000',
      visible: false,
    });


    //        var text_value = if(($("#Province-label")).is(':checked')){}
    return function (feature, resolution) {
      return [new ol.style.Style({
        image: img,
        text: new ol.style.Text({
          font: '12px Calibri,sans-serif',
          text: (function () {
            if (($("#Station-label")).is(':checked')) {
              return feature.get('name')
            } else {
              return ''
            }
          })(),
          fill: textFill,
          stroke: textStroke,
          labelXOffset: '-10px',
          labelYOffset: '-10px',
        }),
      })];
    };
  };


  var stations_layer = new ol.layer.Vector({
    source: stations_source,
    style: stations_style(),
  });

  // provinces
  var provinces_style = function () {
    var stroke = new ol.style.Stroke({
      color: 'rgba(80,238,247,1)',
      width: 2,
    });
    var textStroke = new ol.style.Stroke({
      color: '#fff',
      width: 3
    });
    var textFill = new ol.style.Fill({
      color: '#000',
      visible: false,
    });
    var fill = new ol.style.Fill({
      color: 'rgba(250,5,5,0)'
    });

    //        var text_value = if(($("#Province-label")).is(':checked')){}
    return function (feature, resolution) {
      return [new ol.style.Style({
        stroke: stroke,
        fill: fill,
        text: new ol.style.Text({
          font: parseInt(5000 / resolution) + 'px Calibri,sans-serif',
          text: (function () {
            if (($("#Province-label")).is(':checked')) {
              return feature.get('province')
            } else {
              return ''
            }
          })(),
          fill: textFill,
          stroke: textStroke,
        }),
      })];
    };
  };

  //  var provinces_source = new ol.source.Vector({
  //    projection: 'EPSG:4326',
  //    url: '/media/geojson/provinces.js',
  //    format: new ol.format.GeoJSON()
  //  });

  var provinces_source = new ol.source.GeoJSON({
    projection: 'EPSG:4326',
    url: '/media/geojson/provinces.js',
  });

  var provinces_layer = new ol.layer.Vector({
    source: provinces_source,
    style: provinces_style(),
    visible: false,
  });

  // landuse
  landuse_color_code = {
    'TSN': 'rgba(170,255,255,1)',
    'TSL': 'rgba(170,255,255,1)',
    'NCS': 'rgba(230,230,200,1)',
    'TSK': 'rgba(250,170,160,1)',
    'SKS': 'rgba(205,170,205,1)',
    'CTS': 'rgba(255,160,170,1)',
    'LNQ': 'rgba(255,215,170,1)',
    'HNK': 'rgba(255,240,180,1)',
    'MVR': 'rgba(180,255,255,1)',
    'TSC': 'rgba(255,170,160,1)',
    'CCC': 'rgba(255,170,160,1)',
    'LUA': 'rgba(255,252,130,1)',
    'COC': 'rgba(230,230,130,1)',
    'LUC': 'rgba(255,252,140,1)',
    'TON': 'rgba(255,170,160,1)',
    'SXN': 'rgba(255,252,110,1)',
    'SKC': 'rgba(250,170,160,1)',
    'DRA': 'rgba(205,170,205,1)',
    'DKH': 'rgba(255,170,160,1)',
    'LUK': 'rgba(255,252,150,1)',
    'LUN': 'rgba(255,252,180,1)',
    'DVH': 'rgba(255,170,160,1)',
    'DBV': 'rgba(255,170,160,1)',
    'CQP': 'rgba(255,100,80,1)',
    'RPT': 'rgba(190,255,30,1)',
    'DGD': 'rgba(255,170,160,1)',
    'DYT': 'rgba(255,170,160,1)',
    'DTL': 'rgba(170,255,255,1)',
    'ODT': 'rgba(255,160,255,1)',
    'LNP': 'rgba(170,255,50,1)',
    'NHK': 'rgba(255,240,180,1)',
    'SON': 'rgba(160,255,255,1)',
    'SKK': 'rgba(250,170,160,1)',
    'LNK': 'rgba(255,215,170,1)',
    'CSD': 'rgba(255,255,254,1)',
    'RPH': 'rgba(190,255,30,1)',
    'RPK': 'rgba(190,255,30,1)',
    'DTT': 'rgba(255,170,160,1)',
    'RPM': 'rgba(190,255,30,1)',
    'DCS': 'rgba(255,255,254,1)',
    'ONT': 'rgba(255,208,255,1)',
    'RPN': 'rgba(190,255,30,1)',
    'RDT': 'rgba(110,255,100,1)',
    'CLN': 'rgba(255,210,160,1)',
    'MVT': 'rgba(180,255,255,1)',
    'DGT': 'rgba(255,170,50,1)',
    'CSK': 'rgba(255,160,170,1)',
    'DNL': 'rgba(255,170,160,1)',
    'DXH': 'rgba(255,170,160,1)',
    'SMN': 'rgba(180,255,255,1)',
    'BHK': 'rgba(255,240,180,1)',
    'CHN': 'rgba(255,252,120,1)',
    'SKX': 'rgba(205,170,205,1)',
    'BCS': 'rgba(255,255,254,1)',
    'RDD': 'rgba(110,255,100,1)',
    'TTN': 'rgba(255,170,160,1)',
    'MVK': 'rgba(180,255,255,1)',
    'RDM': 'rgba(110,255,100,1)',
    'RDN': 'rgba(110,255,100,1)',
    'RDK': 'rgba(110,255,100,1)',
    'TIN': 'rgba(255,170,160,1)',
    'RSM': 'rgba(180,255,180,1)',
    'RSN': 'rgba(180,255,180,1)',
    'CDG': 'rgba(255,160,170,1)',
    'DCH': 'rgba(255,170,160,1)',
    'RSK': 'rgba(180,255,180,1)',
    'NKH': 'rgba(245,255,180,1)',
    'NTS': 'rgba(170,255,255,1)',
    'OTC': 'rgba(255,180,255,1)',
    'MVB': 'rgba(180,255,255,1)',
    'LMU': 'rgba(255,255,254,1)',
    'DDT': 'rgba(255,170,160,1)',
    'PNK': 'rgba(255,170,160,1)',
    'RSX': 'rgba(180,255,180,1)',
    'LNC': 'rgba(255,215,170,1)',
    'PNN': 'rgba(255,255,100,1)',
    'RST': 'rgba(180,255,180,1)',
    'MNC': 'rgba(180,255,255,1)',
    'NNP': 'rgba(255,255,100,1)',
    'NTD': 'rgba(210,210,210,1)',
    'CAN': 'rgba(255,80,70,1)'
  }

  var landuse_style = function () {
    var stroke = new ol.style.Stroke({
      color: 'rgba(0,0,0,1)',
      width: 0.1,
    });
    var textStroke = new ol.style.Stroke({
      color: '#fff',
      width: 3
    });
    var textFill = new ol.style.Fill({
      color: '#000',
      visible: false,
    });


    return function (feature, resolution) {
      return [new ol.style.Style({
        stroke: stroke,
        fill: new ol.style.Fill({
          color: (function () {
            if (landuse_color_code[feature.get('code')]) {
              return landuse_color_code[feature.get('code')]
            } else {
              return 'rgba(1,1,1,1)'
            }
          })()
        }),
        text: new ol.style.Text({
          font: parseInt(30 / resolution) + 'px Calibri,sans-serif',
          text: (function () {
            if (($("#Landuse-label")).is(':checked')) {
              return feature.get('code')
            } else {
              return ''
            }
          })(),
          fill: textFill,
          //                    stroke: textStroke,
        }),
      })];
    };
  };

  //  var landuse_source = new ol.source.GeoJSON({
  //    projection: 'EPSG:4326',
  //    url: '/media/geojson/landuse.js'
  //  });


  //  var landuse_source = new ol.source.Vector({
  //    projection: 'EPSG:4326',
  //    url: '/media/geojson/landuse.js',
  //    format: new ol.format.GeoJSON()
  //  });

  //  var landuse_layer = new ol.layer.Vector({
  //    source: landuse_source,
  //    style: landuse_style(),
  //    visible: false
  //  });
  ///-----------------------------Base layer/-----------------------------
  var baselayers = [
    new ol.layer.Tile({
      style: 'osm',
      source: new ol.source.OSM()
    }),
    new ol.layer.Tile({
      style: 'aerial',
      visible: false,
      source: new ol.source.MapQuest({layer: 'sat'})
    })
    ];
  ///-----------------------------User layer/--------------------------------
  var user = (function () {
    if (document.getElementById("username")) {
      return (document.getElementById("username")).getAttribute("username");
    } else {
      return []
    }
  })();

  var user_layers = [];
    if (document.getElementById("usermaps")) {
        $(".usermap").each(function (index, elem) {
            var layername = elem.getAttribute("id");
            var layername = elem.getAttribute("source_link")
            var usermap_source = new ol.source.GeoJSON({
                projection: 'EPSG:4326',
                url: String(elem.getAttribute("source_link")),
            });

            var usermap_layer = new ol.layer.Vector({
                source: usermap_source,
                visible: true,
            });
            user_layers.push(usermap_layer)

        });
    }



  ///-----------------------------Mouse position/-----------------------------
  var mousePositionControl = new ol.control.MousePosition({
    coordinateFormat: ol.coordinate.createStringXY(4),
    projection: 'EPSG:4326',
    // comment the following two lines to have the mouse position
    // be placed within the map.
    className: 'custom-mouse-position',
    target: document.getElementById('mouse-position'),
    undefinedHTML: '000.0000, 00.0000'
  });

  var scaleline = new ol.control.ScaleLine({
    units: 'degrees'
  })

// -----------------------------------------Zoom to layer-----------------------------------------


$("#zoom2layer").click(function () {
    var min_x = [];
    var min_y = [];
    var max_x = [];
    var max_y = [];
     $(".layers-control:checked").each(function (index, elem) {
         var extent = (eval(elem.getAttribute("source"))).getExtent();
         min_x.push(extent[0]);
         min_y.push(extent[1]);
         max_x.push(extent[2]);
         max_y.push(extent[3]);
     });
    var x_min = Math.min.apply(null, min_x);
    var y_min = Math.min.apply(null, min_y);
    var x_max = Math.max.apply(null, max_x);
    var y_max = Math.max.apply(null, max_y);
    var final_extent = [x_min,y_min,x_max,y_max];
    map.getView().fitExtent(final_extent, map.getSize());

});
// -----------------------------------------------------------------------------------------------
  //-----------------------------Set viet-----------------------------
  var view = new ol.View({
    center: ol.proj.transform([107.0446, 10.6394], 'EPSG:4326', 'EPSG:3857'),
    zoom: 10
  });

  //------------------------------Set map------------------------------
  var map = new ol.Map({
    controls: ol.control.defaults({
      attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
        collapsible: false
      })
    }).extend([mousePositionControl, scaleline]),
    target: document.getElementById('map'),
    layers: (baselayers.concat(user_layers)).concat([
//                landuse_layer,
                provinces_layer,
                stations_layer
                ]),
    view: view
  });

  $('#basemap-select').change(function () {
    var style = $(this).find(':selected').val();
    var i, ii;
    for (i = 0, ii = baselayers.length; i < ii; ++i) {
      baselayers[i].set('visible', (baselayers[i].get('style') == style));
    }
  });

  $('#basemap-select').trigger('change');


  var visible_provinces = new ol.dom.Input(document.getElementById('Province'));
  visible_provinces.bindTo('checked', provinces_layer, 'visible');

  var visible_stations = new ol.dom.Input(document.getElementById('Station'));
  visible_stations.bindTo('checked', stations_layer, 'visible');

  //  var visible_landuse = new ol.dom.Input(document.getElementById('Landuse'));
  //  visible_landuse.bindTo('checked', landuse_layer, 'visible');

  // add drag box


  var select = new ol.interaction.Select();
  map.addInteraction(select);

  var selectedFeatures = select.getFeatures();


  // a DragBox interaction used to select features by drawing boxes
  var dragBox = new ol.interaction.DragBox({
    condition: ol.events.condition.shiftKeyOnly,
    style: new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: [0, 0, 255, 1]
      })
    })
  });
  map.addInteraction(dragBox);


  var infoBox = document.getElementById('info');
  var id = [];
  var name = [];

  dragBox.on('boxend', function (evt) {
    // features that intersect the box are added to the collection of
    // selected features, and their names are displayed in the "info"
    // div

    var info = [];
    var extent = dragBox.getGeometry().extent;

    stations_source.forEachFeatureInExtent(extent, function (feature) {

      selectedFeatures.push(feature);
      info.push(feature.get('name'));
      id.push(feature.get('id'));
      name.push(feature.get('name'));

    });
    if (info.length > 0) {
      infoBox.innerHTML = "Selected Objects: " + String(info.length);
    }
  });


  // clear selection when drawing a new box and when clicking on the map
  dragBox.on('boxstart', function (e) {
    id = [];
    name = [];
    selectedFeatures.clear();
    infoBox.innerHTML = 'Selected Objects: 0';
  });


  map.on('click', function () {
    id = [];
    name = [];
    selectedFeatures.clear();
    infoBox.innerHTML = 'Selected Objects: 0';
  });


  //    var element = document.getElementById('popup');
  //    var popup = new ol.Overlay({
  //      element: element,
  ////      stopEvent: false
  //    });
  //    map.addOverlay(popup);
  //
  //        // display popup on click
  //    map.on('click', function(evt) {
  //
  //      var feature = map.forEachFeatureAtPixel(evt.pixel,
  //          function(feature, layer) {
  //            return feature;
  //          });
  //      if (feature) {
  //        var geometry = feature.getGeometry();
  //        var coord = evt.coordinate;
  //
  //        popup.setPosition(coord);
  //        $(element).popover({
  //          'placement': 'top',
  //          'html': true,
  //          'content': feature.get('name')
  //        });
  //        $(element).popover('show');
  //      } else {
  //        $(element).popover('destroy');
  //      }
  //    });


  // change mouse cursor when over marker
  //    $(map.getViewport()).on('mousemove', function(e) {
  //      var pixel = map.getEventPixel(e.originalEvent);
  //      var hit = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
  //        return true;
  //      });
  //      if (hit) {
  //        map.getTarget().style.cursor = 'pointer';
  //      } else {
  //        map.getTarget().style.cursor = '';
  //      }
  //    });




  //-----------------------------------------Data review-----------------------------------------
  //     send id request to backend

  $("#data-review").click(function () {
    $('#spinner').show();
    $.ajax({
      async:true,
      type: 'POST',
      url: 'data_review',
      data: {
        'id[]': id,
        'name[]': name,
        //                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
      },
    complete: function() {
            $("#spinner").hide();
        },
      success: function (newdata) {
         if(newdata==="/auth/require_login"){
             window.location.href = "/auth/require_login";
         }else{
            var datareview_popup = document.getElementById("allData")
            datareview_popup.innerHTML = newdata;
         };
      },
      error: function () {
        alert("Failed in sending ajax request")
      },
      dataType: 'html',
      headers: {
        'X-CSRFToken': csrftoken
      }

    });

  });

  //-----------------------------------------Download selected data-----------------------------------------
  $("#map-data").click(function (e) {
    var $that = $(e.target);

    if ($that.closest("#Download")[0]) {
      $('#spinner').show();
      var selected_id = [];
      var selected_variable = [];
      var selected_starttime = [];
      var selected_endtime = [];

      $(".ck_download:checked").each(function (index, elem) {
        var arr = elem.id.split("_");
        selected_id.push(String(arr[1]));
        selected_variable.push(String(arr[2]));
        selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
        selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
      });


      $.ajax({
        async:true,
        type: 'POST',
        url: 'data_download',
        data: {
          'selected_id[]': selected_id,
          'selected_variable[]': selected_variable,
          'selected_starttime[]': selected_starttime,
          'selected_endtime[]': selected_endtime
        },
        complete: function() {
            $("#spinner").hide();
        },
        success: function (url) {
            window.location = url;
        },
        error: function () {
            alert('Failed in sending ajax request');
        },
        dataType: 'html',
        headers: {
          'X-CSRFToken': csrftoken
        }
      });
    }
  });


  // -----------------------------------------Graph-----------------------------------------
  $("#map-data").click(function (e) {
    var $that = $(e.target);
    if ($that.closest(".fa-bar-chart")[0]) {
      var str_id = $that.closest(".fa-bar-chart")[0].id;
      split_str_id = str_id.split("_");
      var start_time = document.getElementById(str_id.replace('Graph', 'Starttime')).value;
      var end_time = document.getElementById(str_id.replace('Graph', 'Endtime')).value;
      var id = split_str_id[1];
      var variable = split_str_id[2];

      if(document.getElementById(str_id.replace('Graph', 'Removeoutlier')).checked == true){
          var removeoutlier = "True";
      }else{
          var removeoutlier = "False";
      }

      var newwindow = window.open("statistic_data", "graph");
      newwindow.onload = function(){
      $(newwindow.document.getElementById("spinner")).show();
      };
      $.ajax({
        async:true,
        type: 'POST',
        url: 'show_graph',
        data: {
          'id': id,
          'variable': variable,
          'starttime': start_time,
          'endtime': end_time,
          'removeoutlier': removeoutlier,
        },
        success: function (data) {
            var bd = newwindow.document.body;
            var initial = newwindow.document.getElementById("initial_data_content");
            $(initial).append(data);
            newwindow.document.getElementById("id").value = id;
            newwindow.document.getElementById("variable").value = variable.replace(/-/g," ");
            newwindow.document.getElementById("starttime").value = start_time;
            newwindow.document.getElementById("endtime").value = end_time;
            $(newwindow.document.getElementById("spinner")).hide();
        },
        error: function () {
          alert('Failed in sending ajax request')
        },
        dataType: 'html',
        headers: {
          'X-CSRFToken': csrftoken
        }
      });

    }

  });



  // -----------------------------------------Export png-----------------------------------------
    var exportPNGElement = document.getElementById('export-png');

    if ('download' in exportPNGElement) {
      exportPNGElement.addEventListener('click', function(e) {
        map.once('postcompose', function(event) {
          var canvas = event.context.canvas;
          exportPNGElement.href = canvas.toDataURL('image/png');
        });
        map.renderSync();
      }, false);
    } else {
      var info = document.getElementById('no-download');
      /**
       * display error message
       */
      info.style.display = '';
    }
// -----------------------------------------zoom in, zoom out-----------------------------------------

    $("#zoom_in").on('click', function (){
        var zoom = view.getZoom();
        view.setZoom(zoom+1);
    });

    $("#zoom_out").on('click', function (){
        var zoom = view.getZoom();
        view.setZoom(zoom-1);
    });
  //-----------------------------------------Export to Swat-----------------------------------------

  $("#export2swat").click(function () {
    $('#spinner').show();
    var start_time = document.getElementById("swat_starttime").value;
    var end_time = document.getElementById("swat_endtime").value;

    console.log(start_time);
    console.log(end_time)
    $.ajax({
      async:true,
      type: 'POST',
      url: 'export2swat',
      data: {
        'id[]': id,
        'name[]': name,
        'swat_starttime':start_time,
        'swat_endtime':end_time,
      },
      complete: function() {
            $("#spinner").hide();
        },
      success: function (newdata) {
         if(newdata==="/auth/require_login"){
             window.location.href = "/auth/require_login";
         }else{
            window.location = newdata;
         };
      },
      error: function () {
        alert("Failed in sending ajax request")
      },
      dataType: 'html',
      headers: {
        'X-CSRFToken': csrftoken
      }

    });

  });

  //-----------------------------------------Multiplevariable statistic-----------------------------------------
  $("#map-data").click(function (e) {
      var $that = $(e.target);
      if ($that.closest("#multivariable-statistic")[0]) {

          $('#spinner').show();
            var selected_id = [];
            var selected_sitename = [];
            var selected_variable = [];
            var selected_starttime = [];
            var selected_endtime = [];


          $(".ck_download:checked").each(function (index, elem) {
              var arr = elem.id.split("_");
              selected_id.push(String(arr[1]));
              selected_sitename.push(elem.getAttribute("sitename"));
              selected_variable.push(String(arr[2]));
              selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
              selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
              console.log(selected_sitename);
          });

          var newwindow = window.open("multivariable_statistic");
          newwindow.onload = function(){
          };
          if( selected_id.length >= 2){

          $.ajax({
              async: true,
              type: 'POST',
              url: 'multivariable_statistic',
              data: {
                  'selected_id[]': selected_id,
                  'selected_sitename[]':selected_sitename,
                  'selected_variable[]': selected_variable,
                  'selected_starttime[]': selected_starttime,
                  'selected_endtime[]': selected_endtime
              },
              complete: function () {
                   $("#spinner").hide();
              },
              success: function (data) {
                newwindow.document.open();
                newwindow.document.write(data) ;
                newwindow.document.close();
              },
              error: function () {
                  alert('Failed in sending ajax request');
              },
              dataType: 'html',
              headers: {
                  'X-CSRFToken': csrftoken
              }
          });
        }else{
           alert('Seleted variables have to be >= 2');
        }
  }

  });

  //-----------------------------------------compare with model-----------------------------------------
  $("#map-data").click(function (e) {
      var $that = $(e.target);
      if ($that.closest("#compare-model")[0]) {
          $('#spinner').show();
              var selected_id = [];
              var selected_variable = [];
              var selected_starttime = [];
              var selected_endtime = [];


          $(".ck_download:checked").each(function (index, elem) {
              var arr = elem.id.split("_");
              selected_id.push(String(arr[1]));
              selected_variable.push(String(arr[2]));
              selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
              selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
          });

          if( selected_id.length === 1){
              var newwindow = window.open("upload_model_file");
              newwindow.onload = function(){
          $.ajax({
              async: true,
              type: 'POST',
              url: 'upload_model_file',
              complete: function () {
                  $("#spinner").hide();
              },
              success: function (){
                console.log(selected_id[0])
                newwindow.document.getElementById("id").value = selected_id[0];
                newwindow.document.getElementById("variable").value = selected_variable[0].replace(/-/g," ");
                newwindow.document.getElementById("starttime").value = selected_starttime[0];
                newwindow.document.getElementById("endtime").value = selected_endtime[0];
              },
              error: function () {
                  alert('Failed in sending ajax request');
              },
              dataType: 'html',
              headers: {
                  'X-CSRFToken': csrftoken
              }
          })
         }
          }else{
              $("#spinner").hide();
              alert('Please select extractly one variabe');
          };


      }
  });

//-----------------------------------------generate swat wgn-----------------------------------------
    $("#map-data").click(function (e) {
      var $that = $(e.target);
      if ($that.closest("#swat-wgn")[0]) {

          $('#spinner').show();
            var selected_id = [];
            var selected_variable = [];
            var selected_starttime = [];
            var selected_endtime = [];
            var removeoutlier = [];
          $(".ck_download:checked").each(function (index, elem) {
              var arr = elem.id.split("_");
              selected_id.push(String(arr[1]));
              selected_variable.push(String(arr[2]));
              selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
              selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
              if(document.getElementById(elem.id.replace('Check', 'Removeoutlier')).checked == true){
                    removeoutlier.push("True");
                }else{
                    removeoutlier.push("False");
              }
          });


          $.ajax({
              async: true,
              type: 'POST',
              url: 'generate_swat_wgn',
              data: {
                  'selected_id[]': selected_id,
                  'selected_variable[]': selected_variable,
                  'selected_starttime[]': selected_starttime,
                  'selected_endtime[]': selected_endtime,
                  'removeoutlier[]': removeoutlier
              },
              complete: function () {
                   $("#spinner").hide();
              },
              success: function (url) {
                  window.location = url;
              },
              error: function () {
                  alert('Failed in sending ajax request');
              },
              dataType: 'html',
              headers: {
                  'X-CSRFToken': csrftoken
              }
          });

  }

  });


// -----------------------------------------Delete site-----------------------------------------
    $("#delete_sites").click(function () {
        $('#spinner').show();
            console.log(id);
            console.log(name);

            $.ajax({
              async:true,
              type: 'POST',
              url: '/database/delete_sites',
              data: {
                'id[]': id,
                'name[]': name,
              },
              complete: function() {
                    $("#spinner").hide();
                },
              success: function (newdata) {
                 if(newdata==="/auth/require_login"){
                     window.location.href = "/auth/require_login";
                 }else{
                 };
              },
              error: function () {
                alert("Failed in sending ajax request")
              },
              dataType: 'html',
              headers: {
                'X-CSRFToken': csrftoken
              }

            });

      });
// -----------------------------------------Delete data-----------------------------------------
  $("#map-data").click(function (e) {
      var $that = $(e.target);
      if ($that.closest("#delete-data")[0]) {

          $('#spinner').show();
            var selected_id = [];
            var selected_sitename = [];
            var selected_variable = [];
            var selected_starttime = [];
            var selected_endtime = [];


          $(".ck_download:checked").each(function (index, elem) {
              var arr = elem.id.split("_");
              selected_id.push(String(arr[1]));
              selected_sitename.push(elem.getAttribute("sitename"));
              selected_variable.push(String(arr[2]));
              selected_starttime.push(String(document.getElementById("Starttime_" + arr[1] + "_" + arr[2]).value));
              selected_endtime.push(String(document.getElementById("Endtime_" + arr[1] + "_" + arr[2]).value));
              console.log(selected_sitename);
          });

          $.ajax({
              async: true,
              type: 'POST',
              url: '/database/delete_data',
              data: {
                  'selected_id[]': selected_id,
                  'selected_sitename[]':selected_sitename,
                  'selected_variable[]': selected_variable,
                  'selected_starttime[]': selected_starttime,
                  'selected_endtime[]': selected_endtime
              },
              complete: function () {
                   $("#spinner").hide();
              },
              success: function (data) {
                  alert(data);
              },
              error: function () {
                  alert('Failed in sending ajax request');
              },
              dataType: 'html',
              headers: {
                  'X-CSRFToken': csrftoken
              }
          });

  }

  });


// -----------------------------------------Select data all-----------------------------------------
$("#map-data").click(function () {
    $(".selectAll").click(function () {
    if ($(this).is(':checked')) {
        $('.ck_download').attr('checked', true);
    } else {
        $('.ck_download').attr('checked', false);
    }
 })
});
// -----------------------------------------Track position-----------------------------------------



  var geolocation = new ol.Geolocation({
    projection: view.getProjection()
  });

  function el(id) {
    return document.getElementById(id);
  }

  el('track').addEventListener('click', function () {
    geolocation.setTracking(true);
  });

  // handle geolocation error.
  geolocation.on('error', function (error) {
    var info = document.getElementById('info');
    info.innerHTML = error.message;
    info.style.display = '';
  });

  var accuracyFeature = new ol.Feature();
  geolocation.on('change:accuracyGeometry', function () {
    accuracyFeature.setGeometry(geolocation.getAccuracyGeometry());
  });



  var img = new ol.style.Circle({
    fill: new ol.style.Fill({
      color: 'rgba(250,5,5,1)'
    }),
    radius: 5,
    stroke: new ol.style.Stroke({
      color: 'rgba(250,5,5,1)',
      width: 1,
    })
  });


  var positionFeature = new ol.Feature();
  positionFeature.setStyle(new ol.style.Style({
    image: img,
  }));


      geolocation.on('change:position', function () {
          var coordinates = geolocation.getPosition();
          view.setCenter(coordinates)
          view.setZoom(15)
          positionFeature.setGeometry(coordinates ?
              new ol.geom.Point(coordinates) : null);
      });



  var featuresOverlay = new ol.FeatureOverlay({
    map: map,
    //    features: [accuracyFeature, positionFeature]
    features: [positionFeature]
  });

});
