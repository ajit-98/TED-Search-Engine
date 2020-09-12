var punctuation = ['.',',','!','?'];

angular.module('tedSearchEngine').controller('SearchDispController',SearchDispController);

function SearchDispController(searchDataFactory,$routeParams,$window){
    var vm=this;
    vm.query = $routeParams.q
    vm.noResult = false;
    vm.Display = false;
    searchDataFactory.displaySearchResults(vm.query).then(function(response){
        if(response.repeatRequest == '1'){
            $window.location.reload()
        } 
        else{
            vm.Display = true;
            vm.searchResults = response.searchResults
            var len = vm.searchResults.length;
            if (len==0){
                vm.noResult = true;
            }
            for(i=0;i<len;i++){
                var dispTranscript = vm.searchResults[i].transcript
                var j=200
                while(!punctuation.includes(dispTranscript.charAt(j))){
                    j = j-1;
                }
                console.log(j)
                vm.searchResults[i].transcript = dispTranscript.substring(0,j) + '...'
            }
                
        }
    })
    
    
}
