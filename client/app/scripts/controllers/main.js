GLClient.controller('MainCtrl', ['$scope', '$rootScope', '$http', '$route', '$routeParams', '$location',  '$filter', '$translate', '$modal', 'Authentication', 'Node', 'GLCache',
  function($scope, $rootScope, $http, $route, $routeParams, $location, $filter, $translate, $modal, Authentication, Node, GLCache) {
    $scope.started = true;
    $scope.rtl = false;
    $scope.logo = '/static/globaleaks_logo.png';
    $scope.build_stylesheet = '/styles.css';

    var iframeCheck = function() {
      try {
        return window.self !== window.top;
      } catch (e) {
        return true;
      }
    };

    $scope.update = function (model, cb, errcb) {
      var success = {};
      success.message = "Updated " + model;
      model.$update(function(result) {
        if (!$scope.successes) {
          $scope.successes = [];
        }
        $scope.successes.push(success);
      }).then(
        function() { if (cb != undefined) cb(); },
        function() { if (errcb != undefined) errcb(); }
      );
    };

    $scope.randomFluff = function () {
      return Math.random() * 1000000 + 1000000;
    };

    $scope.isWizard = function () {
      return $location.path() == '/wizard';
    };

    $scope.isHomepage = function () {
      return $location.path() == '/';
    };

    $scope.isLoginPage = function () {
      return ($location.path() == '/login' ||
              $location.path() == '/admin');
    };

    $scope.showLoginForm = function () {
      return (!$scope.isHomepage() &&
              !$scope.isLoginPage());
    };

    $scope.hasSubtitle = function () {
      return $scope.header_subtitle != '';
    };

    $scope.open_intro = function () {
      if ($scope.intro_opened) {
        return;
      } else {
        $scope.intro_opened = true;
      }

      var modalInstance = $modal.open({
        templateUrl: 'views/partials/intro.html',
        controller: 'IntroCtrl',
        size: 'lg',
        scope: $scope
      });

    };

    $scope.set_title = function () {
      if ($location.path() == '/') {
        $scope.ht = $scope.node.header_title_homepage;
      } else if ($location.path() == '/submission') {
        $scope.ht = $scope.node.header_title_submissionpage;
      } else if ($location.path() == '/receipt') {
        $scope.ht = $scope.node.header_title_receiptpage;
      } else {
        $scope.ht = $filter('translate')($scope.header_title);
      }
    }

    $scope.route_check = function () {
      if ($scope.node) {

        if ($scope.node.wizard_done === false) {
          $location.path('/wizard');
        }

        if (($location.path() == '/') && ($scope.node.landing_page == 'submissionpage')) {
          $location.path('/submission');
        }

        if ($location.path() == '/submission' &&
            $scope.anonymous === false &&
            $scope.node.tor2web_submission === false) {
          $location.path("/");
        }

        /* Feature implemented for amnesty and currently disabled */
        //$scope.open_intro();
      }
    }

    $scope.show_file_preview = function(content_type) {
      var content_types = [
        'image/gif',
        'image/jpeg',
        'image/png',
        'image/bmp'
      ];

      return content_types.indexOf(content_type) > -1;
    };

    var init = function () {

      $scope.logo = '/static/globaleaks_logo.png?' + $scope.randomFluff();
      $scope.build_stylesheet = "/styles.css?" + $scope.randomFluff();

      $scope.session_id = Authentication.id;
      $scope.homepage = Authentication.homepage;
      $scope.auth_landing_page = Authentication.auth_landing_page;
      $rootScope.role = Authentication.role;

      $scope.node = Node.get(function(node, getResponseHeaders) {

        // Tor detection and enforcing of usage of HS if users are using Tor
        if (window.location.hostname.match(/^[a-z0-9]{16}\.onion$/)) {
          // A better check on this situation would be
          // to fetch https://check.torproject.org/api/ip
          $rootScope.anonymous = true;
        } else {
          if (window.location.protocol === 'https:') {
             var headers = getResponseHeaders();
             if (headers['x-check-tor'] !== undefined && headers['x-check-tor'] === 'true') {
               $rootScope.anonymous = true;
               if ($scope.node.hidden_service && !iframeCheck()) {
                 // the check on the iframe is in order to avoid redirects
                 // when the application is included inside iframes in order to not
                 // mix HTTPS resources with HTTP resources.
                 window.location.href = $scope.node.hidden_service + $location.url();
               }
             } else {
               $rootScope.anonymous = false;
             }
          } else {
            $rootScope.anonymous = false;
          }
        }

        $scope.route_check();

        if ($rootScope.language == undefined || $.inArray($rootScope.language, node.languages_enabled) == -1) {
          $rootScope.language = node.default_language;
          $rootScope.default_language = node.default_language;
          $translate.use($rootScope.language);
        }

        $scope.languages_supported = {};
        $scope.languages_enabled = {};
        $scope.languages_enabled_selector = [];
        $.each(node.languages_supported, function (idx) {
          var code = node.languages_supported[idx]['code'];
          $scope.languages_supported[code] = node.languages_supported[idx]['name'];
          if ($.inArray(code, node.languages_enabled) != -1) {
            $scope.languages_enabled[code] = node.languages_supported[idx]['name'];
            $scope.languages_enabled_selector.push({"name": node.languages_supported[idx]['name'], "code": code});
          }
        });

        $scope.languages_enabled_length = Object.keys(node.languages_enabled).length;

        $scope.show_language_selector = ($scope.languages_enabled_length > 1);

        $scope.set_title();

      });

    };

    $scope.reload = function() {
      GLCache.removeAll();
      init();
      $route.reload();
    }

    $scope.$on( "$routeChangeStart", function(event, next, current) {
      $scope.route_check();
    });

    $scope.$on('$routeChangeSuccess', function() {
      var lang = $location.search().lang;
      if(lang && $.inArray(lang, $scope.node.languages_enabled) !== -1) {
        $rootScope.language = lang;
      }

      $scope.set_title();

    });

    $scope.$on("REFRESH", function() {
      $scope.reload();
    });

    $rootScope.$watch('language', function (newVal, oldVal) {
      if (newVal && newVal !== oldVal) {

        if(oldVal === undefined && newVal === $scope.node.default_language)
          return;

        $translate.use($rootScope.language);

        if (["ar", "he", "ur"].indexOf(newVal) !== -1) {
          $scope.rtl = true;
          $scope.build_stylesheet = "/styles-rtl.css";
        } else {
          $scope.rtl = false;
          $scope.build_stylesheet = "/styles.css";
        }

        $rootScope.$broadcast("REFRESH");

      }

    });

    $scope.$watch(function (scope) {
      return Authentication.id;
    }, function (newVal, oldVal) {
      $scope.session_id = Authentication.id;
      $scope.auth_landing_page = Authentication.auth_landing_page;
      $scope.role = Authentication.role;
    });

    init();

  }

]);

