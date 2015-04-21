# -*- coding: UTF-8
# config
# ******
#
# Configuration file do not contain GlobaLeaks Node information, like in the 0.1
# because all those infos are stored in the databased.
# Config contains some system variables usable for debug,

import sys
import glob
import shutil
import traceback
import logging
import pwd
import grp
import getpass
from optparse import OptionParser
from ctypes import CDLL

import re
import os
import transaction
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor
from twisted.internet.threads import deferToThreadPool
from storm import exceptions, tracer
from storm.zope.zstorm import ZStorm
from storm.databases.sqlite import sqlite
from cyclone.web import HTTPError
from cyclone.util import ObjectDict as OD
from globaleaks import __version__, DATABASE_VERSION, LANGUAGES_SUPPORTED_CODES



# XXX. MONKEYPATCH TO SUPPORT STORM 0.19
import storm.databases.sqlite


class SQLite(storm.databases.sqlite.Database):
    connection_factory = storm.databases.sqlite.SQLiteConnection

    def __init__(self, uri):
        if sqlite is storm.databases.sqlite.dummy:
            raise storm.databases.sqlite.DatabaseModuleError("'pysqlite2' module not found")
        self._filename = uri.database or ":memory:"
        self._timeout = float(uri.options.get("timeout", 5))
        self._synchronous = uri.options.get("synchronous")
        self._journal_mode = uri.options.get("journal_mode")
        self._foreign_keys = uri.options.get("foreign_keys")

    def raw_connect(self):
        # See the story at the end to understand why we set isolation_level.
        raw_connection = sqlite.connect(self._filename, timeout=self._timeout,
                                        isolation_level=None)
        if self._synchronous is not None:
            raw_connection.execute("PRAGMA synchronous = %s" %
                                   (self._synchronous,))

        if self._journal_mode is not None:
            raw_connection.execute("PRAGMA journal_mode = %s" %
                                   (self._journal_mode,))

        if self._foreign_keys is not None:
            raw_connection.execute("PRAGMA foreign_keys = %s" %
                                   (self._foreign_keys,))

        return raw_connection


storm.databases.sqlite.SQLite = SQLite
storm.databases.sqlite.create_from_uri = SQLite
# XXX. END MONKEYPATCH

verbosity_dict = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

external_counted_events = {
    'new_submission': 0,
    'finalized_submission': 0,
    'anon_requests': 0,
    'file_uploaded': 0,
}


