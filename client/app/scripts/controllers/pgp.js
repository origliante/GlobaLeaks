
GLClient.controller('PGPConfigCtrl', ['$scope', function($scope){


    $scope.generate_key = function() {
            $scope.receiver.gpg_key_armor = "ANTANI";

            var email = 'a@b.org';
            var password = 'abc123';

            var k_user_id = email;
            var k_passphrase = password;
            var k_bits = 4096;
            var k_bits = 2048;

            var key = openpgp.generateKeyPair({ numBits: k_bits,
                                                userId: k_user_id,
                                                passphrase: k_passphrase}).then(function(keyPair) {
                    var zip = new JSZip();
                    var user_id = k_user_id.replace("@", "_at_");
                    var user_id = user_id.replace(".", "_dot_");
                    var folder_name = "globaleaks-keys-" + user_id
                    var file_name = folder_name + '.zip'

                    var keys = zip.folder( folder_name );
                    keys.file("private_" + user_id + ".asc", keyPair.privateKeyArmored );
                    keys.file("public_" + user_id + ".asc", keyPair.publicKeyArmored );

                    var content = zip.generate({type:"blob"});
                    saveAs(content, file_name );

                    var pubkey = keyPair.publicKeyArmored;
                    idx = pubkey.length - 1;
                    while ( pubkey[idx] != '-' ) {
                        pubkey = pubkey.slice(0, idx);
                        idx -= 1;
                    }
                    console.log(pubkey);

                    $scope.receiver.gpg_key_armor = keyPair.publicKeyArmored;
                    $scope.$apply();
                });

            return true;

    }


}]);

