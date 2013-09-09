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
        'notifyService', function(){
            jQuery(document).ready(function(){
                $("#notify_container").notify();
            })
            this.notify = function(title, text, expire){
                jQuery("#notify_container").notify("create", {
                    title: title || "",
                    text: text || "",
                    },{
                        expires: expire || 1000,
                        speed: 1000
                    }
                );
            }
        }
    )

    .service(
        'localStorageService', ['$window', function($window){   
            var supports_html5_storage = function (){
            try {
                    if('localStorage' in $window && $window['localStorage'] !== null){
                        $window.localStorage.setItem('drchrono', true);
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
                    return $window.localStorage.getItem(key, true);
                }
            }
            this.set = function(key, value){
                if(this._supports_html5_storage){
                    $window.localStorage.setItem(key, value);
                }
            }
        }]
    )
    .directive('simpleSearch', ["$parse", "notifyService", function($parse, notifyService) {
        return function(scope, element, attrs) {
            var ngModel = $parse(attrs.ngModel);
            element.autocomplete({
                source: function( request, response ) {
                    $.ajax({
                        url: "/list",
                        dataType: "json",
                        data: {
                            term: request.term,
                            project_id: jQuery("#project_id").val(),
                        },
                        success: function(data) {
                            response(data.data);
                            console.log(data.data)
                            if(data.data.length === 0){
                                notifyService.notify("No Result Found...")
                            }
                        },
                        error: function(data){
                            notifyService.notify("Something is wrong...")
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

    .controller("searchController", ["$scope", "search_resources", "$window", "localStorageService", "notifyService", function($scope, search_resources, $window, localStorageService, notifyService){
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

        $scope.clearHistory = function(){
            $scope.record = null;
            $scope.result_history = [];
            saveHistory();
        }

        $scope.resetView = function(){
            $scope.result = {}
            $scope.attrs = []
            $scope.functions = []
            $scope.classes = []
            $scope.code = ""
        }

        $scope.searchRecord = function(obj){
            notifyService.notify("Loading...");
            pushResult(obj);
            var request = {'id': obj.id, 'type': obj.type, 'project_id': obj.project_id};
            $scope.resetView();
            $scope.request_id += 1;
            if("project_id" in obj)
                $scope.info.project_id = obj.project_id;
            search(request, $scope.request_id)
        }

        var search = function(request, request_id){
           $scope.resource.search(request).$then(
                function(data){
                    if(request_id != $scope.request_id)
                        return false;
                    $window.scrollTo(0, 0);
                    var response = data.data;
                    $scope.result = response.record;
                    $scope.code = response.code;
                    $scope.attrs = response.attrs || [];
                    $scope.functions = response.functions || []
                    $scope.methods = response.methods || []
                    $scope.classes = response.classes || []
                    formatCode();
                },
                function(){
                    $scope.loading = false;
                    notifyService.notify("Something is wrong...")
                }            
            )
        }

        var formatCode = function(){
            $window.jQuery("#id_source_code").removeClass("prettyprinted")
            $window.setTimeout($window.prettyPrint, 101);
        }

        var saveHistory = function(){
            $scope.localStorageService.set('history', $window.JSON.stringify($scope.result_history, function (key, val) {
                    if (key == '$$hashKey') {
                        return undefined;
                    }
                    return val;
                })
            );
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
            saveHistory();
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
