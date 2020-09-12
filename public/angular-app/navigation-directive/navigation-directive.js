angular.module('tedSearchEngine').directive('searchNavigation',searchNavigation);

function searchNavigation(){
    return {
        restrict: 'E',
        templateUrl: 'angular-app/navigation-directive/navigation-directive.html',   
    };
}