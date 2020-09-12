angular.module('tedSearchEngine',['ngRoute']).config(config)

function config($routeProvider){
    $routeProvider.when('/',{
        templateUrl: 'angular-app/main/main.html',
        controller: SearchController,
        controllerAs: 'vm',
        access:{
            restricted:false
        }
    })
    .when('/search',{
        templateUrl: 'angular-app/disp-results/search-results.html',
        controller: SearchDispController,
        controllerAs: 'vm',
        access:{
            restricted:false
        }
    })
};