GLClient.controller('ModalCtrl', ['$scope', 
  function($scope, $modalInstance, error) {
    $scope.error = error;
    $scope.seconds = error.arguments[0];
}]);

TabCtrl = ['$scope', function($scope) {
  /* Empty controller function used to implement TAB pages */
}];

GLClient.controller('DisableEncryptionCtrl', ['$scope', '$modalInstance', function($scope, $modalInstance){
    $scope.close = function() {
      $modalInstance.close(false);
    };

    $scope.no = function() {
      $modalInstance.close(false);
    };
    $scope.ok = function() {
      $modalInstance.close(true);
    };

}]);

GLClient.controller('IntroCtrl', ['$scope', '$rootScope', '$modalInstance', function ($scope, $rootScope, $modalInstance) {

  var steps = 3;

  var first_step = 0;

  if ($scope.languages_enabled_length <= 1) {
     first_step = 1;
  }

  $scope.step = first_step;

  $scope.proceed = function () {
    if ($scope.step < steps) {
      $scope.step += 1;
    }
  };

  $scope.back = function () {
    if ($scope.step > first_step) {
      $scope.step -= 1;
    }
  };

  $scope.cancel = function () {
    $modalInstance.close();
  };

  $scope.data = {
    'language': $scope.language
  };

  $scope.$watch("data.language", function (newVal, oldVal) {
    if (newVal && newVal !== oldVal) {
      $rootScope.language = $scope.data.language;
    }
  });

}]);
