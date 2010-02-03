from Products.CMFCore.utils import getToolByName
from Products.RhaptosModuleStorage import product_globals
from Products.RhaptosModuleStorage.ModuleVersionFolder import ModuleVersionStorage
from Globals import package_home
from StringIO import StringIO
import string
import psycopg2.psycopg1 as psycopg
import time
from Products.RhaptosModuleStorage.config import RATE_MODULE_PERMISSION
 
DEFAULT_DB_OPTS = {'admin':'rhaptos_dba',
                   'adminpass':None,
                   'user':'rhaptos',
                   'userpass':None,
                   'dbname':'repository',
                   'server':None,
                   'port':None,
                   }


def _execute_retry(cursor, command, attempts=3, delay=1):
    """
    Execute 'command' in the specified DB 'cursor'

    If the command fails because the resource is being accessed by
    another user, attempt again after a delay.

    attempts: maximum number of retries
    delay   : nuymber of seconds to sleep between attempts
    """
    for n in range(attempts):
        try:
            cursor.execute(command)
            break
        except psycopg.ProgrammingError, e:
            if 'is being accessed by other users' in str(e):
                time.sleep(delay)
                continue
            else:
                raise
    else:
        raise psycopg.ProgrammingError, "Failed after %d attempts to execute DB command %s: %s" % (attempts, command, e)
    

def _dsn(dd, **kwargs):
    d = dd.copy()
    
    for k in kwargs:
        d[k]=kwargs[k]
        
    return 'dbname=%s' % d['dbname'] + ['',' user=%s' % d['user']][bool(d['user'])] + ['',' password=%s' % d['userpass']][bool(d['userpass'])] + ['', ' host=%s' % d['server']][bool(d['server'])] + ['', ' port=%s' % d['port']][bool(d['port'])]


def _dbadminexec(d, execstring, template=False):
    """Execute a command as the DB admin using arguments from 'd' """
    try:
        if template:
            dsn = _dsn(d, dbname='template1', user=d['admin'], password=d['adminpass'])
        else:
            dsn = _dsn(d, user=d['admin'], password=d['adminpass'])
        con = psycopg.connect(dsn)
    except psycopg.OperationalError, e:
        # Badadmin Username: Fail back to user
        raise ValueError, "Unable to connect as supplied DBA admin - %s " %e
    con.set_isolation_level(0)
    c = con.cursor()
    try:
        _execute_retry(c, execstring)
    except psycopg.ProgrammingError, e:
        con.close()
        raise

    con.close()


def create_user(args):
    user = args['user']
    password = args.get('userpass', None)
    command = 'CREATE USER %s' % user + (password and " PASSWORD '%s'" % password or '')
    _dbadminexec(args, command, template=True) 

def user_exists(args):
    try:
        con = psycopg.connect(_dsn(args, dbname='template1'))
    except psycopg.OperationalError, e:
        if 'does not exist' in str(e):
            return False
        else:
            raise
        
    con.close()
    return True

def create_database(args):
    command = 'CREATE DATABASE "%s"' % args['dbname']
    _dbadminexec(args, command, template=True)

def database_exists(args):
    try:
        con = psycopg.connect(_dsn(args))
    except psycopg.OperationalError, e:
        # Database doesn't exist
        if str(e) == 'FATAL:  database "%s" does not exist\n' % args['dbname']:
            return False
        else:
            raise

    con.close()
    return True

def install_plpgsql(args):
    command = """CREATE FUNCTION "plpgsql_call_handler" () RETURNS language_handler AS '$libdir/plpgsql' LANGUAGE C;
    CREATE TRUSTED LANGUAGE "plpgsql" HANDLER "plpgsql_call_handler";"""
    try:
        _dbadminexec(args, command)
    except psycopg.ProgrammingError, e:
        if 'ERROR:  function "plpgsql_call_handler" already exists with same argument types\n' in str(e):
            pass
        else:
            raise
    
def install_tsearch(args):
    ph = package_home(product_globals)
    tsearch_paths = ['/usr/share/postgresql/8.3/contrib/tsearch2.sql',
                     '/usr/share/postgresql/8.2/contrib/tsearch2.sql',
                     ph+'/sql/tsearch2.sql']
    for ts_file in tsearch_paths:
        try:
            ts_schema = open(ts_file,'r').read()
            break
        except IOError:
            pass # find first working one

    _dbadminexec(args, ts_schema)
    command = """
        grant all on pg_ts_cfg to public;
        grant all on pg_ts_cfgmap to public;
        grant all on pg_ts_dict to public;
        grant all on pg_ts_parser to public;
        update pg_ts_cfg set locale = (select current_setting('lc_collate')) where ts_name = 'default';
        """
    _dbadminexec(args, command)

    return ts_file

