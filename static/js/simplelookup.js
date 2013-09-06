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

    .service(
        'localStorageService', ['$window', function($window){   
            var supports_html5_storage = function (){
            try {
                    if('localStorage' in window && window['localStorage'] !== null){
                        window.localStorage.setItem('drchrono', true);
                        return true;
                    } else {
                        return false;
                    }
                } catch (e) {
                    return false;
                }            
            }
            this._supports_html5_storage = supports_html5_storage();
            this.get = function(key){
                if(this._supports_html5_storage){
                    return window.localStorage.getItem(key, true);
                }
            }
            this.set = function(key, value){
                if(this._supports_html5_storage){
                    window.localStorage.setItem(key, value);
                }
            }
        }]
    )
    .directive('simpleSearch', ["$parse", function($parse) {
        return function(scope, element, attrs) {
            var ngModel = $parse(attrs.ngModel);
            element.autocomplete({
                source: function( request, response ) {
                    $.ajax({
                        url: "/list",
                        dataType: "json",
                        data: {
                            term: request.term,
                            project_id: $("#project_id").val(),
                        },
                        success: function(data) {
                            response(data.data);
                        }
                    });
                },
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

    .controller("searchController", ["$scope", "search_resources", "$window", "localStorageService", function($scope, search_resources, $window, localStorageService){
        $scope.request_id = 1;

        $scope.init = function(){
            $scope.resource = search_resources.lookUpResource;
            $scope.info = {
                project_id: 0,
            }
            $scope.localStorageService = localStorageService;
            $scope.result_history = $window.JSON.parse($scope.localStorageService.get("history")) || []
            $scope.info.project_id = $scope.localStorageService.get("project_id") || 0;
        }

        $scope.resetView = function(){
            $scope.result = {}
            $scope.attrs = []
            $scope.functions = []
            $scope.classes = []
        }

        $scope.searchRecord = function(obj){
            pushResult(obj);
            var request = obj
            $scope.resetView();
            $scope.request_id += 1;
            var this_request_id = $scope.request_id;
            $scope.resource.search(obj).$then(
                function(data){
                    if(this_request_id != $scope.request_id)
                        return false;
                    $window.scrollTo(0, 0);
                    var response = data.data;
                    $scope.result = response.result;
                    $scope.attrs = response.attrs || [];
                    $scope.functions = response.functions || []
                    $scope.classes = response.classes || []
                    window.setTimeout(function(){
                        $window.jQuery("#id_source_code").removeClass("prettyprinted")
                        $window.prettyPrint()
                    }, 10);
                },
                function(){
                    $scope.loading = false;
                }            
            )
        }
        var pushResult = function(obj){
            var index = -1;
            for(var i=$scope.result_history.length-1; i>=0; i--){
                var r = $scope.result_history[i];
                if(r.id==obj.id && r.name==obj.name && r.type==obj.type){
                    $scope.result_history.splice(i, 1);
                }
            }
            $scope.result_history.splice(0, 0, obj);
            if($scope.result_history.length > 15)
                $scope.result_history.pop()
            $scope.localStorageService.set('history', $window.JSON.stringify($scope.result_history));
        }

        $scope.result_history = []

        $scope.$watch("record", function(nv){
            if(nv && typeof nv === "object"){
                $scope.searchRecord(nv);
            }
        })
    }])

    .controller("navbarController", ["$scope", "$window", function($scope, $window){
        $scope.changeProject = function(project_id){
            $scope.info.project_id = project_id;
            $scope.localStorageService.set("project_id", project_id);
        }
    }])
}())
