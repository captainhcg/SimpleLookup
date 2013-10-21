/* jQuery Notify UI Widget 1.5 by Eric Hynds
 * http://www.erichynds.com/jquery/a-jquery-ui-growl-ubuntu-notification-widget/
 *
 * Depends:
 *   - jQuery 1.4
 *   - jQuery UI 1.8 widget factory
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
*/
(function(d){d.widget("ech.notify",{options:{speed:500,expires:5E3,stack:"below",custom:!1,queue:!1},_create:function(){var a=this;this.templates={};this.keys=[];this.element.addClass("ui-notify").children().addClass("ui-notify-message ui-notify-message-style").each(function(b){b=this.id||b;a.keys.push(b);a.templates[b]=d(this).removeAttr("id").wrap("<div></div>").parent().html()}).end().empty().show()},create:function(a,b,c){"object"===typeof a&&(c=b,b=a,a=null);a=this.templates[a||this.keys[0]];c&&c.custom&&(a=d(a).removeClass("ui-notify-message-style").wrap("<div></div>").parent().html());this.openNotifications=this.openNotifications||0;return(new d.ech.notify.instance(this))._create(b,d.extend({},this.options,c),a)}});d.extend(d.ech.notify,{instance:function(a){this.__super=a;this.isOpen=!1}});d.extend(d.ech.notify.instance.prototype,{_create:function(a,b,c){this.options=b;var e=this,c=c.replace(/#(?:\{|%7B)(.*?)(?:\}|%7D)/g,function(b,c){return c in a?a[c]:""}),c=this.element=d(c),f=c.find(".ui-notify-close");"function"===typeof this.options.click&&c.addClass("ui-notify-click").bind("click",function(a){e._trigger("click",a,e)});f.length&&f.bind("click",function(){e.close();return!1});this.__super.element.queue("notify",function(){e.open();"number"===typeof b.expires&&0<b.expires&&setTimeout(d.proxy(e.close,e),b.expires)});(!this.options.queue||this.__super.openNotifications<=this.options.queue-1)&&this.__super.element.dequeue("notify");return this},close:function(){var a=this.options.speed;this.element.fadeTo(a,0).slideUp(a,d.proxy(function(){this._trigger("close");this.isOpen=!1;this.element.remove();this.__super.openNotifications-=1;this.__super.element.dequeue("notify")},this));return this},open:function(){if(this.isOpen||!1===this._trigger("beforeopen"))return this;var a=this;this.__super.openNotifications+=1;this.element["above"===this.options.stack?"prependTo":"appendTo"](this.__super.element).css({display:"none",opacity:""}).fadeIn(this.options.speed,function(){a._trigger("open");a.isOpen=!0});return this},widget:function(){return this.element},_trigger:function(a,b,c){return this.__super._trigger.call(this,a,b,c)}})})(jQuery);

var __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

this.simplelookup = (function($) {
  var app;
  app = angular.module('simplelookup', ["ngResource"]);
  app.config([
    '$interpolateProvider', function($interpolateProvider) {
      $interpolateProvider.startSymbol('[[');
      $interpolateProvider.endSymbol(']]');
    }
  ]);
  app.factory('REST', function() {
    return {
      action_map: {
        list: {
          method: 'GET',
          isArray: true,
          params: {
            actionController: 'list'
          }
        },
        search: {
          method: 'GET',
          params: {
            actionController: 'search'
          }
        },
        track: {
          method: 'GET',
          params: {
            actionController: 'track'
          }
        }
      },
      controller_map: {
        id: '@id',
        actionController: "@actionController",
        typeController: "@typeController"
      }
    };
  });
  app.service('notifyService', function() {
    $(document).ready(function() {
      $('#notify_container').notify();
    });
    this.notify = function(title, text, expire) {
      $('#notify_container').notify('create', {
        title: title || '',
        text: text || ''
      }, {
        expire: expire || 1000,
        speed: 1000
      });
    };
  });
  app.service('localStorageService', [
    '$window', function($window) {
      var supports_html5_storage, _supports_html5_storage;
      supports_html5_storage = function() {
        try {
          if ('localStorage' in $window && $window['localStorage'] !== null) {
            $window.localStorage.setItem('simplelookup', true);
            return true;
          } else {
            return false;
          }
        } catch (e) {
          return false;
        }
      };
      _supports_html5_storage = supports_html5_storage();
      this.get = function(key) {
        if (_supports_html5_storage) {
          return $window.localStorage.getItem(key);
        }
      };
      this.set = function(key, value) {
        if (_supports_html5_storage) {
          return $window.localStorage.setItem(key, value);
        }
      };
    }
  ]);
  app.service('search_resources', [
    '$resource', 'REST', function($resource, REST) {
      this.lookUpResource = $resource(':actionController/:typeController/', REST.controller_map, REST.action_map);
      return null;
    }
  ]);
  app.directive('simpleSearch', [
    "$parse", "notifyService", function($parse, notifyService) {
      return function(scope, element, attrs) {
        var ngModel;
        ngModel = $parse(attrs.ngModel);
        element.autocomplete({
          source: function(request, response) {
            return $.ajax({
              url: "/list",
              dataType: "json",
              data: {
                term: request.term,
                project_id: $("#project_id").val()
              },
              success: function(data) {
                response(data.data);
                if (data.data.length === 0) {
                  return notifyService.notify("No Result Found...");
                }
              },
              error: function(data) {
                return notifyService.notify("Something is wrong...");
              }
            });
          },
          minLength: 1,
          focus: function(event, ui) {
            return event.preventDefault();
          },
          select: function(event, data) {
            if (data) {
              event.preventDefault();
              if (ngModel) {
                return scope.$apply(function(scope) {
                  data.item.toString = function() {
                    return data.item.name;
                  };
                  return ngModel.assign(scope, data.item);
                });
              }
            }
          }
        });
        return element.data("ui-autocomplete")._renderItem = function(ul, item) {
          return $("<li>").append("<a>" + item.label + "<br><small style='color: blue'>" + item.desc + "</small></a>").appendTo(ul);
        };
      };
    }
  ]);
  app.controller("searchController", [
    "$scope", "search_resources", "$window", "localStorageService", "notifyService", function($scope, search_resources, $window, localStorageService, notifyService) {
      var makePath, pushResult, sameRecord, saveHistory, search;
      $scope.request_id = 1;
      $scope.init = function() {
        $scope.resource = search_resources.lookUpResource;
        $scope.info = {
          project_id: 0
        };
        $scope.localStorageService = localStorageService;
        $scope.result_history = $window.JSON.parse($scope.localStorageService.get("history") || "[]") || [];
        $scope.info.project_id = $scope.localStorageService.get("project_id") || 0;
        $scope.revisions = {};
        $scope.viewing = "code";
      };
      $scope.clearHistory = function() {
        $scope.record = null;
        $scope.result_history = [];
        saveHistory();
      };
      $scope.resetView = function() {
        $scope.result = {};
        $scope.attrs = [];
        $scope.functions = [];
        $scope.classes = [];
        $scope.code = "";
      };
      $scope.searchRecord = function(obj) {
        var request;
        if (obj.label) {
          pushResult(obj);
        }
        request = {
          'id': obj.id,
          'type': obj.type,
          'project_id': obj.project_id
        };
        $scope.resetView();
        $scope.request_id += 1;
        if (__indexOf.call(obj, "project_id") >= 0) {
          $scope.info.project_id = obj.project_id;
        }
        search(request, $scope.request_id);
      };
      sameRecord = function(o1, o2) {
        var attr, cmp_list, _i, _len;
        if (!o1 && !o2) {
          return true;
        } else if (o1 && o2) {
          cmp_list = ['project_id', 'function_id', 'module_id', 'class_id'];
          for (_i = 0, _len = cmp_list.length; _i < _len; _i++) {
            attr = cmp_list[_i];
            if (o1[attr] !== o2[attr]) {
              return false;
            }
          }
          return true;
        } else {
          return false;
        }
      };
      $scope.getRevisions = function(obj) {
        if (sameRecord(obj, $scope.revisions.obj)) {
          $scope.viewing = "revisions";
          return;
        }
        $scope.loading = true;
        $scope.resource.track(obj).$then(function(data) {
          var response;
          response = data.data;
          $scope.loading = false;
          $scope.viewing = "revisions";
          $scope.revisions = {};
          $scope.revisions.obj = obj;
          $scope.revisions.list = response.data;
          return $scope.revisions.terminated = response.terminated;
        }, function() {
          $scope.loading = false;
          return notifyService.notify("Something is wrong...");
        });
      };
      $scope.toggleDisplay = function(revision) {
        var r, _i, _len, _ref;
        if (revision.display) {
          return revision.display = false;
        } else {
          _ref = $scope.revisions.list;
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            r = _ref[_i];
            r.display = false;
          }
          return revision.display = true;
        }
      };
      $scope.getMoreRevisions = function(obj, last_hash) {
        $scope.loading = true;
        obj.last_hash = last_hash;
        $scope.resource.track(obj).$then(function(data) {
          var response;
          response = data.data;
          $scope.loading = false;
          $scope.viewing = "revisions";
          $scope.revisions.obj = obj;
          $scope.revisions.list = $scope.revisions.list.concat(response.data);
          return $scope.revisions.terminated = response.terminated;
        }, function() {
          $scope.loading = false;
          return notifyService.notify("Something is wrong...");
        });
      };
      search = function(request, request_id) {
        $scope.resource.search(request).$then(function(data) {
          var response;
          if (request_id !== $scope.request_id) {
            return false;
          }
          $window.scrollTo(0, 0);
          $scope.loading = false;
          $scope.viewing = "code";
          response = data.data;
          $scope.result = response.record;
          $scope.result.project_id = request.project_id;
          $scope.code = response.code;
          $scope.attrs = response.attrs || [];
          $scope.functions = response.functions || [];
          $scope.methods = response.methods || [];
          $scope.classes = response.classes || [];
          return makePath($scope.result);
        }, function() {
          $scope.loading = false;
          return notifyService.notify("Something is wrong...");
        });
      };
      makePath = function(obj) {
        $scope.path = {};
        if (obj.type === "module") {
          $scope.path.path = obj.path;
          $scope.path.module = obj.label;
          $scope.path.module_id = obj.id;
        } else if (obj.type === "class") {
          $scope.path.path = obj.module_path;
          $scope.path.module = obj.module_name;
          $scope.path.module_id = obj.module_id;
          $scope.path["class"] = obj.label;
          $scope.path.class_id = obj.id;
        } else if (obj.type === "function" || obj.type === "method") {
          $scope.path.path = obj.module_path;
          $scope.path.module = obj.module_name;
          $scope.path.module_id = obj.module_id;
          $scope.path["class"] = obj.class_name;
          $scope.path.class_id = obj.class_id;
          $scope.path["function"] = obj.label;
          $scope.path.function_id = obj.id;
        }
        $scope.path.project_id = obj.project_id;
        return $scope.path;
      };
      saveHistory = function() {
        return $scope.localStorageService.set('history', $window.JSON.stringify($scope.result_history, function(key, val) {
          if (key === "$$hashKey") {
            return void 0;
          } else {
            return val;
          }
        }));
      };
      pushResult = function(obj) {
        var idx, r;
        idx = $scope.result_history.length;
        while (idx) {
          idx = idx - 1;
          r = $scope.result_history[idx];
          if (r.id === obj.id && r.name === obj.name && r.type === obj.type) {
            $scope.result_history.splice(idx, 1);
          }
        }
        $scope.result_history.splice(0, 0, angular.copy(obj));
        if ($scope.result_history.length > 15) {
          $scope.result_history.pop();
        }
        return saveHistory();
      };
      $scope.$watch("record", function(nv) {
        $scope.revisions = {};
        if (nv && typeof nv === "object") {
          $scope.searchRecord(nv);
        }
      });
      $scope.init();
    }
  ]);
  app.controller("navbarController", [
    "$scope", "$window", function($scope, $window) {
      return $scope.changeProject = function(project_id) {
        $scope.info.project_id = project_id;
        return $scope.localStorageService.set("project_id", project_id);
      };
    }
  ]);
  return app;
})(jQuery);
