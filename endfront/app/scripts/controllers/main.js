'use strict';

/**
 * @ngdoc function
 * @name interactionsApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the interactionsApp
 */
angular.module('interactionsApp')
  .controller('MainCtrl', function ($scope, $http, $q) {

    var hostname = "";

    $scope.showMedicinalProducts = true;
    $scope.medicalProductsPrefix = '';
    $scope.medicalProducts = [];
    $scope.medicalProductsBuffer = [];
    var medicinalProductsCanceler = $q.defer();
    $scope.$watch('medicalProductsPrefix',function(medicalProductsPrefix){
      console.log('medicalProductsPrefix',medicalProductsPrefix);
      if(!medicalProductsPrefix || medicalProductsPrefix.length < 4 ){ 
        $scope.medicalProductsBuffer = [];
        return;
      }

      medicinalProductsCanceler.resolve;
      medicinalProductsCanceler = $q.defer();
      $http.get(hostname + '/medicinalproducts?startsWith=' + medicalProductsPrefix, {timeout: medicinalProductsCanceler.promise}).then(function(response){
        $scope.medicalProductsBuffer = 
            response.data.drugs.filter(function(s){
              return $scope.medicalProducts.indexOf(s) === -1;
            });

        console.log('response',response.data, $scope.medicalProductsBuffer);
      },function(response){
        //TODO: bootstrap alert dialog
        alert('error fetching response');
      });
    });

    $scope.addMedicalProduct = function(product){
      $scope.medicalProductsPrefix = '';
      $scope.medicalProductsBuffer = [];
      $scope.medicalProducts.push(product);
      $scope.showConditions = $scope.showConditions || $scope.medicalProducts.length >= 2;
      refreshInteraction();
    };

    $scope.removeMedicalProduct = function(product){
      $scope.medicalProducts.splice($scope.medicalProducts.indexOf(product),1);
      refreshInteraction();
    };

    $scope.conditionsPrefix = '';
    $scope.conditions = [];
    $scope.conditionsBuffer = [];
    var conditionsCanceler = $q.defer();

    $scope.$watch('conditionsPrefix',function(conditionsPrefix){
      if(!conditionsPrefix || conditionsPrefix.length < 4 ){
        $scope.conditionsBuffer = [];
        return;
      }

      conditionsCanceler.resolve;
      conditionsCanceler = $q.defer();
      $http.get(hostname + '/preexistingconditions?startsWith=' + conditionsPrefix, {timeout: conditionsCanceler.promise}).then(function(response){
        $scope.conditionsBuffer = response.data.conditions.filter(function(s){
              return $scope.conditions.indexOf(s) === -1;
            });
      },function(response){
        //TODO: bootstrap alert dialog
        alert('error fetching response');
      });
    });

    $scope.addCondition = function(condition){
      $scope.showInteractions = true;
      $scope.conditionsPrefix = '';
      $scope.conditionsBuffer = [];
      $scope.conditions.push(condition);
      refreshInteraction();
    };

    $scope.removeCondition = function(condition){
      $scope.conditions.splice($scope.medicalProducts.indexOf(condition),1);
      refreshInteraction();
    };

    $scope.interactions = [];
    //$scope.$watchCollection('[medicalProductsPrefix,conditionsPrefix]',refreshInteraction);
    function refreshInteraction(){
      if(!$scope.medicalProducts.length ||
            $scope.medicalProducts.length < 2 ||
            !$scope.conditions.length){
        $scope.interactions = [];
        $scope.interactionScore = null;
        $scope.showNoResultsFound = false;
        return;
      }

      $http.get(hostname + '/interactions?' + 
                    'medicinalproducts=' + 
                      $scope.medicalProducts.join(',') + '&' +
                    'preexistingconditions=' + 
                    $scope.conditions.join(',')).then(function(response){
        
        if(!response.data.results || response.data.results.length !== 2){
          alert('Unexpected result from server');
          return;
        }
        $scope.interactionScore = response.data.results[0].filter(function(o){return o.AE === 'Interaction'})[0].score;
        $scope.formattedInteractionScore = Math.round($scope.interactionScore * 100);
        $scope.showNoResultsFound = response.data.results[1].length === 0;
        $scope.interactions = response.data.results[1];
        console.log(
          $scope.interactionScore,
          $scope.formattedInteractionScore,
          $scope.showNoResultsFound,
          $scope.interactions,
          response);
      },function(response){
        //TODO: bootstrap alert dialog
        alert('error fetching response');
      });
    }

    $scope.showVisualzation = viz;
  });

var vizRun = false;
function viz(){
  if(vizRun) return; 
  vizRun  = true;
  var width = 960,
      height = 500;

  var color = d3.scale.category20();

  var force = d3.layout.force()
      .charge(-120)
      .linkDistance(30)
      .size([width, height]);

  var svg = d3.select("#d3").append("svg")
      .attr("width", width)
      .attr("height", height);

  var graph = {
      "alcohol":{
                  "marijuana":0.734,
                  "advil":0.663,
                  "oxycontin":0.8
      },
      "oxycontin":{
                  "ibuprofen":0.34,
                  "modafinil":0.8
      },
      "birth control":{
                  "alcohol":0.1,
                  "marijuana":0.3
      }

  };

  var nodes = [];
  var nodeIdToIndexMap = {};
  var links = [];

  function addNode(str){
    var idx = nodeIdToIndexMap[str];
    if(!idx){
      var idx = nodes.push({name : str}) - 1;  
      nodeIdToIndexMap[str] = idx;
    }
    return idx;
  } 
  Object.keys(graph).forEach(function(source){
      var sourceIdx = addNode(source);
      Object.keys(graph[source]).forEach(function(target){
        var targetIdx = addNode(target);
        var value = graph[source][target];
        links.push({source : sourceIdx, target : targetIdx, value : value});
      });
  });
  force
      .nodes(nodes)
      .links(links)
      .distance(200)
      .charge(-200)
      .start();

  var link = svg.selectAll(".link")
      .data(links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return d.value * 10 })
      .on('click',function(d){ alert(d.value)});

  // Create the groups under svg
  var gnodes = svg.selectAll('g.gnode')
    .data(nodes)
    .enter()
    .append('g')
    .classed('gnode', true);

  // Add one circle in each group
  var node = gnodes.append("circle")
    .attr("class", "node")
    .attr("r", 5)
    .style("fill", function(d) { return color(d.group); })
    .call(force.drag);

  // Append the labels to each group
  var labels = gnodes.append("text")
    .attr("dx", 12)
    .text(function(d) { return d.name; });

  force.on("tick", function() {
    // Update the links
    link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

    // Translate the groups
    gnodes.attr("transform", function(d) { 
      return 'translate(' + [d.x, d.y] + ')'; 
    });    

  });
}