class GLSettingsClass(object):
    initialized = False

    def __init__(self):

        if GLSettingsClass.initialized:
            error_msg = "Singleton GLSettingClass instanced twice!"
            raise Exception(error_msg)
        else:
            GLSettingsClass.initialized = True

        # command line parsing utils
        self.parser = OptionParser()
        self.cmdline_options = None

        # version
        self.version_string = __version__

        # daemon
        self.nodaemon = False

        # threads sizes
        self.db_thread_pool_size = 1

        self.bind_addresses = '127.0.0.1'

        # bind port
        self.bind_port = 8082

        # store name
        self.store_name = 'main_store'

        self.db_type = 'sqlite'
        # Database version tracking
        self.db_version = DATABASE_VERSION

        # debug defaults
        self.storm_debug = False
        self.http_log = -1
        self.http_log_counter = 0
        self.loglevel = "CRITICAL"

        # files and paths
        self.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.pid_path = '/var/run/globaleaks'
        self.working_path = '/var/globaleaks'
        self.static_source = '/usr/share/globaleaks/glbackend'
        self.glclient_path = '/usr/share/globaleaks/glclient'

        self.set_ramdisk_path()

        # list of plugins available in the software
        self.notification_plugins = [
            'MailNotification',
        ]

        self.default_password = 'globaleaks'

        # session tracking, in the singleton classes
        self.sessions = dict()

        # statistical, referred to latest period
        # and resetted by session_management sched
        self.failed_login_attempts = 0

        # download tocken trackin
        self.download_tokens = dict()

        # static file rules
        self.staticfile_regexp = r'(.*)'
        self.staticfile_overwrite = False
        self.reserved_names = OD()
        self.reserved_names.logo = "globaleaks_logo"
        self.reserved_names.css = "custom_stylesheet"
        self.reserved_names.html = "custom_homepage"

        # acceptable 'Host:' header in HTTP request
        self.accepted_hosts = "127.0.0.1,localhost"

        self.receipt_regexp = u'[0-9]{16}'

        # default timings for scheduled jobs
        self.session_management_minutes_delta = 1  # runner.py function expects minutes
        self.notification_minutes_delta = 2  # runner.py function expects minutes
        self.delivery_seconds_delta = 20  # runner.py function expects seconds
        self.anomaly_seconds_delta = 10  # runner.py function expects seconds
        self.mailflush_minutes_delta = 5  # before change check mailflush logic and delay


        # Default values, used to initialize DB at the first start,
        # or whenever the value is not supply by client.
        # These value are then stored in the single instance
        # (Node, Receiver or Context) and then can be updated by
        # the admin using the Admin interface (advanced settings)
        self.defaults = OD()

        # default tor2web_admin setting is set to True;
        # the setting is then switched based on automatic user detection during wizard:
        #
        # - if the admin performs the wizard via tor2web the permission is kept True
        # - if the admin performs the wizard via Tor the permission is set to False
        self.defaults.tor2web_admin = True

        self.defaults.tor2web_submission = False
        self.defaults.tor2web_receiver = False
        self.defaults.tor2web_unauth = True
        self.defaults.allow_unencrypted = False
        self.defaults.allow_iframes_inclusion = False
        self.defaults.maximum_namesize = 128
        self.defaults.maximum_textsize = 4096
        self.defaults.maximum_filesize = 30  # expressed in megabytes
        self.defaults.maximum_request_size = 4  # expressed in megabytes
        self.defaults.exception_email = u"globaleaks-stackexception@lists.globaleaks.org"
        # Context dependent values:
        self.defaults.tip_seconds_of_life = (3600 * 24) * 15
        self.defaults.submission_seconds_of_life = (3600 * 24) * 3

        self.defaults.language = u'en'
        self.defaults.languages_enabled = LANGUAGES_SUPPORTED_CODES

        self.defaults.timezone = 0
        self.defaults.landing_page = 'homepage'

        self.defaults.receiver_notif_enable = True
        self.defaults.admin_notif_enable = True
        self.defaults.notif_server = None
        self.defaults.notif_port = None
        self.defaults.notif_username = None
        self.defaults.notif_security = None
        self.defaults.notif_uses_tor = None

        # this became false when, few MBs cause node to disable submissions
        self.defaults.disk_availability = True
        self.defaults.minimum_megabytes_required = 1024  # 1 GB, or the node is disabled

        # a dict to keep track of the lifetime of the session. at the moment
        # not exported in the UI.
        # https://github.com/globaleaks/GlobaLeaks/issues/510
        self.defaults.lifetimes = {
            'admin': (60 * 60),
            'receiver': (60 * 60),
            'wb': (60 * 60)
        }

        # A lot of operations performed massively by globaleaks
        # should avoid to fetch continuously variables from the DB so that
        # it is important to keep this variables in memory
        #
        # To this aim a variable memory_copy is instantiated as a copy of
        # self.defaults and then initialized and updated after
        # create_tables() and for every node+notif update
        self.memory_copy = OD(self.defaults)

        # Default delay threshold
        self.delay_threshold = 0.800

        # unchecked_tor_input contains information that cannot be validated now
        # due to complex inclusions or requirements. Data is used in
        # globaleaks.db.datainit.apply_cli_options()
        self.unchecked_tor_input = {}

        # SOCKS default
        self.socks_host = "127.0.0.1"
        self.socks_port = 9050

        self.notification_limit = 30

        self.user = getpass.getuser()
        self.group = getpass.getuser()
        self.uid = os.getuid()
        self.gid = os.getgid()
        self.start_clean = False
        self.devel_mode = False
        self.developer_name = ''
        self.skip_wizard = False
        self.glc_path = None

        # Number of failed login enough to generate an alarm
        self.failed_login_alarm = 5

        # Number of minutes in which a user is prevented to login in case of triggered alarm
        self.failed_login_block_time = 5

        # Size in bytes of every log file. Once this size is reached the
        # logfile is rotated.
        # Default: 1M
        self.log_file_size = 1000000
        # Number of log files to conserve.
        self.maximum_rotated_log_files = 100

        # size used while streaming files
        self.file_chunk_size = 8192

        # Disk file encryption in realtime
        # if the key is fine or is not.
        # this key permit Globaleaks to resist on application restart
        # not to a reboot! (is written in GLSetting.
        # key is initialized and stored in key path.
        # key_id contains an identifier of the key (when system reboots,
        # key changes.
        ### you can read more about this security measure in the document:
        ### https://github.com/globaleaks/GlobaLeaks/wiki/Encryption
        self.AES_key_size = 32
        # This key_id is just to identify the keys, and is generated with
        self.AES_key_id_regexp = u'[A-Za-z0-9]{16}'
        self.AES_counter_nonce = 128 / 8
        self.AES_file_regexp = r'(.*)\.aes'
        self.AES_file_regexp_comp = re.compile(self.AES_file_regexp)
        self.AES_keyfile_prefix = "aeskey-"

        self.exceptions = {}

        # Extreme debug option triggered by --XXX, that's are the defaults
        self.debug_option_in_the_future = 0
        self.debug_option_UUID_human = ""
        self.debug_UUID_human_counter = 0
        self.debug_option_mlockall = False


    def eval_paths(self):
        self.config_file_path = '/etc/globaleaks'

        self.pidfile_path = os.path.join(self.pid_path, 'globaleaks-' + str(self.bind_port) + '.pid')
        self.glfiles_path = os.path.abspath(os.path.join(self.working_path, 'files'))
        self.gldb_path = os.path.abspath(os.path.join(self.working_path, 'db'))
        self.log_path = os.path.abspath(os.path.join(self.working_path, 'log'))
        self.submission_path = os.path.abspath(os.path.join(self.glfiles_path, 'submission'))
        # this temporary directory is not under RamDisk because contain the temporary encrypted files!
        self.tmp_upload_path = os.path.abspath(os.path.join(self.glfiles_path, 'encrypted_upload'))
        self.static_path = os.path.abspath(os.path.join(self.glfiles_path, 'static'))
        self.static_path_l10n = os.path.abspath(os.path.join(self.static_path, 'l10n'))
        self.static_db_source = os.path.abspath(os.path.join(self.root_path, 'globaleaks', 'db'))
        self.torhs_path = os.path.abspath(os.path.join(self.working_path, 'torhs'))
        self.db_schema_file = os.path.join(self.static_db_source, self.db_type + '.sql')
        self.logfile = os.path.abspath(os.path.join(self.log_path, 'globaleaks.log'))
        self.httplogfile = os.path.abspath(os.path.join(self.log_path, "http.log"))

        # gnupg path is used by PGP as temporary directory with keyring and files encryption.
        self.pgproot = os.path.abspath(os.path.join(self.ramdisk_path, 'gnupg'))

        if self.db_type == 'sqlite':
            self.db_uri = 'sqlite:' + \
                          os.path.abspath(os.path.join(self.gldb_path,
                                                       'glbackend-%d.db?foreign_keys=ON' % DATABASE_VERSION))

        # If we see that there is a custom build of GLClient, use that one.
        custom_glclient_path = '/var/globaleaks/custom-glclient'
        if os.path.exists(custom_glclient_path):
            self.glclient_path = custom_glclient_path


    def set_ramdisk_path(self):
        self.ramdisk_path = '/dev/shm/globaleaks'
        if not os.path.isdir('/dev/shm'):
            self.ramdisk_path = os.path.join(self.working_path, 'ramdisk')

        self.log_debug("Setting ramdisk to: %s" % self.ramdisk_path)

    def set_devel_mode(self):
        self.devel_mode = True

        # is forced by -z, but unitTest has not:
        if not self.cmdline_options:
            self.developer_name = u"Random GlobaLeaks Developer"
        else:
            self.developer_name = unicode(self.cmdline_options.developer_name)

        self.pid_path = os.path.join(self.root_path, 'workingdir')
        self.working_path = os.path.join(self.root_path, 'workingdir')
        self.static_source = os.path.join(self.root_path, 'staticdata')

        self.set_ramdisk_path()

        self.glclient_path = os.path.abspath(os.path.join(self.root_path, "..", "client", "build"))
        if not os.path.exists(self.glclient_path):
            self.glclient_path = os.path.abspath(os.path.join(self.root_path, "..", "client", "app"))


    def set_glc_path(self, glcp):
        self.glclient_path = os.path.abspath(os.path.join(self.root_path, glcp))


    def enable_debug_mode(self):
        import signal

        def start_pdb(signal, trace):
            import pdb

            pdb.set_trace()

        signal.signal(signal.SIGQUIT, start_pdb)

    def validate_tor_dir_struct(self, tor_dir):
        """
        Return False instead of quit(-1) because at the startup this struct
        can in fact be empty
        """
        if not os.path.isdir(tor_dir):
            print "Invalid directory provided as -D argument (%s)" % self.cmdline_options.tor_dir
            return False

        hostname_tor_file = os.path.join(tor_dir, 'hostname')
        if not os.path.isfile(hostname_tor_file):
            print "Not found 'hostname' file as expected in Tor dir (-D %s): skipped" % tor_dir
            return False

        return True

    def load_cmdline_options(self):
        """
        This function is called by runner.py and operate in cmdline_options,
        interpreted and filled in bin/startglobaleaks script.

        happen in startglobaleaks before the sys.argv is modified
        """
        assert self.cmdline_options is not None

        self.nodaemon = self.cmdline_options.nodaemon

        self.storm_debug = self.cmdline_options.storm_debug

        self.loglevel = verbosity_dict[self.cmdline_options.loglevel]

        self.bind_addresses = self.cmdline_options.ip.replace(" ", "").split(",")

        if not self.validate_port(self.cmdline_options.port):
            quit(-1)
        self.bind_port = self.cmdline_options.port

        self.http_log = self.cmdline_options.http_log

        self.accepted_hosts = list(set(self.bind_addresses + \
                                       self.cmdline_options.host_list.replace(" ", "").split(",")))

        self.disable_email_torification = self.cmdline_options.disable_email_torification

        self.socks_host = self.cmdline_options.socks_host

        if not self.validate_port(self.cmdline_options.socks_port):
            quit(-1)
        self.socks_port = self.cmdline_options.socks_port

        try:
            self.delay_threshold = (int(self.cmdline_options.delay) / 1000.0)

            if self.delay_threshold > 2:
                print "[?] Are you sure ? You've set a security delay of", \
                    self.delay_threshold, "seconds"
        except ValueError:
            print "Invalid delay inserted, a number of milliseconds is required"
            quit(-1)

        if self.cmdline_options.ramdisk:
            self.ramdisk_path = self.cmdline_options.ramdisk

        # we're not performing here the checks because utility.acquire_url_address cannot
        # be included here.
        # This cause that *content* validation cannot be done here, but when GL is started.
        if self.cmdline_options.tor_dir and self.validate_tor_dir_struct(self.cmdline_options.tor_dir):

            hostname_tor_file = os.path.join(self.cmdline_options.tor_dir, 'hostname')

            if not os.access(hostname_tor_file, os.R_OK):
                print "Tor HS file in %s cannot be read" % hostname_tor_file
                quit(-1)

            with file(hostname_tor_file, 'r') as htf:
                hostname_tor_content = htf.read(22)  # hostname + .onion
                GLSetting.unchecked_tor_input['hostname_tor_content'] = hostname_tor_content
        # URL validation and DB import continue in apply_cli_options

        if self.cmdline_options.hidden_service:
            GLSetting.unchecked_tor_input['hidden_service'] = self.cmdline_options.hidden_service

        if self.cmdline_options.public_website:
            GLSetting.unchecked_tor_input['public_website'] = self.cmdline_options.public_website
        # These three option would be used in globaleaks.db.datainit.apply_cli_options()

        if self.cmdline_options.user and self.cmdline_options.group:
            self.user = self.cmdline_options.user
            self.group = self.cmdline_options.group
            self.uid = pwd.getpwnam(self.cmdline_options.user).pw_uid
            self.gid = grp.getgrnam(self.cmdline_options.group).gr_gid
        elif self.cmdline_options.user:
            # user selected: get also the associated group
            self.user = self.cmdline_options.user
            self.uid = pwd.getpwnam(self.cmdline_options.user).pw_uid
            self.gid = pwd.getpwnam(self.cmdline_options.user).pw_gid
        elif self.cmdline_options.group:
            # group selected: keep the current user
            self.group = self.cmdline_options.group
            self.gid = grp.getgrnam(self.cmdline_options.group).gr_gid
            self.uid = os.getuid()

        if self.uid == 0 or self.gid == 0:
            print "Invalid user: cannot run as root"
            quit(-1)

        self.start_clean = self.cmdline_options.start_clean

        self.working_path = self.cmdline_options.working_path

        if self.cmdline_options.developer_name:
            print "Enabling Development Mode for %s" % \
                  self.cmdline_options.developer_name
            self.developer_name = unicode(self.cmdline_options.developer_name)
            self.set_devel_mode()

        if self.cmdline_options.skip_wizard:
            self.skip_wizard = True

        if self.cmdline_options.glc_path:
            self.set_glc_path(self.cmdline_options.glc_path)

        self.eval_paths()

        # special evaluation of glclient directory:
        indexfile = os.path.join(self.glclient_path, 'index.html')
        if os.path.isfile(indexfile):
            print "Serving GLClient from %s" % self.glclient_path
        else:
            print "Invalid directory of GLCLient: %s: index.html not found" % self.glclient_path
            quit(-1)

        # hardcore extremely dangerous --XXX option trigger
        # one,two,three
        if self.cmdline_options.xxx:
            print "\033[1;33mHardcore dangerous hazardous radioactive --XXX option used!\033[0m"
            hardcore_opts = self.cmdline_options.xxx.split(',')
            if len(hardcore_opts):
                try:
                    GLSetting.debug_option_in_the_future = int(hardcore_opts[0])
                except ValueError:
                    print "Invalid number of seconds provided:", hardcore_opts[0]
                    quit(-1)
                print "→ \033[1;31mUsing", GLSetting.debug_option_in_the_future, \
                    "seconds in the future\033[0m"

            if len(hardcore_opts) > 1 and len(hardcore_opts[1]) > 1:
                # at least two byte needed, so you can skip this option
                GLSetting.debug_option_UUID_human = hardcore_opts[1]

                if len(GLSetting.debug_option_UUID_human) > 8:
                    GLSetting.debug_option_UUID_human = GLSetting.debug_option_UUID_human[:8]

                print "→ \033[1;31mUsing", GLSetting.debug_option_UUID_human, \
                    "to generate human readable UUIDv4\033[0m"

            if len(hardcore_opts) > 2 and len(hardcore_opts[2]) > 1:
                self.debug_option_mlockall = True
                print "→ \033[1;31mUsing mlockall(2) system call to prevent GlobaLeaks swap\033[0m"
                self.avoid_globaleaks_swap()

            print "\n"


    def validate_port(self, inquiry_port):
        if inquiry_port >= 65535 or inquiry_port < 0:
            print "Invalid port number ( > than 65535 can't work! )"
            return False
        return True

    def avoid_globaleaks_swap(self):
        """
        use mlockall(2) system call to prevent GlobaLeaks from swapping
        """
        libc = CDLL("libc.so.6")

        # lock memory from swapping that is created in the FUTURE
        # (does NOT apply to stuff that is already in memory!)
        if libc.mlockall(2):
            print "Unable to libc.mlockall"
            quit(-1)

    def create_directories(self):
        """
        Execute some consistency checks on command provided Globaleaks paths

        if one of working_path or static path is created we copy
        here the static files (default logs, and in the future pot files for localization)
        because here stay all the files needed by the application except the python scripts
        """
        new_environment = False

        def create_directory(path):
            # returns false if the directory is already present
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                    self.log_debug("Created directoy %s" % path)
                    return True
                except OSError as excep:
                    self.log_debug("Error in creating directory: %s (%s)" % (path, excep.strerror))
                    raise excep
            else:
                if not os.path.isdir(path):
                    self.log_debug("Error creating directory: %s (path exists and is not a dir)" % path)
                    raise Exception("Error creating directory: %s (path exists and is not a dir)" % path)
                return False

        if create_directory(self.working_path):
            new_environment = True

        create_directory(self.gldb_path)
        create_directory(self.glfiles_path)
        create_directory(self.static_path)
        create_directory(self.static_path_l10n)
        create_directory(self.submission_path)
        create_directory(self.tmp_upload_path)
        create_directory(self.log_path)
        create_directory(self.torhs_path)
        create_directory(self.ramdisk_path)

        logo_path = os.path.join(self.static_path, "%s.png" % GLSetting.reserved_names.logo)
        # Missing default logo: is supposed we're initializing a new globaleaks directory
        # happen in unitTest and when a new working directory is specify
        if not os.path.isfile(logo_path):
            new_environment = True

        if new_environment:
            almost_one_file = 0
            for _, _, files in os.walk(self.static_source):
                almost_one_file += 1
                # REMIND: at the moment are not supported subpaths
                for single_file in files:
                    shutil.copyfile(
                        os.path.join(self.static_source, single_file),
                        os.path.join(self.static_path, single_file)
                    )
            if not almost_one_file:
                print "[Non fatal error] Found empty: %s" % self.static_source
                print "Your instance has not torrc and the default logo"


    def check_directories(self):
        for path in (self.working_path, self.root_path, self.glclient_path,
                     self.glfiles_path, self.static_path, self.submission_path, self.log_path):
            if not os.path.exists(path):
                raise Exception("%s does not exist!" % path)

        # Directory with Write + Read access
        for rdwr in (self.working_path,
                     self.glfiles_path, self.static_path, self.submission_path, self.log_path):
            if not os.access(rdwr, os.W_OK | os.X_OK):
                raise Exception("write capability missing in: %s" % rdwr)

        # Directory in Read access
        for rdonly in (self.root_path, self.glclient_path):
            if not os.access(rdonly, os.R_OK | os.X_OK):
                raise Exception("read capability missing in: %s" % rdonly)

    def fix_file_permissions(self, path=None):
        """
        Recursively updates file permissions on a given path.
        UID and GID default to -1, and mode is required
        """
        if not path:
            path = self.working_path

        # we need to avoid changing permissions to torhs directory and its files
        if path == os.path.join(self.working_path, 'torhs'):
            return

        try:
            if path != self.working_path:
                os.chown(path, self.uid, self.gid)
                os.chmod(path, 0700)
        except Exception as excep:
            print "Unable to update permissions on %s: %s" % (path, excep)
            quit(-1)

        for item in glob.glob(path + '/*'):
            if os.path.isdir(item):
                self.fix_file_permissions(item)
            else:
                try:
                    os.chown(item, self.uid, self.gid)
                    os.chmod(item, 0700)
                except Exception as excep:
                    print "Unable to update permissions on %s: %s" % (item, excep)
                    quit(-1)

    def remove_directories(self):
        for root, dirs, files in os.walk(self.working_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def drop_privileges(self):

        if os.getgid() != self.gid:
            try:
                print "switching group privileges since %d to %d" % (os.getgid(), self.gid)
                os.setgid(self.gid)
            except OSError as droperr:
                print "unable to drop group privileges: %s" % droperr.strerror
                quit(-1)

        if os.getuid() != self.uid:
            try:
                print "switching user privileges since %d to %d" % (os.getuid(), self.uid)
                os.setuid(self.uid)
            except OSError as droperr:
                print "unable to drop user privileges: %s" % droperr.strerror
                quit(-1)

    def log_debug(self, message):
        """
        Log to stdout only if debug is set at higher levels
        """
        if self.loglevel == logging.DEBUG:
            print message

    def cleaning_dead_files(self):
        """
        This function is called at the start of GlobaLeaks, in
        bin/globaleaks, and checks if the file present in
        temporally_encrypted_dir
            (XXX change submission now used to too much thing)
        """

        # temporary .aes files must be simply deleted
        for f in os.listdir(GLSetting.tmp_upload_path):

            path = os.path.join(GLSetting.tmp_upload_path, f)
            print "Removing old temporary file: %s" % path

            try:
                os.remove(path)
            except OSError as excep:
                print "Error while evaluating removal for %s: %s" % (path, excep.strerror)

        # temporary .aes files with lost keys can be deleted
        # while temporary .aes files with valid current key
        # will be automagically handled by delivery sched.
        keypath = os.path.join(self.ramdisk_path, GLSetting.AES_keyfile_prefix)

        for f in os.listdir(GLSetting.submission_path):
            path = os.path.join(GLSetting.submission_path, f)
            try:
                result = GLSetting.AES_file_regexp_comp.match(f)
                if result is not None:
                    if not os.path.isfile("%s%s" % (keypath, result.group(1))):
                        print "Removing old encrypted file (lost key): %s" % path
                        os.remove(path)
            except Exception as excep:
                print "Error while evaluating removal for %s: %s" % (path, excep)


# GLSetting is a singleton class exported once
GLSetting = GLSettingsClass()


class transact(object):
    """
    Class decorator for managing transactions.
    Because Storm sucks.
    """
    tp = ThreadPool(0, GLSetting.db_thread_pool_size)

    readonly = False

    def __init__(self, method):
        self.store = None
        self.method = method
        self.instance = None
        self.debug = GLSetting.storm_debug

        if self.debug:
            tracer.debug(self.debug, sys.stdout)

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __call__(self, *args, **kwargs):
        return self.run(self._wrap, self.method, *args, **kwargs)

    @staticmethod
    def run(function, *args, **kwargs):
        """
        Defer provided function to thread
        """
        return deferToThreadPool(reactor, transact.tp,
                                 function, *args, **kwargs)

    @staticmethod
    def get_store():
        """
        Returns a reference to Storm Store
        """
        zstorm = ZStorm()
        zstorm.set_default_uri(GLSetting.store_name, GLSetting.db_uri)

        return zstorm.get(GLSetting.store_name)

    def _wrap(self, function, *args, **kwargs):
        """
        Wrap provided function calling it inside a thread and
        passing the store to it.
        """
        self.store = self.get_store()

        try:
            if self.instance:
                result = function(self.instance, self.store, *args, **kwargs)
            else:
                result = function(self.store, *args, **kwargs)

        except (exceptions.IntegrityError, exceptions.DisconnectionError):
            transaction.abort()
            # we print the exception here because we do not propagate it
            GLSetting.log_debug(traceback.format_exc())
            result = None
        except HTTPError as excep:
            transaction.abort()
            raise excep
        except:
            transaction.abort()
            self.store.close()
            # propagate the exception
            raise
        else:
            if not self.readonly:
                self.store.commit()
            else:
                self.store.flush()
                self.store.invalidate()
        finally:
            self.store.close()

        return result


class transact_ro(transact):
    readonly = True


transact.tp.start()
reactor.addSystemEventTrigger('after', 'shutdown', transact.tp.stop)
