"use strict";function viz(){function a(a){var b=i[a];if(!b){var b=h.push({name:a})-1;i[a]=b}return b}if(!vizRun){vizRun=!0;var b=960,c=500,d=d3.scale.category20(),e=d3.layout.force().charge(-120).linkDistance(30).size([b,c]),f=d3.select("#d3").append("svg").attr("width",b).attr("height",c),g={alcohol:{marijuana:.734,advil:.663,oxycontin:.8},oxycontin:{ibuprofen:.34,modafinil:.8},"birth control":{alcohol:.1,marijuana:.3}},h=[],i={},j=[];Object.keys(g).forEach(function(b){var c=a(b);Object.keys(g[b]).forEach(function(d){var e=a(d),f=g[b][d];j.push({source:c,target:e,value:f})})}),e.nodes(h).links(j).distance(200).charge(-200).start();{var k=f.selectAll(".link").data(j).enter().append("line").attr("class","link").style("stroke-width",function(a){return Math.sqrt(a.value)}),l=f.selectAll("g.gnode").data(h).enter().append("g").classed("gnode",!0);l.append("circle").attr("class","node").attr("r",5).style("fill",function(a){return d(a.group)}).call(e.drag),l.append("text").text(function(a){return a.name})}e.on("tick",function(){k.attr("x1",function(a){return a.source.x}).attr("y1",function(a){return a.source.y}).attr("x2",function(a){return a.target.x}).attr("y2",function(a){return a.target.y}),l.attr("transform",function(a){return"translate("+[a.x,a.y]+")"})})}}angular.module("interactionsApp",["ngAnimate","ngCookies","ngResource","ngRoute","ngSanitize","ngTouch"]).config(["$routeProvider",function(a){a.when("/",{templateUrl:"views/main.html",controller:"MainCtrl"}).otherwise({redirectTo:"/"})}]),angular.module("interactionsApp").controller("MainCtrl",["$scope","$http","$q",function(a,b,c){function d(){return!a.medicalProducts.length||a.medicalProducts.length<2||!a.conditions.length?(a.interactions=[],a.interactionScore=null,void(a.showNoResultsFound=!1)):void b.get(e+"/interactions?medicinalproducts="+a.medicalProducts.join(",")+"&preexistingconditions="+a.conditions.join(",")).then(function(b){return b.data.results&&2===b.data.results.length?(a.interactionScore=b.data.results[0].filter(function(a){return"Interaction"===a.AE})[0].score,a.formattedInteractionScore=Math.round(100*a.interactionScore),a.showNoResultsFound=0===b.data.results[1].length,a.interactions=b.data.results[1],void console.log(a.interactionScore,a.formattedInteractionScore,a.showNoResultsFound,a.interactions,b)):void alert("Unexpected result from server")},function(){alert("error fetching response")})}var e="";a.showMedicinalProducts=!0,a.medicalProductsPrefix="",a.medicalProducts=[],a.medicalProductsBuffer=[];var f=c.defer();a.$watch("medicalProductsPrefix",function(d){return console.log("medicalProductsPrefix",d),!d||d.length<4?void(a.medicalProductsBuffer=[]):(f.resolve,f=c.defer(),void b.get(e+"/medicinalproducts?startsWith="+d,{timeout:f.promise}).then(function(b){a.medicalProductsBuffer=b.data.drugs.filter(function(b){return-1===a.medicalProducts.indexOf(b)}),console.log("response",b.data,a.medicalProductsBuffer)},function(){alert("error fetching response")}))}),a.addMedicalProduct=function(b){a.medicalProductsPrefix="",a.medicalProductsBuffer=[],a.medicalProducts.push(b),a.showConditions=a.showConditions||a.medicalProducts.length>=2,d()},a.removeMedicalProduct=function(b){a.medicalProducts.splice(a.medicalProducts.indexOf(b),1),d()},a.conditionsPrefix="",a.conditions=[],a.conditionsBuffer=[];var g=c.defer();a.$watch("conditionsPrefix",function(d){return!d||d.length<4?void(a.conditionsBuffer=[]):(g.resolve,g=c.defer(),void b.get(e+"/preexistingconditions?startsWith="+d,{timeout:g.promise}).then(function(b){a.conditionsBuffer=b.data.conditions.filter(function(b){return-1===a.conditions.indexOf(b)})},function(){alert("error fetching response")}))}),a.addCondition=function(b){a.showInteractions=!0,a.conditionsPrefix="",a.conditionsBuffer=[],a.conditions.push(b),d()},a.removeCondition=function(b){a.conditions.splice(a.medicalProducts.indexOf(b),1),d()},a.interactions=[],a.showVisualzation=viz}]);var vizRun=!1;