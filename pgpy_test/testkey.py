import pgpy


PUB=file('jskey.asc').read()
ak, others = pgpy.PGPKey.from_blob( PUB )
print ak, others


