'use strict';

var visifrance = (function() {

  var visifrance_app = angular.module('visifrance', []);


  var g_base_uri = '';
  var g_get_api = '';

  var init = function(_base_uri, _get_api) {
    g_base_uri = _base_uri;
    g_get_api = _get_api;
  }

   /*
   * Services
   */
  visifrance_app.factory('visifrance_service', function($http) {
    // Return the service object
    return { 
      get_departements_api: "france-departement.topojson",
      get_departements_stats_api: "departements-stats"
    };
  });

  /*
   * Utility functions that should probably not be here but in some kind of library
   */
  function loader(config) {
    return { 
      start: function() {
        var radius = Math.min(config.width, config.height) / 2;
        var tau = 2 * Math.PI;

        var arc = d3.svg.arc()
                .innerRadius(radius*0.5)
                .outerRadius(radius*0.9)
                .startAngle(0);

        var svg = d3.select(config.container).append("svg")
            .attr("id", config.id)
            .attr("width", config.width)
            .attr("height", config.height)
            // Position the spinner of the svg we are drawing
            .style("position", "absolute")
            .style("top", 0)
            .style("left", 0)
          .append("g")
            .attr("transform", "translate(" + config.width / 2 + "," + config.height / 2 + ")")

        var background = svg.append("path")
                .datum({endAngle: 0.33*tau})
                .style("fill", "#4D4D4D")
                .attr("d", arc)
                .call(spin, 1500)

        function spin(selection, duration) {
            selection.transition()
                .ease("linear")
                .duration(duration)
                .attrTween("transform", function() {
                    return d3.interpolateString("rotate(0)", "rotate(360)");
                });

            setTimeout(function() { spin(selection, duration); }, duration);
        }

        function transitionFunction(path) {
            path.transition()
                .duration(7500)
                .attrTween("stroke-dasharray", tweenDash)
                .each("end", function() { d3.select(this).call(transition); });
        }
      },
      stop: function() {
        d3.select('#' + config.id).remove();
      }
    };
  }

  /*
   * Controllers
   */
  visifrance_app.controller('visifrance_controller', ['$scope', 'visifrance_service', function($scope, visifrance_service) {

    // Display the results
    var display_departements = function($scope, visifrance_service) {
 
      var width = 700,
          height = 700;

      var svg = d3.select("#map").append("svg")
          .attr("width", width)
          .attr("height", height);
      //    .attr("style", "border: solid #000 3px;");

      var myLoader = loader({width: 700, height: 700, container: "#map", id: "loader"});
      // Start the spinner
      myLoader.start();

      d3.json(visifrance_service.get_departements_api, function(error, fra) {
        if (error) return console.error(error);
        // Get the departement borders
        var subunits = topojson.feature(fra, fra.objects['france-departement']);
        // Prepare a merctor projection, centered on the center of france with a good zoom
        var projection = d3.geo.mercator()
                        .center([1.7, 46.9])
                        .scale(3000)
                        .translate([width / 2, height / 2]);

        var path = d3.geo.path().projection(projection);

        d3.json(visifrance_service.get_departements_stats_api, function(error, stats) {
          // Get the value in an array and sort them
          var euro_by_m2 = Object.keys(stats.average_price_per_m_square).map(function(x) { return stats.average_price_per_m_square[x]; }).sort()
          console.log(euro_by_m2);
          // Set up a color scale from green to red using the stats
          var min = Math.min.apply(null, euro_by_m2);
          var max = Math.max.apply(null, euro_by_m2);
          var average = euro_by_m2.reduce(function(a, b) { return a + b; }) / euro_by_m2.length;
          var median = euro_by_m2[euro_by_m2.length / 2];
          var color = d3.scale.pow().exponent(2)
                              .domain([min, median * 1.2, max])
                              .range(['green', 'orange', 'red']);
          // Now display the departements
          svg.selectAll("path")
              .data(subunits.features)
              .enter()
                .append("path")
                .style("fill", function(d) { 
                  return color(stats.average_price_per_m_square[d.id]); 
                })
                .attr("d", path)
                .attr("class", "departement")
                .on("mouseover", function(d) {
                  // Update info box
                  $scope.departement = d.properties.NOM_DEPT;
                  $scope.average_price_per_m_square = stats.average_price_per_m_square[d.id];
                  $scope.nb_appart_vente = stats.number_of_annonces_per_departement[d.id];
                  $scope.show_info = true;
                  $scope.$apply();
                  // Redisplay the map with the selected path on top
                  svg.selectAll("path").sort(function (a, b) { // select the parent and sort the path's
                    if (a.id != d.id) return -1;               // a is not the hovered element, send "a" to the back
                    else return 1;                             // a is the hovered element, bring "a" to the front
                  });
                });
          // When mouse leaves the svg, clear the info
          svg.on("mouseout", function() {
            $scope.show_info = false;
            $scope.$apply();
          });


          // Remove the spinner
          myLoader.stop();
        });
      });
    };

    // Initialize scope items
    $scope.departement = '';
    $scope.average_price_per_m_square = '';
    $scope.nb_appart_vente = '';
    $scope.show_info = false;
    // Display france    
    display_departements($scope, visifrance_service);
  }]);

  return {
    init: init,
  };
}());
    
if (typeof exports != 'undefined'){
  module.exports = visifrance;
}