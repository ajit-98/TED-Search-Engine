angular.module('tedSearchEngine').factory('searchDataFactory',searchDataFactory);

function searchDataFactory($http){
    return {
        getSearches:getSearches,
        displaySearchResults:displaySearchResults
    };
    function getSearches(query){
        return $http.get('/api/search?q='+query).then(complete).catch(failed);
    }
    function displaySearchResults(query){
        return $http.get('/api/search?q='+query).then(complete).catch(failed);
    }
    function complete(response){
        return response.data;
    }
    function failed(error){
        console.log(error.statusText);
    }
}