#
# RhaptosModuleStorage installation tests
#

import psycopg
import time
import sys
import os
"""
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.RhaptosSite.tests.RhaptosTestCase import RhaptosTestCase
from CMFTestCase import CMFTestCase
#from Products.RhaptosModuleStorage.Extensions import Install as DBInstall
#from Products.RhaptosModuleStorage.Extensions import Install as DBInstall
"""
"""
# Global Database options for testing.  You may have to change these 
DB_OPTS = {
    'admin':'postgres',
    'adminpass':None,
    'user':'testrun',
    'userpass':None,
    'dbname':'testdb',
    'server':'localhost',
    'port':None
    }
"""
"""
class TestModuleVersionStorage(RhaptosTestCase):
"""
"""Test the VersionStorage methods """
"""    
    def _safeDropDB(self):
        #Drop the test database, but don't error if it doesn't exist
        DAname = DB_OPTS['dbname']+'DA'
        try:
            self.portal[DAname].manage_close_connection()
            self.portal.manage_delObjects(DAname)
        except KeyError:
            pass
        
        try:
            DBInstall._dbadminexec(DB_OPTS, 'DROP DATABASE %s' % DB_OPTS['dbname'], template=True)
        except psycopg.ProgrammingError, e:
            if 'does not exist' in str(e):
                pass
            else:
                raise

    def _safeCreateDB(self):
        #Create a new test database
        try:
            #DBInstall._dbadminexec(DB_OPTS, 'CREATE DATABASE %s' % DB_OPTS['dbname'], template=True)
            #DBInstall.installdb(self.portal)
            DBInstall.setupDBConnection(self.portal, self.portal)
            DBInstall.installdb(self.portal)
        except psycopg.ProgrammingError, e:
            if 'already exists' in str(e):
                pass
            else:
                raise
            
    def _safeDropUser(self):
        #Drop the test user, but don't error if it doesn't exist
        try:
            DBInstall._dbadminexec(DB_OPTS, 'DROP USER %s' % DB_OPTS['user'], template=True)
        except psycopg.ProgrammingError, e:
            if 'does not exist' in str(e) or 'user owns database' in str(e):
                pass
            else:
                raise        

    def _safeRemoveStorage(self):
        #Remove the Module Storage object and unregister it with RhaptosRepository
        try:
            storage = self.portal.content.getStorageForType('Module')
            self.portal.content.removeStorage(storage.id)
        except KeyError:
            pass

    def afterSetUp(self):
        RhaptosTestCase.afterSetUp(self)
        
        DB_OPTS.update(self.portal._dbopts)
        # Blow away leftover test user/db from previous runs
        self._safeDropDB()
        self._safeDropUser()
        self._safeRemoveStorage()

    def beforeTearDown(self):
        self._safeDropDB()
        self._safeDropUser()
        self._safeRemoveStorage()


    def testFullInstall(self):
        #DB Install must succeed with absolutely nothing prepared beforehand
        opts  = DB_OPTS.copy()
        self.portal._dbopts = opts
        DBInstall.install(self.portal)

    def testFullInstallNoAdminFails(self):
        #Full DB install must fail if admin not provided
        opts  = DB_OPTS.copy()
        opts['admin'] = None
        self.portal._dbopts = opts
        self.assertRaises(psycopg.ProgrammingError, DBInstall.install, self.portal)

    def testFullInstallBadAdminFails(self):
        #Install must fail if bad admin provided
        opts  = DB_OPTS.copy()
        opts['admin'] = 'nonexistantadmin'
        self.portal._dbopts = opts
        self.assertRaises(ValueError, DBInstall.install, self.portal)
        
    def testCreateUser(self):
        #create_user must successfully create DB user
        opts  = DB_OPTS.copy()
        self.failIf(DBInstall.user_exists(opts))
        DBInstall.create_user(opts)
        self.failUnless(DBInstall.user_exists(opts))

    def testCreateUserPassword(self):
        #create_user must successfully create DB user with a password
        opts  = DB_OPTS.copy()
        opts['userpass'] = 'foo'
        self.failIf(DBInstall.user_exists(opts))
        DBInstall.create_user(opts)
        self.failUnless(DBInstall.user_exists(opts))

    def testCreateDB(self):
        #create_database must successfully create DB
        opts  = DB_OPTS.copy()
        DBInstall.create_user(opts)
        self.failIf(DBInstall.database_exists(opts))
        DBInstall.create_database(opts)
        self.failUnless(DBInstall.database_exists(opts))

    def testInstallUserExists(self):
        #DB Install must succeed when passed an existing user
        opts  = DB_OPTS.copy()
        self.failIf(DBInstall.user_exists(opts))
        DBInstall.create_user(opts)
        self.portal._dbopts = opts
        DBInstall.install(self.portal)
        # XXX: We must verify that the supplied user owns the DB or something

    def testInstallUserExistsNoAdminFails(self):
        #DB install with existing user must fail if admin not provided
        opts  = DB_OPTS.copy()
        self.failIf(DBInstall.user_exists(opts))
        DBInstall.create_user(opts)

        opts['admin'] = None
        self.portal._dbopts = opts
        self.assertRaises(psycopg.ProgrammingError, DBInstall.install, self.portal)

    def testInstallDBExists(self):
        #DB Install must succeed when passed an existing database
        opts  = DB_OPTS.copy()

        self.failIf(DBInstall.database_exists(opts))
        DBInstall.create_database(opts)
        self.portal._dbopts = opts
        DBInstall.install(self.portal)
        # XXX: We must verify that the schema was correctly created or something

    def testInstallDBExistsNoAdminFails(self):
        #DB install with existing DB must fail if admin not provided
        opts  = DB_OPTS.copy()
        self.failIf(DBInstall.database_exists(opts))
        DBInstall.create_database(opts)

        opts['admin'] = None
        self.portal._dbopts = opts
        self.assertRaises(psycopg.ProgrammingError, DBInstall.install, self.portal)

    def testInstallPLpgSQLInstalled(self):
        #DB Install must succeed when passed an existing database with PL/pgSQL installed
        opts  = DB_OPTS.copy()

        self.failIf(DBInstall.database_exists(opts))
        DBInstall.create_database(opts)
        DBInstall.install_plpgsql(opts)
        self.portal._dbopts = opts
        DBInstall.install(self.portal)
        # XXX: We must verify that the schema was correctly created or something

    def testInstallTSearchInstalled(self):
        #DB Install must succeed when passed an existing database with tsearch installed
        opts  = DB_OPTS.copy()

        self.failIf(DBInstall.database_exists(opts))
        DBInstall.create_database(opts)
        DBInstall.install_tsearch(opts)
        self.portal._dbopts = opts
        DBInstall.install(self.portal)
        # XXX: We must verify that the schema was correctly created or something

    def testInstallPLpgSQLAndTsearchInstalled(self):
        #DB Install must succeed when passed an existing database with tsearch and PL/pgSQL installed
        opts  = DB_OPTS.copy()

        self.failIf(DBInstall.database_exists(opts))
        DBInstall.create_database(opts)
        DBInstall.install_plpgsql(opts)
        DBInstall.install_tsearch(opts)
        self.portal._dbopts = opts
        DBInstall.install(self.portal)
        # XXX: We must verify that the schema was correctly created or something

    def testInstallPLpgSQLAndTsearchInstalledNoAdmin(self):
        #DB Install must succeed when passed an existing database with tsearch and PL/pgSQL installed and no admin account
        opts  = DB_OPTS.copy()

        self.failIf(DBInstall.database_exists(opts))
        DBInstall.create_database(opts)
        DBInstall.install_plpgsql(opts)
        DBInstall.install_tsearch(opts)
        DBInstall.create_user(opts)
        
        opts['admin'] = None
        self.portal._dbopts = opts
        DBInstall.install(self.portal)
        # XXX: We must verify that the schema was correctly created or something

"""        
"""               
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestModuleVersionStorage))
        return suite
"""
