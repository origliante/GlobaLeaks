
var gkey = null;
var plain_k = null;


openpgp.config.commentstring = 'GlobaLeaks';
openpgp.config.prefer_hash_algorithm = openpgp.enums.hash.sha256;


function key_change_passphrase(privateKeyArmored, old_pwd, new_pwd) {
    // read armored key
    try {
        privKey = openpgp.key.readArmored(privateKeyArmored).keys[0];
    } catch (e) {
        throw new Error('Importing key failed. Parsing error!');
    }

    // decrypt private key with passphrase
    if (!privKey.decrypt(old_pwd)) {
        throw new Error('Old passphrase incorrect!');
    }

    // encrypt key with new passphrase
    try {
        packets = privKey.getAllKeyPackets();
        for (var i = 0; i < packets.length; i++) {
            packets[i].encrypt(new_pwd);
        }
        newKeyArmored = privKey.armor();
    } catch (e) {
        throw new Error('Setting new passphrase failed!');
    }

    // check if new passphrase really works
    if (!privKey.decrypt(new_pwd)) {
        throw new Error('Decrypting key with new passphrase failed!');
    }
    return newKeyArmored;
}




function generate_key(email, password) {
    var k_user_id = email;
    var k_passphrase = password;
    var k_bits = 4096;
    var k_bits = 2048;

    key = openpgp.generateKeyPair({ numBits: k_bits,
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
    });

    return key;
}



function browser_has_crypto() {
    if (!window.crypto.getRandomValues) {
        window.alert("Error: Browser not supported\nReason: We need a cryptographically secure PRNG to be implemented (i.e. the window.crypto method)\nSolution: Use Chrome >= 11, Safari >= 3.1 or Firefox >= 21");
        return false;
    }
    return true;
}



function key_is_valid(armoredKey) {
    pgp_message = openpgp.key.readArmored( armoredKey );
    if (!pgp_message) {
        //("Invalid PGP file.");
        return false;
    }
    if (typeof(pgp_message.keys) == 'undefined') {
        //("NO Keys in armored PGP file");
        return false;
    }
    return true; 
}



function key_get_params(keyArmored) {
    var key, packet, userIds;

    // process armored key input
    if (keyArmored) {
        key = openpgp.key.readArmored(keyArmored).keys[0];
    } else if (this._publicKey) {
        key = this._publicKey;
    } else {
        throw new Error('Cannot read key params... keys not set!');
    }

    packet = key.primaryKey;

    // read user names and email addresses
    userIds = [];
    key.getUserIds().forEach(function(userId) {
        userIds.push({
            name: userId.split('<')[0].trim(),
            emailAddress: userId.split('<')[1].split('>')[0].trim()
        });
    });

    return {
        _id: packet.getKeyId().toHex().toUpperCase(),
        userId: userIds[0].emailAddress, // the primary (first) email address of the key
        userIds: userIds, // a dictonary of all the key's name/address pairs
        fingerprint: packet.getFingerprint().toUpperCase(),
        algorithm: packet.algorithm,
        bitSize: packet.getBitSize(),
        created: packet.created,
    };
}


