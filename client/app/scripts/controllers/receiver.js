/* global window */

GLClient.controller('ReceiverSidebarCtrl', ['$scope', '$location', function($scope, $location){
  var current_menu = $location.path().split('/').slice(-1);
  $scope.active = {};
  $scope.active[current_menu] = "active";
}]);

GLClient.controller('ReceiverFirstLoginCtrl', ['$scope', '$rootScope', '$location', 'ReceiverPreferences', 'changePasswordWatcher',
  function($scope, $rootScope, $location, ReceiverPreferences, changePasswordWatcher) {

    $scope.preferences = ReceiverPreferences.get();

    changePasswordWatcher($scope, "preferences.old_password",
        "preferences.password", "preferences.check_password");

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

    };

}]);

GLClient.controller('ReceiverPreferencesCtrl', ['$scope', '$rootScope', 'ReceiverPreferences', 'changePasswordWatcher', 'CONSTANTS',
  function($scope, $rootScope, ReceiverPreferences, changePasswordWatcher, CONSTANTS) {

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

      if ($scope.preferences.gpg_key_remove == undefined) {
        $scope.preferences.gpg_key_remove = false;
      }
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

    $scope.pref_save = function() {

      $scope.preferences.password = '';
      $scope.preferences.old_password = '';

      if ($scope.preferences.gpg_key_remove == true) {
        $scope.preferences.gpg_key_armor = '';
      }

      if ($scope.preferences.gpg_key_armor !== undefined &&
          $scope.preferences.gpg_key_armor != '') {
        $scope.preferences.gpg_key_remove = false;
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

GLClient.controller('ReceiverNotificationCtrl', ['$scope', '$rootScope', 'ReceiverNotification',
  function($scope, $rootScope, ReceiverNotification) {
  $scope.activities = ReceiverNotification.get();

  $scope.clear_notifications = function() {
    ReceiverNotification['delete']({}, function(){
      $rootScope.$broadcast("REFRESH");
    });
  }

}]);
