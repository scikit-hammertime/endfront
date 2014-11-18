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
      $scope.showConditions = true;
      $scope.medicalProductsPrefix = '';
      $scope.medicalProductsBuffer = [];
      $scope.medicalProducts.push(product);
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
      if(!$scope.medicalProducts.length || !$scope.conditions.length){
        $scope.interactions = [];
        return;
      }

      $http.get(hostname + '/interactions?' + 
                    'medicinalproducts=' + 
                      $scope.medicalProducts.join(',') + '&' +
                    '/preexistingconditions=' + 
                    $scope.conditions.join(',')).then(function(response){
        $scope.interactions  = response.data.results;
      },function(response){
        //TODO: bootstrap alert dialog
        alert('error fetching response');
      });
    }
  });
