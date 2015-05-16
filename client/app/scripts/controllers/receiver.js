GLClient.controller('ReceiverSidebarCtrl', ['$scope', '$location', function($scope, $location){

  var current_menu = $location.path().split('/').slice(-1);
  $scope.active = {};
  $scope.active[current_menu] = "active";
}]);

GLClient.controller('ReceiverFirstLoginCtrl', ['$scope', '$rootScope', '$location', 'ReceiverPreferences', 'changePasswordWatcher', 'glcrypto',
  function($scope, $rootScope, $location, ReceiverPreferences, changePasswordWatcher, glcrypto) {

    $scope.preferences = ReceiverPreferences.get();

    changePasswordWatcher($scope, "preferences.old_password",
        "preferences.password", "preferences.check_password");

<<<<<<< HEAD
    $scope.pass_save = function() {
      ReceiverPreferences.generate_and_save_key($scope.preferences);
=======
    $scope.pass_save = function () {
      // avoid changing any GPG setting - TODO: ???
      $scope.preferences.gpg_key_remove = false;
      $scope.preferences.gpg_key_armor = '';

      var new_password = gl_password($scope.preferences.password);
      var new_passphrase = gl_passphrase($scope.preferences.password);
      console.log('first login password ', $scope.preferences.password, ' ', new_password);
      console.log('first login passphrase ', new_passphrase);

      //$scope.preferences.old_password = old_pwd;
      $scope.preferences.password = new_password;
      $scope.preferences.check_password = new_password;

      //TODO: add e-mail
      var k_user_id = $scope.preferences.email;
      var k_user_id = 'fake@email.com';
      var k_passphrase = new_passphrase;
      var k_bits = 2048;

      openpgp.config.show_version = false;
      openpgp.config.show_comment = false;

      key = openpgp.generateKeyPair({   numBits: k_bits,
                                        userId: k_user_id,
                                        passphrase: k_passphrase }).then(function(keyPair) {

            $scope.preferences.pgp_glkey_pub = keyPair.publicKeyArmored;
            $scope.preferences.pgp_glkey_priv = keyPair.privateKeyArmored;

            $scope.preferences.$update(function () {
                if (!$rootScope.successes) {
                    $rootScope.successes = [];
                }
                $rootScope.successes.push({message: 'Updated your password!'});
                $location.path("/receiver/tips");
            });
      });

>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
    };

}]);

GLClient.controller('ReceiverPreferencesCtrl', ['$scope', '$rootScope', 'ReceiverPreferences', 'changePasswordWatcher', 'CONSTANTS', 'glcrypto',
  function($scope, $rootScope, ReceiverPreferences, changePasswordWatcher, CONSTANTS, glcrypto) {

    $scope.tabs = [
      {
        title: "Password Configuration",
        template: "views/receiver/preferences/tab1.html",
        ctrl: TabCtrl
      },
      {
        title: "Notification Settings",
        template: "views/receiver/preferences/tab2.html",
        ctrl: TabCtrl
      },
      {
        title:"Encryption Settings",
        template:"views/receiver/preferences/tab3.html",
        ctrl: TabCtrl
      }
    ];

    $scope.navType = 'pills';

    $scope.timezones = CONSTANTS.timezones;
    $scope.email_regexp = CONSTANTS.email_regexp;

    $scope.preferences = ReceiverPreferences.get();

    changePasswordWatcher($scope, "preferences.old_password",
        "preferences.password", "preferences.check_password");

    $scope.pass_save = function () {
      if (!$scope.preferences.pgp_e2e_public) {
        ReceiverPreferences.generate_and_save_key($scope.preferences);
      } else {
        glcrypto.derivate_password($scope.preferences.old_password, "salt!").then(function(data1) {
          var old_password = data1.stretched;

          glcrypto.derivate_passphrase($scope.preferences.old_password, "salt!").then(function(data2) {
            var old_passphrase = data2.stretched;

            glcrypto.derivate_password($scope.preferences.password, "salt!").then(function(data3) {
              var new_password = data3.stretched;

              glcrypto.derivate_passphrase($scope.preferences.password, "salt!").then(function(data4) {
                var new_passphrase = data4.stretched;

                try {
                  privKey = openpgp.key.readArmored($scope.preferences.pgp_e2e_private).keys[0];
                } catch (e) {
                  throw new Error('Importing key failed. Parsing error!');
                }

                if (!privKey.decrypt(old_passphrase)) {
                  throw new Error('Old passphrase incorrect!');
                }

                try {
                  packets = privKey.getAllKeyPackets();
                  for (var i = 0; i < packets.length; i++) {
                    packets[i].encrypt(new_passphrase);
                  }

                  newKeyArmored = privKey.armor();
                } catch (e) {
                  throw new Error('Setting new passphrase failed!');
                }

                if (!privKey.decrypt(new_passphrase)) {
                  throw new Error('Decrypting key with new passphrase failed!');
                }

                $scope.preferences.old_password = old_password;
                $scope.preferences.password = new_password;
                $scope.preferences.pgp_e2e_private = newKeyArmored;

                $scope.preferences.$update(function (){
                  if (!$rootScope.successes) {
                    $rootScope.successes = [];
                  }
                  $rootScope.successes.push({message: 'Updated your password!'});
                });
              })
            });
          });
        });
      }
<<<<<<< HEAD
    }
=======
      if ($scope.preferences.gpg_key_armor == undefined) {
        $scope.preferences.gpg_key_armor = '';
      }

      var new_password = gl_password($scope.preferences.password);
      var old_password = gl_password($scope.preferences.old_password);
      var new_passphrase = gl_passphrase($scope.preferences.password);
      console.log('update login password ', $scope.preferences.password, ' ', new_password);
      console.log('old login password ', $scope.preferences.old_password, ' ', old_password);
      console.log('update passphrase ', new_passphrase);

      if (! $scope.preferences.pgp_glkey_pub ) {

            //TODO: receiver email if present
            var k_user_id = $scope.preferences.email;
            var k_user_id = 'fake@email.com';
            var k_passphrase = new_passphrase;
            var k_bits = 2048;

            openpgp.config.show_version = false;
            openpgp.config.show_comment = false;

            key = openpgp.generateKeyPair({ numBits: k_bits,
                                            userId: k_user_id,
                                            passphrase: k_passphrase }).then(function(keyPair) {

                $scope.preferences.pgp_glkey_pub = keyPair.publicKeyArmored;
                $scope.preferences.pgp_glkey_priv = keyPair.privateKeyArmored;
                $scope.preferences.old_password = old_password;
                $scope.preferences.password = new_password;
                $scope.preferences.check_password = new_password;

                $scope.preferences.$update(function () {
                    if (!$rootScope.successes) {
                        $rootScope.successes = [];
                    }
                    $rootScope.successes.push({message: 'Updated your password!'});
                });

            });

      } else {
            var old_passphrase = gl_passphrase($scope.preferences.old_password);
            console.log('update old passphrase ', $scope.preferences.old_password, ' ', old_passphrase);

            try {
                privKey = openpgp.key.readArmored( $scope.preferences.pgp_glkey_priv ).keys[0];
            } catch (e) {
                throw new Error('Importing key failed. Parsing error!');
            }
            if (!privKey.decrypt( old_passphrase )) {
                throw new Error('Old passphrase incorrect!');
            }
            try {
                packets = privKey.getAllKeyPackets();
                for (var i = 0; i < packets.length; i++) {
                    packets[i].encrypt( new_passphrase );
                }
                newKeyArmored = privKey.armor();
            } catch (e) {
                throw new Error('Setting new passphrase failed!');
            }
            if (!privKey.decrypt( new_passphrase )) {
                throw new Error('Decrypting key with new passphrase failed!');
            }
            $scope.preferences.pgp_glkey_priv = newKeyArmored;
            $scope.preferences.old_password = old_password;
            $scope.preferences.password = new_password;
            $scope.preferences.check_password = new_password;

            $scope.preferences.$update(function () {
                if (!$rootScope.successes) {
                    $rootScope.successes = [];
                }
                $rootScope.successes.push({message: 'Updated your password!'});
            });

      }

    };
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235

    $scope.pref_save = function() {

      $scope.preferences.password = '';
      $scope.preferences.old_password = '';

      if ($scope.preferences.pgp_key_remove == true) {
        $scope.preferences.pgp_key_public = '';
      }

      if ($scope.preferences.pgp_key_public !== undefined &&
          $scope.preferences.pgp_key_public != '') {
        $scope.preferences.pgp_key_remove = false;
      }

      $scope.preferences.$update(function(){

        if (!$rootScope.successes) {
          $rootScope.successes = [];
        }
        $rootScope.successes.push({message: 'Updated your preferences!'});
      });
    }

}]);

GLClient.controller('ReceiverTipsCtrl', ['$scope', 'ReceiverTips',
  function($scope, ReceiverTips) {
  $scope.tips = ReceiverTips.query();
}]);
