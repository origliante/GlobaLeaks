# -*- encoding: utf-8 -*-
import os

from twisted.python import log
from storm.exceptions import OperationalError
from storm.locals import create_database, Store
from storm.properties import PropertyColumn
from storm.variables import BoolVariable, DateTimeVariable
from storm.variables import EnumVariable, IntVariable, RawStrVariable, PickleVariable
from storm.variables import UnicodeVariable, JSONVariable

from globaleaks import DATABASE_VERSION, models
from globaleaks.settings import GLSetting


# This code is take directly from the GlobaLeaks-pre-model-refactor

def variableToSQL(var, db_type):
    """
    We take as input a storm.variable and we output the SQLite string it
    represents.
    """
    if isinstance(var, BoolVariable):
        data_mapping = {
            "sqlite": "INTEGER",
        }
    elif isinstance(var, DateTimeVariable):
        data_mapping = {
            "sqlite": "VARCHAR",
        }
    elif isinstance(var, EnumVariable):
        data_mapping = {
            "sqlite": "BLOB",
        }
    elif isinstance(var, IntVariable):
        data_mapping = {
            "sqlite": "INTEGER",
        }
    elif isinstance(var, RawStrVariable):
        data_mapping = {
            "sqlite": "BLOB",
        }
    elif isinstance(var, UnicodeVariable):
        data_mapping = {
            "sqlite": "VARCHAR",
        }
    elif isinstance(var, JSONVariable):
        data_mapping = {
            "sqlite": "BLOB",
        }
    elif isinstance(var, PickleVariable):
        data_mapping = {
            "sqlite": "BLOB",
        }
    else:
        raise ValueError('Invalid var: {}'.format(var))

    return "%s" % data_mapping[db_type]


def varsToParametersSQL(variables, primary_keys, db_type):
    """
    Takes as input a list of variables (convered to SQLite syntax and in the
    form of strings) and primary_keys.
    Outputs these variables converted into paramter syntax for SQLites.

    ex.
        variables: ["var1 INTEGER", "var2 BOOL", "var3 INTEGER"]
        primary_keys: ["var1"]

        output: "(var1 INTEGER, var2 BOOL, var3 INTEGER PRIMARY KEY (var1))"
    """
    params = "("
    for var in variables[:-1]:
        params += "%s %s, " % (var[0], var[1])
    if len(primary_keys) > 0:
        params += "%s %s, " % variables[-1]
        params += "PRIMARY KEY ("
        for key in primary_keys[:-1]:
            params += "%s, " % key
        params += "%s))" % primary_keys[-1]
    else:
        params += "%s %s)" % variables[-1]
    return params


def generateCreateQuery(model):
    """
    This takes as input a Storm model and outputs the creation query for it.
    """
    prehistory = model.__storm_table__.find("_v_")
    if prehistory != -1:
        table_name = model.__storm_table__[:prehistory]
    else:
        table_name = model.__storm_table__

    query = "CREATE TABLE " + table_name + " "

    variables = []
    primary_keys = []

    for attr in dir(model):
        a = getattr(model, attr)
        if isinstance(a, PropertyColumn):
            var = a.variable_factory()
            data_mapping = variableToSQL(var, GLSetting.db_type)
            name = a.name
            variables.append((name, data_mapping))
            if a.primary:
                primary_keys.append(name)

    query += varsToParametersSQL(variables, primary_keys, GLSetting.db_type)
    return query


