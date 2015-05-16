import pgpy

<<<<<<< HEAD
=======
SKEY="bananelamponi123"
>>>>>>> 3ebbfba3163835c70398991d1b5457fea90a124c

PUB=file('jskey.asc').read()
ak, others = pgpy.PGPKey.from_blob( PUB )
print ak, others


