"use strict";

angular.module('resourceServices.authentication', [])
  .factory('Authentication', ['$q', '$http', '$location', '$routeParams',
                              '$rootScope', '$timeout', '$cookies', 'glcrypto',
    function($q, $http, $location, $routeParams, $rootScope, $timeout, $cookies, glcrypto) {
      function Session(){
        var self = this;

        var salt = 'salt!';

        var login_success = function(response, cb) {
          self.id = response.session_id;
          self.user_id = response.user_id;
          self.role = response.role;
          self.session = response.session;
          self.state = response.state;
          self.password_change_needed = response.password_change_needed;

          self.homepage = '';
          self.auth_landing_page = '';

          if (self.role == 'admin') {
              self.homepage = '/#/admin/landing';
              self.auth_landing_page = '/admin/landing';
          } else if (self.role == 'receiver') {
            self.homepage = '/#/receiver/tips';
            if (self.password_change_needed) {
                self.auth_landing_page = '/receiver/firstlogin';
            } else {
                self.auth_landing_page = '/receiver/tips';
            }
          } else if(self.role == 'wb') {
            self.auth_landing_page = '/status';
          }

          if (cb){
            return cb(response);
          }

          if ($routeParams['src']) {
            $location.path($routeParams['src']);
          } else {
            $location.path(self.auth_landing_page);
          }

          $location.search('');
        };

<<<<<<< HEAD
        $rootScope.login = function(username, userpassword, role, cb) {
=======
        $rootScope.login = function(username, password, role, cb) {

          if (role == 'receiver' && password != 'globaleaks') {
            var pwd = gl_password(password);
            var passphrase = gl_passphrase(password);
            $rootScope.receiver_key_passphrase = passphrase;
            password = pwd;
          }

          return $http.post('/authentication', {'username': username,
                                                'password': password,
                                                'role': role})
            .success(function(response) {
              self.id = response.session_id;
              self.user_id = response.user_id;
              self.username = username;
              self.role = response.role;
              self.session = response.session;
              self.state = response.state;
              self.password_change_needed = response.password_change_needed;

              self.homepage = '';
              self.auth_landing_page = '';

              if (self.role == 'admin') {
                  self.homepage = '/#/admin/landing';
                  self.auth_landing_page = '/admin/landing';
              }
              if (self.role == 'receiver') {
                self.homepage = '/#/receiver/activities';
                if (self.password_change_needed) {
                    self.auth_landing_page = '/receiver/firstlogin';
                } else {
                    self.auth_landing_page = '/receiver/activities';
                }
              }
              if (self.role == 'wb') {
                self.auth_landing_page = '/status';
              }
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

          self.username = username;
          self.password = userpassword;
          self.userpassword = userpassword;
          self.role = role;

          if (role != 'wb') {
            glcrypto.derivate_password(userpassword, salt).then(function(data1) {

              self.password = data1.stretched;

              glcrypto.derivate_passphrase(self.password, salt).then(function(data2) {
                self.passphrase = data2.stretchedy;
              });

              return $http.post('/authentication', {
                                                     'username': self.username,
                                                     'password': self.password,
                                                     'role': self.role
                                                   })
                .success(function(response) {
                  login_success(response, cb);
                })
                .error(function(response) {
                  // in case of error we test for old login method where the
                  // password was not subject to scrypt.
                  // this code should be kept temporarly until all nodes
                  // are migrated to use end2end.

                  $http.post('/authentication', {
                                                  'username': self.username,
                                                  'password': self.userpassword,
                                                  'role': self.role
                                                })
                    .success(function(response) {
                      login_success(response, cb);
                    })

                });
            });
          } else {
            return $http.post('/authentication', {
                                                   'username': self.username,
                                                   'password': self.userpassword,
                                                   'role': self.role
                                                 })
              .success(function(response) {
                login_success(response, cb);
              })
          }
        };

        self.logout_performed = function () {
          var role = self.role;

          self.id = null;
          self.user_id = null;
          self.username = null;
          self.role = null;
          self.session = null;
          self.homepage = null;
          self.auth_langing_page = null;

          if (role === 'wb') {
            $location.path('/');
          } else if (role === 'admin') {
            $location.path('/admin');
          } else {
            $location.path('/login');
          }
        };

        $rootScope.logout = function() {
          // we use $http['delete'] in place of $http.delete due to
          // the magical IE7/IE8 that do not allow delete as identifier
          // https://github.com/globaleaks/GlobaLeaks/issues/943
          $http['delete']('/authentication').then(self.logout_performed,
                                                  self.logout_performed);

        };

        self.get_auth_headers = function() {
          var h = {};

          if (self.id) {
            h['X-Session'] = self.id;
          }

          if ($cookies['XSRF-TOKEN']) {
            h['X-XSRF-TOKEN'] = $cookies['XSRF-TOKEN'];
          }

          if ($rootScope.language) {
            h['GL-Language'] = $rootScope.language;
          }

          return h;
        };

        $rootScope.get_auth_headers = self.get_auth_headers;

      };

      return new Session;
}]);

angular.module('resourceServices', ['ngResource', 'resourceServices.authentication']).
  factory('globalInterceptor', ['$q', '$injector', '$rootScope', '$location',
  function($q, $injector, $rootScope, $location) {
    var requestTimeout = 30000,
      $http = null, $modal = null;

    $rootScope.showRequestBox = false;
    
    function showModal(error) {
      $modal = $modal || $injector.get('$modal');
      var modalInstance = $modal.open({
        templateUrl: 'views/partials/error_popup.html',
        controller: 'ModalCtrl',
        resolve: {
          error: function() {
            return error;
          }
        }
      })
    };

    /* This interceptor is responsible for keeping track of the HTTP requests
     * that are sent and their result (error or not error) */
    return function(promise) {

      $http = $http || $injector.get('$http');

      $rootScope.pendingRequests = function () {
        return $http.pendingRequests.length;
      };

      $rootScope.showRequestBox = true;

      return promise.then(function(response) {

        if ($http.pendingRequests.length < 1) {
          $rootScope.showRequestBox = false;
        }

        return response;
      }, function(response) {
        /* 
           When the response has failed write the rootScope
           errors array the error message.
        */

        if ($http.pendingRequests.length < 1) {
          $rootScope.showRequestBox = false;
        }

        var error = {};
        var source_path = $location.path();

        error.message = response.data.error_message;
        error.code = response.data.error_code;
        error.url = response.config.url;
        error.arguments = response.data.arguments;
        
        // In here you should place the error codes that should trigger a modal
        // view.
        if (['55', '56', '57'].indexOf(error.code) != -1) {
          showModal(error); 
        }

        /* 30: Not Authenticated / 24: Wrong Authentication */
        if (error.code == 30 || error.code == 24) {

          if (error.code == 24) {
              $rootScope.logout();
          } else {
            var redirect_path = '/login';

            // If we are wb on the status page, redirect to homepage
            if (source_path === '/status') {
                redirect_path = '/';
            }
            // If we are admin on the /admin(/*) pages, redirect to /admin
            else if (source_path.indexOf('/admin') === 0) {
                redirect_path = '/admin';
            }

            // Only redirect if we are not alread on the login page
            if ($location.path() !== redirect_path) {
              $location.path(redirect_path);
              $location.search('src='+source_path);
            };
          }
        };

        if (!$rootScope.errors) {
          $rootScope.errors = [];
        }

        $rootScope.errors.push(error);

        return $q.reject(response);
      });
    }
}]).
  factory('GLCache',['$cacheFactory', function ($cacheFactory) {
    return $cacheFactory('GLCache');
}]).
  factory('Node', ['$resource', 'GLCache', function($resource, GLCache) {
    return $resource('/node', {}, {
      get: {
        method: 'GET',
        cache: GLCache
      }
    })
}]).
  factory('Contexts', ['$resource', 'GLCache', function($resource, GLCache) {
    return $resource('/contexts', {}, {
      get: {
        method: 'GET',
        cache: GLCache
      }
    })
}]).
  factory('Receivers', ['$resource', 'GLCache', function($resource, GLCache) {
    return $resource('/receivers', {}, {
      get: {
        method: 'GET',
        cache: GLCache
      }
    })
}]).
  // In here we have all the functions that have to do with performing
  // submission requests to the backend
  factory('Submission', ['$rootScope', '$resource', '$filter', '$location', 'Authentication', 'Node', 'Contexts', 'Receivers', 'glcrypto',
  function($rootScope, $resource, $filter, $location, Authentication, Node, Contexts, Receivers, glcrypto) {

    var submissionResource = $resource('/submission/:token_id/',
        {token_id: '@token_id'},
        {submit:
          {method: 'PUT'}
    });

    var isReceiverInContext = function(receiver, context) {
      return receiver.contexts.indexOf(context.id);
    };

    return function(fn, context_id, receivers_ids) {
      /**
       * This factory returns a Submission object that will call the fn
       * callback once all the information necessary for creating a submission
       * has been collected.
       *
       * This means getting the node information, the list of receivers and the
       * list of contexts.
       */
      var self = this,
        forEach = angular.forEach;

      self.contexts = [];
      self.receivers = [];
      self.current_context = undefined;
      self.maximum_filesize = null;
      self.allow_unencrypted = null;
      self.current_context_fields = [];
      self.current_context_receivers = [];
      self.current_submission = null; 
      self.receivers_selected = {};
<<<<<<< HEAD
      self.uploading = false;
      self.receivers_selected_keys = [];
      
      Authentication.whistleblower_keycode = glcrypto.generate_keycode();
      Authentication.whistleblower_e2e_key = undefined;
=======
      self.receivers_selected_keys = [];
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

      self.whistleblower_e2e_key_promise = glcrypto.generate_key_from_keycode(Authentication.whistleblower_keycode, 'salt!');
      
      var setCurrentContextReceivers = function() {
        self.receivers_selected = {};
        self.receivers_selected_keys = [];
        self.current_context_receivers = [];

<<<<<<< HEAD
        forEach(self.receivers, function(receiver) {
          // enumerate only the receivers of the current context and with pgp keys
          if (self.current_context.receivers.indexOf(receiver.id) !== -1 && receiver.pgp_e2e_public) {
=======
        forEach(self.receivers, function(receiver){
          // enumerate only the receivers of the current context and with pgp keys
          if (self.current_context.receivers.indexOf(receiver.id) !== -1 && receiver.pgp_glkey_pub) {
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
            self.current_context_receivers.push(receiver);

            if (!self.current_context.show_receivers) {
                self.receivers_selected[receiver.id] = true;
                return;
            }

            if (receivers_ids) {
              if (receivers_ids.indexOf(receiver.id) != -1) {
                self.receivers_selected[receiver.id] = true;
                return;
              }
            }

            if (receiver.configuration == 'default' && self.current_context.select_all_receivers) {
              self.receivers_selected[receiver.id] = true;
            } else if (receiver.configuration == 'forcefully_selected') {
              self.receivers_selected[receiver.id] = true;
            }
          }

        });
      };

      Node.get(function(node) {
        self.maximum_filesize = node.maximum_filesize;
        self.allow_unencrypted = node.allow_unencrypted;

        Contexts.query(function(contexts){
          self.contexts = contexts;
          if (context_id) {
            self.current_context = $filter('filter')(self.contexts, 
                                                     {"id": context_id})[0];
          }
          if (self.current_context === undefined) {
            self.current_context = $filter('orderBy')(self.contexts, 'presentation_order')[0];
          }
          Receivers.query(function(receivers){
            self.receivers = [];
            forEach(receivers, function(receiver){
              if (receiver.pgp_key_status !== 'enabled') {
                receiver.missing_pgp = true;
              }
              self.receivers.push(receiver);
            });
            setCurrentContextReceivers();
            fn(self); // Callback!
          });
        });
      });

      /**
       * @name Submission.create
       * @description
       * Create a new submission based on the currently selected context.
       *
       * */
      self.create = function(cb) {
        //TODO: encrypt wb_steps here also

        self.current_submission = new submissionResource({
          context_id: self.current_context.id,
<<<<<<< HEAD
          wb_steps: self.current_context.steps,
          receivers: [],
          human_captcha_answer: 0,
          wb_e2e_public: "",
          /* at the moment is just a fingerprint of the pubkey */
          wb_signature: ""
=======
          wb_steps: _.clone(self.current_context.steps),
          files: [], finalize: false, receivers: [],
          pgp_glkey_pub: "", pgp_glkey_priv: ""
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
        });

        setCurrentContextReceivers();

        self.current_submission.$save(function(submissionID){
          angular.forEach(self.current_context.fields, function(field, k) {
            if (field.type === "checkboxes") {
              self.current_context.fields[k].value = {};
            }
          });

          self.current_submission.wb_steps = self.current_context.steps;

          if (cb)
            cb();
        });
      };

      /**
       * @name Submission.submit
       * @description
       * Submit the currently configured submission.
       * This involves setting the receivers of the submission object to those
       * currently selected and setting up the submission fields entered by the
       * whistleblower.
       */
      self.submit = function() {
        if (!self.receivers_selected) {
          return;
        }

        if (!self.current_submission) {
          return;
        }

        // Set the currently selected pgp pub keys
        self.receivers_selected_keys = [];
<<<<<<< HEAD
        forEach(self.receivers_selected, function(selected, id){
          if (selected) {
            forEach(self.receivers, function(receiver){
              if (id == receiver.id) {
                self.receivers_selected_keys.push(receiver.pgp_e2e_public);
=======
        _.each(self.receivers_selected, function(selected, id){
          if (selected) {
            _.each(self.receivers, function(receiver){
              if (id == receiver.id) {
                self.receivers_selected_keys.push(receiver.pgp_glkey_pub);
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
              }
            });
          }
        });

        // Set the currently selected receivers
        self.receivers = [];
        // remind this clean the collected list of receiver_id
        self.current_submission.receivers = [];
        angular.forEach(self.receivers_selected, function(selected, id){
          if (selected) {
            self.current_submission.receivers.push(id);
          }
        });

<<<<<<< HEAD
        openpgp.config.show_comment = false;
        openpgp.config.show_version = false;

        self.whistleblower_e2e_key_promise.then(
          function(keyPair) {
            Authentication.whistleblower_e2e_key = keyPair;
            self.current_submission.finalize = true;
            self.current_submission.wb_e2e_public = keyPair.publicKeyArmored;
            self.current_submission.wb_signature = keyPair.key.primaryKey.fingerprint;
            self.current_submission.is_e2e_encrypted = true;

            var receivers_and_wb_keys = [];
            forEach(self.receivers_selected_keys, function(key) {
              var r_key_pub = openpgp.key.readArmored(key).keys[0];
              receivers_and_wb_keys.push(r_key_pub);
            });
            var wb_key_pub = openpgp.key.readArmored(keyPair.publicKeyArmored).keys[0];
            receivers_and_wb_keys.push(wb_key_pub);

            var wb_steps = JSON.stringify(self.current_submission.wb_steps);
            openpgp.encryptMessage(receivers_and_wb_keys, wb_steps).then(function(pgp_wb_steps) {
              var list_wb_steps = [];
              list_wb_steps.push(pgp_wb_steps);
              self.current_submission.wb_steps = list_wb_steps;

                self.current_submission.$submit(function(result) {
                  if (result) {
                    $location.url("/receipt");
                  }
                });

            });
          }
        );
=======
        //TODO: generate receipt and passphrase
        openpgp.config.show_comment = false;
        openpgp.config.show_version = false;
        openpgp.generateKeyPair({
            numBits: 2048,
            //passphrase: "",
            userId: "somebody@somewhere.com" }).then( function(tkp) {

            self.current_submission.finalize = true;
            self.current_submission.pgp_glkey_pub = tkp.publicKeyArmored;
            self.current_submission.pgp_glkey_priv = tkp.privateKeyArmored;

            console.log('receivers_selected_keys ', self.receivers_selected_keys);
            var receivers_and_wb_keys = [];
            _.each(self.receivers_selected_keys, function(key) {
                var r_key_pub = openpgp.key.readArmored(key).keys[0];
                receivers_and_wb_keys.push( r_key_pub );
            });
            var wb_key_pub = openpgp.key.readArmored( tkp.publicKeyArmored ).keys[0];
            receivers_and_wb_keys.push( wb_key_pub );
            console.log('Submission receivers_and_wb_keys ', receivers_and_wb_keys);

            var wb_steps = JSON.stringify(self.current_submission.wb_steps);
            //console.log(wb_steps);

            openpgp.encryptMessage(receivers_and_wb_keys, wb_steps).then( function(pgp_wb_steps) {
                var list_wb_steps = [];
                list_wb_steps.push(pgp_wb_steps);
                self.current_submission.wb_steps = list_wb_steps;

                self.current_submission.$submit(function(result) {
                    if (result) {
                        Authentication.keycode = self.current_submission.receipt;
                        $location.url("/receipt");
                    }
                });

            });

      });
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

      };

    };

}]).
  factory('Tip', ['$resource', '$rootScope', 'Receivers', 'ReceiverPreferences',
<<<<<<< HEAD
  function($resource, $rootScope, Receivers, ReceiverPreferences) {
=======
          function($resource, $rootScope, Receivers, ReceiverPreferences) {
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

    var tipResource = $resource('/rtip/:tip_id', {tip_id: '@id'}, {update: {method: 'PUT'}});
    var receiversResource = $resource('/rtip/:tip_id/receivers', {tip_id: '@tip_id'}, {});
    var commentsResource = $resource('/rtip/:tip_id/comments', {tip_id: '@tip_id'}, {});
    var messageResource = $resource('/rtip/:tip_id/messages', {tip_id: '@tip_id'}, {});

    return function(tipID, fn) {
      var self = this,
<<<<<<< HEAD
        forEach = angular.forEach;
=======
      forEach = angular.forEach;
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
      self.tip = {};
      
      ReceiverPreferences.get(function(preferences){

<<<<<<< HEAD
      ReceiverPreferences.get(function(preferences){
        // decrypt receiver priv key
        self.privateKey = openpgp.key.readArmored(preferences.pgp_e2e_private).keys[0];
        var ret = self.privateKey.decrypt($rootScope.receiver_key_passphrase);
=======
      tipResource.get(tipID, function(result){

        var privateKey = openpgp.key.readArmored( preferences.pgp_glkey_priv ).keys[0];
        // decrypt receiver priv key
        var ret = privateKey.decrypt( $rootScope.receiver_key_passphrase );
        console.log('decrypted receiver privateKey ', ret);

        openpgp.config.show_comment = false;
        openpgp.config.show_version = false;

        var pgpMessage = openpgp.message.readArmored( result.wb_steps[0] );
        openpgp.decryptMessage(privateKey, pgpMessage).then(function(decr_wb_steps) {

        receiversResource.query(tipID, function(receiversCollection){
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

        tipResource.get(tipID, function(result){
          self.tip = result;
<<<<<<< HEAD
=======
          var json_wb_steps = JSON.parse(decr_wb_steps);
          self.tip.wb_steps = json_wb_steps;

>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
          self.tip.comments = [];
          self.tip.messages = [];
          self.tip.receivers = receiversCollection;
          self.receivers_and_wb_keys = [];

          // build receivers and wb pub keys list
          _.each(receiversCollection, function(receiver) {
                var r_key_pub = openpgp.key.readArmored(receiver.pgp_glkey_pub).keys[0];
                self.receivers_and_wb_keys.push( r_key_pub );
          });
          var wb_key_pub = openpgp.key.readArmored( self.tip.pgp_glkey_pub ).keys[0];
          self.receivers_and_wb_keys.push( wb_key_pub );

          if (typeof(result.wb_steps[0]) == 'string'
              && result.wb_steps[0].indexOf("-----BEGIN PGP MESSAGE-----") == 0) {
						var pgpMessage = openpgp.message.readArmored(result.wb_steps[0]);
						openpgp.decryptMessage(self.privateKey, pgpMessage).then(function(decr_wb_steps) {
                var json_wb_steps = JSON.parse(decr_wb_steps);
                self.tip.wb_steps = json_wb_steps;
            });
          } else {
                self.tip.wb_steps = result.wb_steps;
          }

<<<<<<< HEAD
          receiversResource.query(tipID, function(receiversCollection){
            self.tip.receivers = receiversCollection;
            self.cleartext_message = '';
            self.cleartext_comment = '';

            // build receivers and wb pub keys list
            self.receivers_and_wb_keys = [];
            forEach(receiversCollection, function(receiver) {
                var r_key_pub = openpgp.key.readArmored(receiver.pgp_e2e_public).keys[0];
                self.receivers_and_wb_keys.push(r_key_pub);
=======
          self.tip.newMessage = function(content) {
            openpgp.encryptMessage(self.receivers_and_wb_keys, content).then( function(pgp_content) {

              var m = new messageResource(tipID);
              m.content = pgp_content;
              m.$save(function(newMessage) {
                self.tip.messages.unshift(newMessage);
              });

>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
            });
            var wb_key_pub = openpgp.key.readArmored(self.tip.wb_e2e_public).keys[0];
            self.receivers_and_wb_keys.push(wb_key_pub);

            self.tip.newComment = function(content) {
              openpgp.encryptMessage(self.receivers_and_wb_keys, content).then(function(pgp_content) {
                var c = new commentsResource(tipID);
                c.content = pgp_content;
                self.clearc = content;
                c.$save(function(newComment) {
                  newComment.content = self.clearc;
                  self.tip.comments.unshift(newComment);
                  self.clearc = '';
                });
              });
            };

<<<<<<< HEAD
            self.tip.newMessage = function(content) {
              openpgp.encryptMessage(self.receivers_and_wb_keys, content).then(function(pgp_content) {
                var m = new messageResource(tipID);
                m.content = pgp_content;
                self.clearm = content;
                m.$save(function(newMessage) {
                  self.tip.messages.unshift(newMessage);
                  self.clearm = '';
                });
              });
            };

            messageResource.query(tipID, function(messageCollection){
              forEach(messageCollection, function(message) {
                if (typeof(message.content) == 'string'
                    && message.content.indexOf("-----BEGIN PGP MESSAGE-----") == 0) {
                  var pgpMessage = openpgp.message.readArmored(message.content);
                  openpgp.decryptMessage(self.privateKey, pgpMessage).then(function(decr_content) {
                    message.content = decr_content;
                  }, function(error) {
                    message.content = 'decryptMessage error: ', error;
                  });
                }
              });
              self.tip.messages = messageCollection;
              fn(self.tip);
            });
=======
          messageResource.query(tipID, function(messageCollection){
            _.each(messageCollection, function(message) {

              if ( message.content.indexOf("-----BEGIN PGP MESSAGE-----") > -1 ) {
                var pgpMessage = openpgp.message.readArmored( message.content );
                openpgp.decryptMessage(privateKey, pgpMessage).then(function(decr_content) {
                  message.content = decr_content;
                }, function(error) {
                  console.log('decryptMessage error: ', error);
                });
              }

            });

            self.tip.messages = messageCollection;
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

            commentsResource.query(tipID, function(commentsCollection){
              forEach(commentsCollection, function(comment) {
                if (typeof(comment.content) == 'string'
                    && comment.content.indexOf("-----BEGIN PGP MESSAGE-----") == 0) {
                  var pgpMessage = openpgp.message.readArmored(comment.content);
                  openpgp.decryptMessage(self.privateKey, pgpMessage).then(function(decr_content) {
                    comment.content = decr_content;
                  }, function(error) {
                    comment.content = 'decryptMessage error: ', error;
                  });
                }
              });
              self.tip.comments = commentsCollection;
              fn(self.tip);
            });

<<<<<<< HEAD
          }); // receiverResource
=======
          commentsResource.query(tipID, function(commentsCollection){
            self.tip.comments = commentsCollection;
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

        }); // tipResource

<<<<<<< HEAD
      }); // ReceiverPreferences
=======
        });

        }); // openpgp decrypt

      }); // ReceiverPreferences

      });
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

    };

	}]).

  factory('WBTip', ['$resource', 'Receivers', 'Authentication',
	function($resource, Receivers, Authentication) {

    var forEach = angular.forEach;

    var tipResource = $resource('/wbtip', {}, {update: {method: 'PUT'}});
    var receiversResource = $resource('/wbtip/receivers', {}, {});
    var commentsResource = $resource('/wbtip/comments', {}, {});
    var messageResource = $resource('/wbtip/messages/:id', {id: '@id'}, {});

    return function(fn) {
      var self = this;
<<<<<<< HEAD
      self.keycode = Authentication.whistleblower_keycode;
      self.keyPair = Authentication.whistleblower_e2e_key;
=======
      self.tip = {};
      var privateKey = null;
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

      tipResource.get(function(result) {
        var pgpMessage = openpgp.message.readArmored(result.wb_steps[0]);
        self.privateKey = openpgp.key.readArmored(self.keyPair.privateKeyArmored).keys[0];

<<<<<<< HEAD
        openpgp.config.show_comment = false;
        openpgp.config.show_version = false;

        openpgp.decryptMessage(self.privateKey, pgpMessage).then(function(decr_wb_steps) {

          receiversResource.query(function(receiversCollection) {

            self.tip = result;
            var json_wb_steps = JSON.parse(decr_wb_steps);
            self.tip.wb_steps = json_wb_steps;
            self.receivers_and_wb_keys = [];

            var wb_key_pub = openpgp.key.readArmored(self.tip.wb_e2e_public).keys[0];
            self.receivers_and_wb_keys.push(wb_key_pub);

            self.tip.comments = [];
            self.tip.messages = [];
            self.tip.receivers = [];
            self.tip.msg_receivers_selector = [];
            self.tip.msg_receiver_selected = null;
            self.tip.receivers = receiversCollection;

            // build receivers and wb pub keys list
            forEach(receiversCollection, function(receiver) {
                var r_key_pub = openpgp.key.readArmored(receiver.pgp_e2e_public).keys[0];
                self.receivers_and_wb_keys.push(r_key_pub);
=======
        privateKey = openpgp.key.readArmored( result.pgp_glkey_priv ).keys[0];
        //TODO: decrypt key with receipt, now it is in unencrypted
        var pgpMessage = openpgp.message.readArmored( result.wb_steps[0] );

        openpgp.config.show_comment = false;
        openpgp.config.show_version = false;
        openpgp.decryptMessage(privateKey, pgpMessage).then(function(decr_wb_steps) {

        receiversResource.query(function(receiversCollection) {

          self.tip = result;
          var json_wb_steps = JSON.parse(decr_wb_steps);
          self.tip.wb_steps = json_wb_steps;

          self.tip.comments = [];
          self.tip.messages = [];
          self.tip.receivers = [];
          self.tip.msg_receivers_selector = [];
          self.tip.msg_receiver_selected = null;
          self.tip.receivers = receiversCollection;
          self.receivers_and_wb_keys = [];

          // build receivers and wb pub keys list
          _.each(receiversCollection, function(receiver) {
                var r_key_pub = openpgp.key.readArmored(receiver.pgp_glkey_pub).keys[0];
                self.receivers_and_wb_keys.push( r_key_pub );
          });
          var wb_key_pub = openpgp.key.readArmored( self.tip.pgp_glkey_pub ).keys[0];
          self.receivers_and_wb_keys.push( wb_key_pub );

          self.tip.newComment = function(content) {
            var c = new commentsResource();
            c.content = content;
            c.$save(function(newComment) {
              self.tip.comments.unshift(newComment);
            });
          };

          self.tip.newMessage = function(content) {
            openpgp.encryptMessage(self.receivers_and_wb_keys, content).then( function(pgp_content) {

              var m = new messageResource({id: self.tip.msg_receiver_selected});
              m.content = pgp_content;
              m.$save(function(newMessage) {
                self.tip.messages.unshift(newMessage);
              });

>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
            });

<<<<<<< HEAD
            self.tip.newComment = function(content) {
              openpgp.encryptMessage(self.receivers_and_wb_keys, content).then(function(pgp_content) {
                var c = new commentsResource();
                c.content = pgp_content;
                self.clearc = content;
                c.$save(function(newComment) {
                  newComment.content = self.clearc;
                  self.tip.comments.unshift(newComment);
                  self.clearc = '';
                });
              });
            };

            self.tip.newMessage = function(content) {
              openpgp.encryptMessage(self.receivers_and_wb_keys, content).then(function(pgp_content) {
                var m = new messageResource({id: self.tip.msg_receiver_selected});
                m.content = pgp_content;
                self.clearm = content;
                m.$save(function(newMessage) {
                  self.tip.messages.unshift(newMessage);
                  self.clearm = '';
                });
              });
            };
=======
          self.tip.updateMessages = function () {
            if (self.tip.msg_receiver_selected) {
              messageResource.query({id: self.tip.msg_receiver_selected}, function (messageCollection) {
                _.each(messageCollection, function(message) {

                  if ( message.content.indexOf("-----BEGIN PGP MESSAGE-----") > -1 ) {
                    var pgpMessage = openpgp.message.readArmored( message.content );
                    openpgp.decryptMessage(privateKey, pgpMessage).then(function(decr_content) {
                      message.content = decr_content;
                    });
                  }

                });

                self.tip.messages = messageCollection;
              });
            };
          };

          commentsResource.query({}, function(commentsCollection){
            self.tip.comments = commentsCollection;
          })
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

            self.tip.updateMessages = function () {
              if (self.tip.msg_receiver_selected) {
                messageResource.query({id: self.tip.msg_receiver_selected}, function (messageCollection) {
                  forEach(messageCollection, function(message) {
                    if (message.content.indexOf("-----BEGIN PGP MESSAGE-----") > -1) {
                      var pgpMessage = openpgp.message.readArmored(message.content);
                      openpgp.decryptMessage(self.privateKey, pgpMessage).then(function(decr_content) {
                        message.content = decr_content;
                      });
                    }
                  });
                  self.tip.messages = messageCollection;
                });
              };
            };

            commentsResource.query({}, function(commentsCollection) {
              forEach(commentsCollection, function(comment) {
                if (typeof(comment.content) == 'string'
                    && comment.content.indexOf("-----BEGIN PGP MESSAGE-----") == 0) {
                  var pgpMessage = openpgp.message.readArmored(comment.content);
                  openpgp.decryptMessage(self.privateKey, pgpMessage).then(function(decr_content) {
                    comment.content = decr_content;
                  }, function(error) {
                    comment.content = 'decryptMessage error: ', error;
                  });
                }
              });
              self.tip.comments = commentsCollection;
              fn(self.tip);
            });

          }); //receiversResource

<<<<<<< HEAD
        }); //decryptMessage

      }); //tipResource

    };
=======
          fn(self.tip);
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

}]).
  factory('WBReceipt', ['$rootScope', 'Authentication', 'glcrypto',
    function($rootScope, Authentication, glcrypto){
      return function(keycode, fn) {
        function login() {
          var fp = Authentication.whistleblower_e2e_key.key.primaryKey.fingerprint;
          $rootScope.login('', fp, 'wb', fn);
        }
        if (Authentication.whistleblower_e2e_key) {
          login();
        } else {
          glcrypto.generate_key_from_keycode(keycode, 'salt!').then(
            function(keyPair) {
              Authentication.whistleblower_keycode = keycode;
              Authentication.whistleblower_e2e_key = keyPair;
              login();
            }
          );
        }
      };
}]).
  factory('ReceiverPreferences', ['$resource', '$rootScope', '$location', 'glcrypto',
    function($resource, $rootScope, $location, glcrypto) {
    var ret = $resource('/receiver/preferences', {}, {'update': {method: 'PUT'}});

    ret.generate_and_save_key = function(preferences) {
      glcrypto.generate_e2e_key(preferences.password, "salt!").then(function(data) {
        if (preferences.pgp_key_remove == undefined) {
          preferences.pgp_key_remove = false;
        }

        if (preferences.pgp_key_public == undefined) {
          preferences.pgp_key_public = '';
        }

        preferences.password = data.password;
        preferences.check_password = data.password;
        preferences.pgp_e2e_public = data.e2e_key_pub;
        preferences.pgp_e2e_private = data.e2e_key_prv;

        preferences.$update(function () {
          if (!$rootScope.successes) {
            $rootScope.successes = [];
          }
          $rootScope.successes.push({message: 'Updated your password!'});
          $location.path("/receiver/tips");
        });

        }); //openpgp decrypt

      });
    }

    return ret;
}]).
  factory('ReceiverTips', ['$resource', function($resource) {
    return $resource('/receiver/tips', {}, {'update': {method: 'PUT'}});
}]).
  factory('ReceiverNotification', ['$resource', function($resource) {
    return $resource('/receiver/notifications');
}]).
  factory('ReceiverOverview', ['$resource', function($resource) {
    return $resource('/admin/overview/users');
}]).
  factory('Admin', ['$resource', function($resource) {
    var self = this,
      forEach = angular.forEach;

    function Admin() {
      var self = this,
        adminContextsResource = $resource('/admin/contexts'),
        adminContextResource = $resource('/admin/context/:context_id',
          {context_id: '@id'},
          {
            update: {
              method: 'PUT'
            }
          }
        ),
        adminFieldsResource = $resource('/admin/fields'),
        adminFieldResource = $resource('/admin/field/:field_id', 
          {field_id: '@id'},
          {
            update: {
              method: 'PUT' 
            }
          }
        ),
        adminFieldTemplatesResource = $resource('/admin/fieldtemplates'),
        adminFieldTemplateResource = $resource('/admin/fieldtemplate/:template_id',
          {template_id: '@id'},
          {
            update: {
              method: 'PUT' 
            }
          }
        ),
        adminReceiversResource = $resource('/admin/receivers'),
        adminReceiverResource = $resource('/admin/receiver/:receiver_id',
          {receiver_id: '@id'},
          {
            update: {
              method: 'PUT'
            }
          }
        ),
        adminNodeResource = $resource('/admin/node', {}, {update: {method: 'PUT'}}),
        adminNotificationResource = $resource('/admin/notification', {}, {update: {method: 'PUT'}});

      adminNodeResource.prototype.toString = function() { return "Admin Node"; };
      adminContextsResource.prototype.toString = function() { return "Admin Contexts"; };
      adminContextResource.prototype.toString = function() { return "Admin Context"; };
      adminFieldResource.prototype.toString = function() { return "Admin Field"; };
      adminFieldsResource.prototype.toString = function() { return "Admin Fields"; };
      adminFieldTemplateResource.prototype.toString = function() { return "Admin Field Template"; };
      adminFieldTemplatesResource.prototype.toString = function() { return "Admin Field Templates"; };
      adminReceiversResource.prototype.toString = function() { return "Admin Receivers"; };
      adminReceiverResource.prototype.toString = function() { return "Admin Receiver"; };
      adminNotificationResource.prototype.toString = function() { return "Admin Notification"; };

      self.context = adminContextResource;
      self.contexts = adminContextsResource.query();

      self.new_context = function() {
        var context = new adminContextResource;
        context.name = "";
        context.description = "";
        context.steps = [];
        context.receivers = [];
        context.select_all_receivers = false;
        context.tip_timetolive = 15;
        context.receiver_introduction = "";
        context.can_postpone_expiration = true;
        context.can_delete_submission = true;
        context.maximum_selectable_receivers = 0;
        context.show_small_cards = false;
        context.show_receivers = true;
        context.enable_private_messages = true;
        context.presentation_order = 0;
        context.show_receivers_in_alphabetical_order = false;
        context.reset_steps = false;
        return context;
      };

      self.template_fields = {};
      self.field_templates = adminFieldTemplatesResource.query(function(){
        angular.forEach(self.field_templates, function(field){
          self.template_fields[field.id] = field;
        });
      });

      self.fields = adminFieldsResource.query();
      
      self.new_field = function(step_id) {
        var field = new adminFieldResource;
        field.label = '';
        field.type = '';
        field.description = '';
        field.is_template = false;
        field.hint = '';
        field.multi_entry = false;
        field.options = [];
        field.required = false;
        field.preview = false;
        field.stats_enabled = false;
        field.x = 0;
        field.y = 0;
        field.children = [];
        field.fieldgroup_id = '';
        field.step_id = step_id;
        return field;
      };

      self.new_field_from_template = function(template_id, step_id) {
        var field = new adminFieldResource;
        field.step_id = step_id;
        field.template_id = template_id;
        return field.$save();
      };

      self.new_field_template = function () {
        var field = new adminFieldTemplateResource;
        field.label = '';
        field.type = '';
        field.description = '';
        field.is_template = true;
        field.hint = '';
        field.multi_entry = false;
        field.options = [];
        field.required = false;
        field.preview = false;
        field.stats_enabled = false;
        field.x = 0;
        field.y = 0;
        field.children = [];
        field.fieldgroup_id = '';
        field.step_id = '';
        return field;
      };

      self.fill_default_field_options = function(field) {
        if (field.type == 'tos') {
          field.options.push({'attrs':
            {
              'clause': '',
              'agreement_statement': ''
            }
          });
        }
      };

      self.receiver = adminReceiverResource;
      self.receivers = adminReceiversResource.query();

      self.new_receiver = function () {
        var receiver = new adminReceiverResource;
        receiver.password = '';
        receiver.contexts = [];
        receiver.description = '';
        receiver.mail_address = '';
        receiver.ping_mail_address = '';
        receiver.can_delete_submission = false;
        receiver.can_postpone_expiration = false;
        receiver.tip_notification = true;
        receiver.ping_notification = false;
<<<<<<< HEAD
        receiver.pgp_key_info = '';
        receiver.pgp_key_fingerprint = '';
        receiver.pgp_key_remove = false;
        receiver.pgp_key_public = '';
        receiver.pgp_key_expiration = '';
        receiver.pgp_key_status = 'ignored';
        receiver.pgp_enable_notification = false;
        receiver.pgp_key_public = '';
        receiver.pgp_e2e_public = '';
        receiver.pgp_e2e_private = '';
=======
        receiver.gpg_key_info = '';
        receiver.gpg_key_fingerprint = '';
        receiver.gpg_key_remove = false;
        receiver.gpg_key_armor = '';
        receiver.gpg_key_expiration = '';
        receiver.gpg_key_status = 'ignored';
        receiver.gpg_enable_notification = false;
        receiver.pgp_key_armor_priv = '';
        receiver.pgp_glkey_pub = '';
        receiver.pgp_glkey_priv = '';
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
        receiver.presentation_order = 0;
        receiver.state = 'enable';
        receiver.configuration = 'default';
        receiver.password_change_needed = true;
        receiver.language = 'en';
        receiver.timezone = '0';
        return receiver;
      };

      self.node = adminNodeResource.get(function(){
        self.node.password = '';
        self.node.old_password = '';
      });

      self.fieldtemplate = adminFieldTemplateResource;
      self.field = adminFieldResource;

      self.notification = adminNotificationResource.get();
    }
    return Admin;

}]).
  factory('TipOverview', ['$resource', function($resource) {
    return $resource('/admin/overview/tips');
}]).
  factory('FileOverview', ['$resource', function($resource) {
    return $resource('/admin/overview/files');
}]).
  factory('StatsCollection', ['$resource', function($resource) {
    return $resource('/admin/stats/:week_delta', {week_delta: '@week_delta'}, {});
}]).
  factory('AnomaliesCollection', ['$resource', function($resource) {
    return $resource('/admin/anomalies');
}]).
  factory('AnomaliesHistCollection', ['$resource', function($resource) {
    return $resource('/admin/history');
}]).
  factory('ActivitiesCollection', ['$resource', function($resource) {
    return $resource('/admin/activities/details');
}]).
  factory('StaticFiles', ['$resource', function($resource) {
    return $resource('/admin/staticfiles');
}]).
  factory('DefaultAppdata', ['$resource', function($resource) {
    return $resource('/data/appdata_l10n.json', {});
}]).
  factory('passwordWatcher', ['$parse', function($parse) {
    return function(scope, password) {
      /** This is used to watch the new password and check that is
       *  effectively the same. Sets a local variable mismatch_password.
       *
       *  @param {obj} scope the scope under which we should register watchers
       *                     and insert the mismatch_password field.
       *  @param {string} old_password the old password model name.
       *  @param {string} password the new password model name.
       *  @param {string} check_password need to be equal to the new password.
       **/
      scope.mismatch_password = false;
      scope.unsafe_password = false;
      scope.pwdValidLength = true;
      scope.pwdHasLetter = true;
      scope.pwdHasNumber = true;

      var validatePasswordChange = function () {
        if (scope.$eval(password) !== undefined && scope.$eval(password) != '') {
          scope.pwdValidLength = (scope.$eval(password)).length >= 8;
          scope.pwdHasLetter = (/[A-z]/.test(scope.$eval(password))) ? true : false;
          scope.pwdHasNumber = (/\d/.test(scope.$eval(password))) ? true : false;
          scope.unsafe_password = !(scope.pwdValidLength && scope.pwdHasLetter && scope.pwdHasNumber);
        } else {
          /*
           * This values permits to not show errors when
           * the user has not yed typed any password.
           */
          scope.unsafe_password = false;
          scope.pwdValidLength = true;
          scope.pwdHasLetter = true;
          scope.pwdHasNumber = true;
        }
      };

      scope.$watch(password, function(){
          validatePasswordChange();
      }, true);

    }
}]).
  factory('changePasswordWatcher', ['$parse', function($parse) {
    return function(scope, old_password, password, check_password) {
      /** This is used to watch the new password and check that is
       *  effectively the same. Sets a local variable mismatch_password.
       *
       *  @param {obj} scope the scope under which we should register watchers
       *                     and insert the mismatch_password field.
       *  @param {string} old_password the old password model name.
       *  @param {string} password the new password model name.
       *  @param {string} check_password need to be equal to the new password.
       **/

      scope.invalid = true;

      scope.mismatch_password = false;
      scope.missing_old_password = false;
      scope.unsafe_password = false;

      scope.pwdValidLength = true;
      scope.pwdHasLetter = true;
      scope.pwdHasNumber = true;

      var validatePasswordChange = function () {

        if (scope.$eval(password) !== undefined && scope.$eval(password) != '') {
          scope.pwdValidLength = (scope.$eval(password)).length >= 8;
          scope.pwdHasLetter = (/[A-z]/.test(scope.$eval(password))) ? true : false;
          scope.pwdHasNumber = (/\d/.test(scope.$eval(password))) ? true : false;
          scope.unsafe_password = !(scope.pwdValidLength && scope.pwdHasLetter && scope.pwdHasNumber);
        } else {
          /*
           * This values permits to not show errors when
           * the user has not yed typed any password.
           */
          scope.unsafe_password = false;
          scope.pwdValidLength = true;
          scope.pwdHasLetter = true;
          scope.pwdHasNumber = true;
        }

        if (scope.$eval(password) === undefined ||
          scope.$eval(password) === '' ||
          scope.$eval(password) === scope.$eval(check_password)) {
          scope.mismatch_password = false;
        } else {
          scope.mismatch_password = true;
        }

        if (scope.$eval(old_password) !== undefined && (scope.$eval(old_password)).length >= 1) {
          scope.missing_old_password = false;
        } else {
          scope.missing_old_password = true;
        }

        scope.invalid = scope.$eval(password) === undefined ||
          scope.$eval(password) === '' ||
          scope.mismatch_password ||
          scope.unsafe_password ||
          scope.missing_old_password;
      };

      scope.$watch(password, function(){
          validatePasswordChange();
      }, true);

      scope.$watch(old_password, function(){
          validatePasswordChange();
      }, true);

      scope.$watch(check_password, function(){
          validatePasswordChange();
      }, true);

    }
}]).
  constant('CONSTANTS', {
     /* email regexp is an edited version of angular.js input.js in order to avoid domains with not tld */ 
     "email_regexp": /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/i,
     "https_regexp": /^(https:\/\/([a-z0-9-]+)\.(.*)$|^)$/,
     "http_or_https_regexp": /^(http(s?):\/\/([a-z0-9-]+)\.(.*)$|^)$/,
     "timezones": [
        {"timezone": -12.0, "label": "(GMT -12:00) Eniwetok, Kwajalein"},
        {"timezone": -11.0, "label": "(GMT -11:00) Midway Island, Samoa"},
        {"timezone": -10.0, "label": "(GMT -10:00) Hawaii"},
        {"timezone": -9.0, "label": "(GMT -9:00) Alaska"},
        {"timezone": -8.0, "label": "(GMT -8:00) Pacific Time (US &amp; Canada)"},
        {"timezone": -7.0, "label": "(GMT -7:00) Mountain Time (US &amp; Canada)"},
        {"timezone": -6.0, "label": "(GMT -6:00) Central Time (US &amp; Canada), Mexico City"},
        {"timezone": -5.0, "label": "(GMT -5:00) Eastern Time (US &amp; Canada), Bogota, Lima"},
        {"timezone": -4.0, "label": "(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz"},
        {"timezone": -3.5, "label": "(GMT -3:30) Newfoundland"},
        {"timezone": -3.0, "label": "(GMT -3:00) Brazil, Buenos Aires, Georgetown"},
        {"timezone": -2.0, "label": "(GMT -2:00) Mid-Atlantic"},
        {"timezone": -1.0, "label": "(GMT -1:00 hour) Azores, Cape Verde Islands"},
        {"timezone": 0.0, "label": "(GMT) Western Europe Time, London, Lisbon, Casablanca"},
        {"timezone": 1.0, "label": "(GMT +1:00 hour) Brussels, Copenhagen, Madrid, Paris"},
        {"timezone": 2.0, "label": "(GMT +2:00) Kaliningrad, South Africa"},
        {"timezone": 3.0, "label": "(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg"},
        {"timezone": 3.5, "label": "(GMT +3:30) Tehran"},
        {"timezone": 4.0, "label": "(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi"},
        {"timezone": 4.5, "label": "(GMT +4:30) Kabul"},
        {"timezone": 5.0, "label": "(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent"},
        {"timezone": 5.5, "label": "(GMT +5:30) Bombay, Calcutta, Madras, New Delhi"},
        {"timezone": 5.75, "label": "(GMT +5:45) Kathmandu"},
        {"timezone": 6.0, "label": "(GMT +6:00) Almaty, Dhaka, Colombo"},
        {"timezone": 7.0, "label": "(GMT +7:00) Bangkok, Hanoi, Jakarta"},
        {"timezone": 8.0, "label": "(GMT +8:00) Beijing, Perth, Singapore, Hong Kong"},
        {"timezone": 9.0, "label": "(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk"},
        {"timezone": 9.5, "label": "(GMT +9:30) Adelaide, Darwin"},
        {"timezone": 10.0, "label": "(GMT +10:00) Eastern Australia, Guam, Vladivostok"},
        {"timezone": 11.0, "label": "(GMT +11:00) Magadan, Solomon Islands, New Caledonia"},
        {"timezone": 12.0, "label": "(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka"}
     ]
}).
  config(['$httpProvider', function($httpProvider) {
    $httpProvider.responseInterceptors.push('globalInterceptor');
}]);