def setupModuleStorage(context):
    """Set up database adapter, moduledb tool, create database,
    register as RhaptosRepository storage, and more.
    """
    logger = context.getLogger('rhaptos-modulestorage')
    if context.readDataFile('rhaptosmodulestorage.txt') is None:
        logger.info('Nothing to import.')
        return
    portal = context.getSite()
    
    
    dbtool = getToolByName(portal, 'portal_moduledb', None)
    if not dbtool or not dbtool.db:
        # lack of dbtool with DA string indicates we need to create DB and DA
        logger.info("...setting up DB connection")
        setupDBConnection(portal, portal)
        d = portal._dbopts

        dbtool.setDB(d['dbname']+'DA')

        logger.info(installdb(portal))
    else:
        # we have a DA string, so do any upgrades necessary to the schema
        # FIXME: store a version of the schema somewhere so we can do upgrade work here
        pass

    # Register ModuleVersion storage
    STORAGE = 'module_version_storage'
    if not STORAGE in portal.content.listStorages():
        logger.info("...registering storage: %s" % STORAGE)
        portal.content.registerStorage(ModuleVersionStorage(STORAGE))
        portal.content.setStorageForType('Module', STORAGE)

    # create dummy portal type for ModuleViews
    # FIXME: COMMENTED until such time as we want to have a different portal_type for ModuleView
    # see also ModuleView.py
    # (see )
    #TYPE = 'PublishedModule'
    #typestool = getToolByName(portal, 'portal_types')
    #if not typestool.getTypeInfo(TYPE):
        #logger.info("...registering dummy type: %s" % TYPE)
        #typestool.manage_addTypeInformation(id=TYPE, add_meta_type="Factory-based Type Information")
        #dummytype = getattr(typestool, TYPE)
        #dummytype.manage_changeProperties(title="Published Module",
                                          #description="Dummy type for RhaptosModuleStorage.ModuleView stubs.",
                                          #global_allow=0,
                                          #allow_discussion=0,
                                          #filter_content_types=1,
                                          #allowed_content_types=())
   
    # Setup permission
    logger.info("Completed Install of RhaptosModuleStorage")

def setupDBConnection(self, portal):
    """Set up the database"""
    out = StringIO()
    
    # Create the Database Connection
    if not hasattr(portal.aq_base,'_dbopts'):
        if 'DB_OPTS_TEMP' in portal.aq_parent.objectIds():
            portal._dbopts = getattr(portal.aq_parent['DB_OPTS_TEMP'],'_dbopts',DEFAULT_DB_OPTS).copy()
            portal.aq_parent.manage_delObjects(['DB_OPTS_TEMP'])
        else:
            # This an old ZMI which makes upgrading difficult. Attempt to
            # extract authentication credentials from Z Psycopg connection.
            if 'devrep' not in portal.aq_parent.objectIds():
                raise "No Z Psycoppg Database Connection found"
            db = portal.aq_parent.devrep
            # Attempt to parse the connection string. Abort on any error
            # by letting the exception propagate.
            items = db.connection_string.split(' ')
            settings = {}
            for item in items:
                k, v = item.split('=')
                settings[k] = v
            portal._dbopts = {}
            portal._dbopts['admin'] = settings.get('user', '')
            portal._dbopts['adminpass'] = settings.get('password', '')
            portal._dbopts['user'] = settings.get('user', '')
            portal._dbopts['userpass'] = settings.get('password', '')
            portal._dbopts['dbname'] = settings.get('dbname', '')
            portal._dbopts['server'] = ''
            portal._dbopts['port'] = ''

    d = portal._dbopts

    if not user_exists(d):
        create_user(d)
        out.write('Created user %(user)s\n' %d)

    # We now have a regular database username provided
    if not database_exists(d):
        create_database(d)
        out.write('Created database %(dbname)s\n' %d)

    # We now have an existing database
    con = psycopg.connect(_dsn(d))
    c = con.cursor()
    c.execute("SELECT 1 FROM pg_class WHERE relname='modules'")
    if c.rowcount:
        raise ValueError, "Database populated, not using to avoid dataloss"

    c.execute("SELECT 1 FROM pg_language WHERE lanname='plpgsql'")
    if not c.rowcount:
        install_plpgsql(d)
        out.write('Install plpgsql in database %(dbname)s\n' %d)

    c.execute("SELECT 1 FROM pg_type WHERE typname='tsquery'")
    if not c.rowcount:
        ts_location = install_tsearch(d)
        out.write('Install tsearch in database %s from %s\n' %(d['dbname'], ts_location))

    # Finally ready to create the Database Adapter
    portal.manage_addProduct['ZPsycopgDA'].manage_addZPsycopgConnection(id=d['dbname']+'DA',title='Rhaptos Repository DA',encoding='utf-8',connection_string=_dsn(d), zdatetime=True)
    out.write('Install Database Adapter in %s for database %s\n' %(portal.Title(), d['dbname']))
        

def installdb(self):
    """Install database schema, including pl/pgsql and tsearch"""

    out = StringIO()
    ph = package_home(product_globals)

    rep = getToolByName(self, 'portal_moduledb')
    db=getattr(self,rep.db)

    schema = open(ph+'/sql/db_schema.sql','r').read()
    db.manage_test(query=schema)
    out.write("Initialized Rhaptos DB schema\n")
    schema = open(ph+'/sql/licenses.sql','r').read()
    db.manage_test(query=schema)
    out.write("Initialized content licenses\n")
    schema = open(ph+'/sql/states.sql','r').read()
    db.manage_test(query=schema)
    out.write("Initialized module states\n")
    return out.getvalue()