class TableReplacer(object):
    """
    This is the base class used by every Updater
    """

    def __init__(self, old_db_file, new_db_file, start_ver):
        from globaleaks.db.update_8_9 import Context_v_8, Receiver_v_8, Notification_v_8
        from globaleaks.db.update_9_10 import Node_v_9, Receiver_v_9, User_v_9
        from globaleaks.db.update_10_11 import InternalTip_v_10, InternalFile_v_10
        from globaleaks.db.update_11_12 import Node_v_11, Context_v_11
        from globaleaks.db.update_12_13 import Node_v_12, Context_v_12
        from globaleaks.db.update_13_14 import Node_v_13, Context_v_13
        from globaleaks.db.update_14_15 import Node_v_14, User_v_14, Context_v_14, Receiver_v_14, \
            InternalTip_v_14, Notification_v_14, Stats_v_14, Comment_v_14
        from globaleaks.db.update_15_16 import Receiver_v_15, Notification_v_15
        from globaleaks.db.update_16_17 import Node_v_16, Receiver_v_16, Notification_v_16, Stats_v_16
        from globaleaks.db.update_17_18 import Node_v_17
        from globaleaks.db.update_18_19 import Node_v_18

        self.old_db_file = old_db_file
        self.new_db_file = new_db_file
        self.start_ver = start_ver

        self.std_fancy = " ł "
        self.debug_info = "   [%d => %d] " % (start_ver, start_ver + 1)

        self.table_history = {
            'Node': [Node_v_9, None, Node_v_11, None, Node_v_12, Node_v_13, Node_v_14, Node_v_16, None, Node_v_17, Node_v_18, models.Node],
            'User': [User_v_9, None, User_v_14, None, None, None, None, models.User, None, None, None, None],
            'Context': [Context_v_8, Context_v_11, None, None, Context_v_12, Context_v_13, Context_v_14, models.Context, None, None, None, None],
            'Receiver': [Receiver_v_8, Receiver_v_9, Receiver_v_14, None, None, None, None, Receiver_v_15, Receiver_v_16, models.Receiver, None, None],
            'ReceiverFile': [models.ReceiverFile, None, None, None, None, None, None, None, None, None, None, None],
            'Notification': [Notification_v_8, Notification_v_14, None, None, None, None, None, Notification_v_15, Notification_v_16, models.Notification, None, None],
            'Comment': [Comment_v_14, None, None, None, None, None, None, models.Comment, None, None, None, None],
            'InternalTip': [InternalTip_v_10, None, None, InternalTip_v_14, None, None, None, models.InternalTip, None, None, None, None],
            'InternalFile': [InternalFile_v_10, None, None, models.InternalFile, None, None, None, None, None, None, None, None],
            'WhistleblowerTip': [models.WhistleblowerTip, None, None, None, None, None, None, None, None, None, None, None],
            'ReceiverTip': [models.ReceiverTip, None, None, None , None, None, None, None, None, None, None, None],
            'ReceiverInternalTip': [models.ReceiverInternalTip, None, None, None, None, None, None, None, None, None, None, None],
            'ReceiverContext': [models.ReceiverContext, None, None, None, None, None, None, None, None, None, None, None],
            'Message': [models.Message, None, None, None, None, None, None, None, None, None, None, None],
            'Stats': [Stats_v_14, None, None, None, None, None, None, Stats_v_16, None, models.Stats, None, None],
            'ApplicationData': [models.ApplicationData, None, None, None, None, None, None, None, None, None, None, None],
            'Field': [models.Field, None, None, None, None, None, None, None, None, None, None, None],
            'FieldOption': [models.FieldOption, None, None, None, None, None, None, None, None, None, None, None],
            'FieldField': [models.FieldField, None, None, None, None, None, None, None, None, None, None, None],
            'Step': [models.Step, None, None, None, None, None, None, None, None, None, None, None],
            'StepField': [models.StepField, None, None, None, None, None, None, None, None, None, None, None],
            'Anomalies': [models.Anomalies, None, None, None, None, None, None, None, None, None, None, None],
            'EventLogs': [models.EventLogs, None, None, None, None, None, None, None, None, None, None, None],
        }

        for k, v in self.table_history.iteritems():
            # +1 because count start from 0,
            # -8 because the relase befor the 8th are not supported anymore
            length = DATABASE_VERSION + 1 - 8
            if len(v) != length:
                msg = 'Expecting a table with {} statuses ({})'.format(length, k)
                raise TypeError(msg)


        log.msg('{} Opening old DB: {}'.format(self.debug_info, old_db_file))
        old_database = create_database('sqlite:'+self.old_db_file)
        self.store_old = Store(old_database)

        GLSetting.db_file = new_db_file

        new_database = create_database('sqlite:'+new_db_file)
        self.store_new = Store(new_database)

        if self.start_ver + 1 == DATABASE_VERSION:
            log.msg('{} Acquire SQL schema {}'.format(self.debug_info, GLSetting.db_schema_file))

            if not os.access(GLSetting.db_schema_file, os.R_OK):
                log.msg('Unable to access', GLSetting.db_schema_file)
                raise IOError('Unable to access db schema file')

            with open(GLSetting.db_schema_file) as f:
                create_queries = ''.join(f).split(';')
                for create_query in create_queries:
                    try:
                        self.store_new.execute(create_query+';')
                    except OperationalError:
                        log.msg('OperationalError in "{}"'.format(create_query))
            self.store_new.commit()
            return
            # return here and manage the migrant versions here:

        for k, v in self.table_history.iteritems():

            create_query = self.get_right_sql_version(k, self.start_ver + 1)
            if not create_query:
                # table not present in the version
                continue

            try:
                self.store_new.execute(create_query+';')
            except OperationalError as excep:
                log.msg('{} OperationalError in [{}]'.format(self.debug_info, create_query))
                raise excep

        self.store_new.commit()

    def close(self):
        self.store_old.close()
        self.store_new.close()

    def initialize(self):
        pass

    def epilogue(self):
        pass

    def get_right_model(self, table_name, version):

        table_index = (version - 8)

        if table_name not in self.table_history:
            msg = 'Not implemented usage of get_right_model {} ({} {})'.format(
                __file__, table_name, self.start_ver)
            raise NotImplementedError(msg)

        if version >  DATABASE_VERSION:
            raise ValueError('Version supplied must be less or equal to {}'.format(
                DATABASE_VERSION))

        if self.table_history[table_name][table_index]:
            return self.table_history[table_name][table_index]

        # else, it's none, and we've to take the previous valid version
        while version >= 0:
            if self.table_history[table_name][table_index]:
                return self.table_history[table_name][table_index]
            table_index -= 1

        # This never want happen
        return None

    def get_right_sql_version(self, model_name, version):
        """
        @param model_name:
        @param version:
        @return:
            The SQL right for the stuff we've
        """

        modelobj = self.get_right_model(model_name, version)
        if not modelobj:
            return None

        right_query = generateCreateQuery(modelobj)
        return right_query

    def _perform_copy_list(self, table_name):
        models_count = self.store_old.find(
            self.get_right_model(table_name, self.start_ver)
        ).count()
        log.msg('{} default {} migration assistant: #{}'.format(
            self.debug_info, table_name, models_count))

        old_objects = self.store_old.find(self.get_right_model(table_name, self.start_ver))

        for old_obj in old_objects:
            new_obj = self.get_right_model(table_name, self.start_ver + 1)()

            # Storm internals simply reversed
            for _, v in new_obj._storm_columns.iteritems():
                setattr(new_obj, v.name, getattr(old_obj, v.name) )

            self.store_new.add(new_obj)

        self.store_new.commit()

    def _perform_copy_single(self, table_name):
        log.msg('{} default {} migration assistant'.format(self.debug_info, table_name))

        old_obj = self.store_old.find(self.get_right_model(table_name, self.start_ver)).one()
        new_obj = self.get_right_model(table_name, self.start_ver + 1)()

        # Storm internals simply reversed
        for _, v in new_obj._storm_columns.iteritems():
            setattr(new_obj, v.name, getattr(old_obj, v.name) )

        self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_Context(self):
        self._perform_copy_list("Context")

    def migrate_Node(self):
        self._perform_copy_single("Node")

    def migrate_User(self):
        self._perform_copy_list("User")

    def migrate_ReceiverTip(self):
        self._perform_copy_list("ReceiverTip")

    def migrate_WhistleblowerTip(self):
        self._perform_copy_list("WhistleblowerTip")

    def migrate_Comment(self):
        self._perform_copy_list("Comment")

    def migrate_InternalTip(self):
        self._perform_copy_list("InternalTip")

    def migrate_Receiver(self):
        self._perform_copy_list("Receiver")

    def migrate_InternalFile(self):
        self._perform_copy_list("InternalFile")

    def migrate_ReceiverFile(self):
        self._perform_copy_list("ReceiverFile")

    def migrate_Notification(self):
        self._perform_copy_single("Notification")

    def migrate_ReceiverContext(self):
        self._perform_copy_list("ReceiverContext")

    def migrate_ReceiverInternalTip(self):
        self._perform_copy_list("ReceiverInternalTip")

    def migrate_Message(self):
        """
        has been created between 7 and 8!
        """
        if self.start_ver < 8:
            return

        self._perform_copy_list("Message")

    def migrate_Stats(self):
        """
        has been created between 14 and 15
        and is not migrated since 17
        """
        if self.start_ver < 17:
            return

        self._perform_copy_list("Stats")

    def migrate_ApplicationData(self):
        """
        There is no need to migrate it the application data.
        Default application data is loaded by the application
        and stored onto the db at each new start.
        """
        return

    def migrate_Field(self):
        """
        has been created between 14 and 15!
        """
        if self.start_ver < 15:
            return

        self._perform_copy_list("Field")

    def migrate_FieldOption(self):
        """
        has been created between 14 and 15!
        """
        if self.start_ver < 15:
            return

        self._perform_copy_list("FieldOption")

    def migrate_FieldField(self):
        """
        has been created between 14 and 15!
        """
        if self.start_ver < 15:
            return

        self._perform_copy_list("FieldField")

    def migrate_Step(self):
        """
        has been created between 14 and 15!
        """
        if self.start_ver < 15:
            return

        self._perform_copy_list("Step")

    def migrate_StepField(self):
        """
        has been created between 14 and 15!
        """
        if self.start_ver < 15:
            return

        self._perform_copy_list("StepField")

    def migrate_Anomalies(self):
        """
        has been created between 14 and 15!
        """
        if self.start_ver < 15:
            return

        self._perform_copy_list("Anomalies")

    def migrate_EventLogs(self):
        """
        has been created between 15 and 16!
        """
        if self.start_ver < 16:
            return

        self._perform_copy_list("EventLogs")
