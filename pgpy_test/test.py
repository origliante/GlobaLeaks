
import os

from globaleaks.settings import GLSetting
from globaleaks.third_party.rstr import xeger

from gnupg import GPG

GLSetting.eval_paths()

temp_gpgroot = os.path.join(GLSetting.gpgroot, "%s" % xeger(r'[A-Za-z0-9]{8}'))
print temp_gpgroot

os.makedirs(temp_gpgroot, mode=0700)
gpgh = GPG(gnupghome=temp_gpgroot, options=['--trust-model', 'always'])


