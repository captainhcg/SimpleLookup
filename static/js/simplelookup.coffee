root = exports ? this

root.simplelookup = (jQuery)->
    $ = jQuery
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

    app.service 'localStorageService', ['$window', ($window)->
        supports_html5_storage = ->
            try
                if 'localStorage' in $window && $window['localStorage'] != null
                    $window.localStorage.setItem 'drchrono', true
                    true
                else
                    false
            catch e
                false

        _supports_html5_storage = supports_html5_storage
        @get = (key)->
            if _supports_html5_storage
                $window.localStorage.getItem 'drchrono', true
      
        @set = (key)->
            if _supports_html5_storage
                $window.localStorage.setItem 'drchrono', true
    ]

    app.directive 'simpleSearch', ["$parse", "notifyService", ($parse, notifyService)->
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
    null