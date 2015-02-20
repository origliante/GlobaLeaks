import pgpy
from globaleaks.tests.test_gpg2 import HermesGlobaleaksKey, VALID_PGP_KEY
from pgpy.packet.packets import IntegrityProtectedSKEDataV1


MESSAGE=file('mc.txt').read()
PUB=file('abc.asc').read()

plain_msg = pgpy.PGPMessage.new( MESSAGE, compression=0x00 )
ak, others = pgpy.PGPKey.from_blob( PUB )
pke, sessionkey, cipher_algo = ak.encrypt(plain_msg, setup_only=True)


# usando Message
#<class 'pgpy.packet.packets.PKESessionKeyV3'>   271
#<class 'pgpy.packet.packets.IntegrityProtectedSKEDataV1'>   10693
# non usando Message
#<class 'pgpy.packet.packets.PKESessionKeyV3'>   271
#<class 'pgpy.packet.packets.IntegrityProtectedSKEDataV1'>   10681
# ho visto anche:
#<class 'pgpy.packet.packets.PKESessionKeyV3'>   270
#<class 'pgpy.packet.packets.IntegrityProtectedSKEDataV1'>   10681


ak, others = pgpy.PGPKey.from_blob( PUB )
pke, sessionkey, cipher_algo = ak.encrypt(plain_msg, setup_only=True)
ske = IntegrityProtectedSKEDataV1()
ske.encrypt(sessionkey, cipher_algo, MESSAGE)

print type(pke), ' ', len(pke.__bytes__())
print type(ske), ' ', len(ske.__bytes__())

file('bin.pke', 'w+').write( pke.__bytes__() )
file('bin.ske', 'w+').write( ske.__bytes__() )
mf = file('bin.merge', 'w+')
mf.write( pke.__bytes__() )
mf.write( ske.__bytes__() )
mf.close()

#file('t.dmg.asc', 'w+').write( str(enc_msg) )
#file('bin.msg', 'w+').write( enc_msg.__bytes__() )
#(gleaks)freeride:backend elv$ shasum bin.msg
#b5ac4c5014b790314005f30b881561a21c80f917  bin.msg
#(gleaks)freeride:backend elv$ shasum bin.merge
#b5ac4c5014b790314005f30b881561a21c80f917  bin.merge


