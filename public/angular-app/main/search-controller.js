angular.module('tedSearchEngine').controller('SearchController',SearchController);
function SearchController(searchDataFactory,$routeParams,$location){
    var vm=this;
    vm.getSearchResults = function(){
        if(vm.query){
            searchDataFactory.getSearches(vm.query).then(function(response){
                console.log(response)
                $location.path('/search').search({'q':vm.query})
            });
        }
    }


    
}