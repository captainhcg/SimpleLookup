var app = angular.module('simplelookup', [])

.service('keyWord', function () {
    var keyword = "";
    var type = "";
    var module = "";
    return {
        getProperty:function () {
            return keyword;
        },
        setProperty:function (value) {
            keyword = value;
        }
    };
})

.controller("sidebarController", ["$scope", "$window", "keyWord", function($scope, $window, keyWord){
	$scope.$watch("search", function(nv){
		if(nv){
			console.log($scope.search);
		}

	})
}])