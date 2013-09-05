(function(){
    var app = angular.module('simplelookup', ['ngResource'])

    .config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }])

    .config(['$locationProvider' ,
        function($locationProvider){
            $locationProvider.html5Mode(true);
        }]
    )

    // REST 
    .factory("REST", function(){
        // the action map for communicating with server
        return {
            action_map: {
                list: {method:'GET', isArray: true, params: { actionController: "list" }},
                search: {method:'GET', params: { actionController: "search" }},
                info: {method:'GET', params: { actionController: "info" }},
                export_csv: {method:'GET', params: { actionController: "export_csv" }},
                export_custom: {method:'GET', params: { actionController: "export_custom" }},
                export_html: {method:'GET', params: { actionController: "export_html" }},
            },
            // http://www.bennadel.com/blog/2433-Using-RESTful-Controllers-In-An-AngularJS-Resource.htm
            controller_map: {
                id: "@id",
                actionController: "@actionController",
                typeController: "@typeController"
            }
        }
    })

    .directive('simpleSearch', ["$parse", function($parse) {
        return function(scope, element, attrs) {
            var ngModel = $parse(attrs.ngModel);
            element.autocomplete({
                source: "/list",
                minLength: 3,
                focus: function(event, ui) {
                    event.preventDefault(); //Don't preopulate field
                },
                select : function(event, data) {
                    if (data) {
                        event.preventDefault(); //Keep entry blank
                        if(ngModel){
                            scope.$apply(function(scope){
                                data.item.toString = function(){
                                    return data.item.name;
                                }
                                ngModel.assign(scope, data.item);
                            });
                        }
                    }
                }
            }).data( "ui-autocomplete" )._renderItem = function(ul, item) {
                return jQuery( "<li>" )
                    .append( "<a>"+item.label+"<br><small style='color: blue'>"+item.desc+"</small></a>" )
                    .appendTo( ul );
                };
            }
    }])

    // resources
    .service(
        'search_resources',
        ['$resource', 'REST', function($resource, REST){
            this.lookUpResource = $resource(':actionController/:typeController/', REST.controller_map, REST.action_map);
        }
    ])

    .controller("searchController", ["$scope", "search_resources", function($scope, search_resources){
        $scope.init = function(){
            $scope.resource = search_resources.lookUpResource;
            $scope.info = {
                project_id: 0,
            }
        }

        var search = function(keyword){
            var request = {keyword: keyword, project_id: $scope.info.project_id}
            $scope.resource.list(request).$then(
                function(data){
                    var response = data.data;
                    $scope.loading = false;
                },
                function(){
                    $scope.loading = false;
                }            
            )
        }

        $scope.$watch("search", function(nv){
            if(nv){
                // search(nv);
            }
        })
    }])

    .controller("sidebarController", ["$scope", "$window", function($scope, $window){
    }])

    .controller("navbarController", ["$scope", "$window", function($scope, $window){
        $scope.changeProject = function(project_id){
            $scope.info.project_id = project_id;
        }
    }])
}())