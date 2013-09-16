this.simplelookup = (($)->
    
    app = angular.module 'simplelookup', ["ngResource"]
    
    app.config ['$interpolateProvider', ($interpolateProvider)->
        $interpolateProvider.startSymbol '[['
        $interpolateProvider.endSymbol ']]'
        return
    ]

    app.factory 'REST', ->
        action_map:
            list: {method:'GET', isArray: true, params: {actionController: 'list'}}
            search: {method: 'GET', params: {actionController: 'search'}}
        controller_map:
            id: '@id'
            actionController: "@actionController"
            typeController: "@typeController"

    app.service 'notifyService', ->
        document = $(document)
        document.ready ->
            notify_container = $('#notify_container')
            @notify = (title, text, expire) ->
                notify_container.notify(
                    'create', 
                    {title: title || '', text: text || ''}, 
                    {expire: expire || 1000, speed: 1000},
                )

    app.service 'localStorageService', 
        ['$window', ($window)->
            supports_html5_storage = ->
                try
                    if 'localStorage' in $window && $window['localStorage'] isnt null
                        $window.localStorage.setItem 'simplelookup', true
                        true
                    else
                        false
                catch e
                    false

            _supports_html5_storage = supports_html5_storage
            @get = (key)->
                if _supports_html5_storage
                    $window.localStorage.getItem key
          
            @set = (key, value)->
                if _supports_html5_storage
                    $window.localStorage.setItem key, value
        ]

    app.service 'search_resources',
        ['$resource', 'REST', ($resource, REST)->
            this.lookUpResource = $resource ':actionController/:typeController/', REST.controller_map, REST.action_map
            null
        ]

    app.directive 'simpleSearch', [
        "$parse", "notifyService", ($parse, notifyService)->
            (scope, element, attrs)->
                ngModel = $parse attrs.ngModel
                element.autocomplete {
                    source: (request, response)->
                        $.ajax {
                            url: "/list"
                            dataType: "json"
                            data:
                                term: request.term
                                project_id: $("#project_id").val()
                            success: (data)->
                                response data.data
                                if data.data.length == 0
                                    notifyService.notify "No Result Found..."
                            error: (data)->
                                notifyService.notify "Something is wrong..."
                            }
                    minLength: 1,
                    focus: (event, ui)->
                        event.preventDefault 
                    select: (event, data)->
                        if data
                            event.preventDefault
                            if ngModel
                                scope.$apply (scope)->
                                    data.item.toString = ->
                                        data.item.name
                                    ngModel.assign scope, data.item
                }

                element.data("ui-autocomplete")._renderItem = (ul, item)->
                    $("<li>")
                        .append("<a>"+item.label+"<br><small style='color: blue'>"+item.desc+"</small></a>")
                        .appendTo(ul)
            ]

    app.controller "searchController", 
        ["$scope", "search_resources", "$window", "localStorageService", "notifyService", ($scope, search_resources, $window, localStorageService, notifyService)->
            $scope.request_id = 1;

            $scope.init = ->
                $scope.resource = search_resources.lookUpResource
                $scope.info = project_id: 0
                $scope.localStorageService = localStorageService
                $scope.result_history = $window.JSON.parse($scope.localStorageService.get("history")) or []
                $scope.info.project_id = $scope.localStorageService.get("project_id") or 0
                return

            $scope.clearHistory = ->
                $scope.record = null
                $scope.result_history = []
                saveHistory()
                return

            $scope.resetView = ->
                $scope.result = {}
                $scope.attrs = []
                $scope.functions = []
                $scope.classes = []
                $scope.code = ""
                return

            $scope.searchRecord = (obj)->
                pushResult(obj) if obj.label
                request = 'id': obj.id, 'type': obj.type, 'project_id': obj.project_id
                $scope.resetView()
                $scope.request_id += 1
                $scope.info.project_id = obj.project_id if "project_id" in obj
                search request, $scope.request_id
                return

            search = (request, request_id)->
                $scope.resource.search(request).$then(
                    (data)->
                        return false if request_id != $scope.request_id 
                        $window.scrollTo 0, 0
                        response = data.data
                        $scope.result = response.record
                        $scope.result.project_id = request.project_id
                        $scope.code = response.code
                        $scope.attrs = response.attrs or []
                        $scope.functions = response.functions or []
                        $scope.methods = response.methods or []
                        $scope.classes = response.classes or []
                        makePath $scope.result
                    ->
                        $scope.loading = false
                        notifyService.notify "Something is wrong..."
                )
                return

            makePath = (obj)->
                $scope.path = {}
                if obj.type == "module"
                    $scope.path.path = obj.path
                    $scope.path.module = obj.label
                    $scope.path.module_id = obj.id

                else if obj.type == "class"
                    $scope.path.path = obj.module_path
                    $scope.path.module = obj.module_name
                    $scope.path.module_id = obj.module_id
                    $scope.path.class = obj.label
                    $scope.path.class_id = obj.id

                else if obj.type == "function" or obj.type == "method"
                    $scope.path.path = obj.module_path
                    $scope.path.module = obj.module_name
                    $scope.path.module_id = obj.module_id
                    $scope.path.class = obj.class_name
                    $scope.path.class_id = obj.class_id
                    $scope.path.function = obj.label
                    $scope.path.function_id = obj.id
                $scope.path.project_id = obj.project_id
                $scope.path

            saveHistory = ->
                $scope.localStorageService.set 'history', $window.JSON.stringify($scope.result_history, (key, val)->
                    if key == "$$hashKey"
                        undefined
                    else
                        val
                )

            pushResult = (obj)->
                idx = $scope.result_history.length
                while idx
                    idx = idx - 1
                    r = $scope.result_history[idx];
                    if r.id==obj.id and r.name==obj.name and r.type==obj.type
                        $scope.result_history.splice idx, 1

                $scope.result_history.splice 0, 0, obj
                $scope.result_history.pop if $scope.result_history.length > 15
                saveHistory()

            $scope.$watch "record", (nv)->
                if nv and typeof(nv) == "object"
                    $scope.searchRecord nv
                return
        ]

    app.controller "navbarController", 
        ["$scope", "$window", ($scope, $window)->
            $scope.changeProject = (project_id)->
                $scope.info.project_id = project_id;
                $scope.localStorageService.set "project_id", project_id
        ]

    app
)(jQuery)