import pgpy

SKEY="bananelamponi123"

PUB=file('jskey.asc').read()
ak, others = pgpy.PGPKey.from_blob( PUB )
print ak, others


