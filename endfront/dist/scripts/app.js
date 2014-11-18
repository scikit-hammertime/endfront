'use strict';

/**
 * @ngdoc overview
 * @name interactionsApp
 * @description
 * # interactionsApp
 *
 * Main module of the application.
 */
angular
  .module('interactionsApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
