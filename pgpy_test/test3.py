import gnupg
from config import *

gpg = gnupg.GPG(gnupghome=gpg_home, keyring=pring, secret_keyring=sring)
gpg.encoding = "latin-1"
pkeys = gpg.list_keys(False)
skeys = gpg.list_keys(True)

pnum = len(pkeys)
snum = len(skeys)

print("""
%s contains %d public keys
%s contains %d private keys
""" % (pub_ring, pnum, sec_ring, snum))

