import pgpy
from globaleaks.tests.test_gpg2 import HermesGlobaleaksKey, VALID_PGP_KEY

SKEY="bananelamponi123"

MESSAGE=file('mc.txt').read()
PUB=file('abc.asc').read()
ak, others = pgpy.PGPKey.from_blob( PUB )
print len(MESSAGE)


#plain_msg = pgpy.PGPMessage.new( MESSAGE[0:8142], compression=0x00 )
plain_msg = pgpy.PGPMessage.new( MESSAGE, compression=0x00 )
enc_msg = ak.encrypt(plain_msg)
for pkt in enc_msg:
    print type(pkt), ' ', len(pkt.__bytes__())

outdata = b''.join(pkt.__bytes__() for pkt in enc_msg)
file('mc_enc.asc', 'w+').write( outdata )

#file('mc_enc.asc', 'w+').write( str(enc_msg) )
#file('t.dmg.asc', 'w+').write( str(enc_msg) )

