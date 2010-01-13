#
# RhaptosModuleStorage tests
#
"""
import os, sys, shutil, stat, psycopg
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.RhaptosSite.tests.RhaptosTestCase import RhaptosTestCase
from Products.CMFPlone.tests.PloneTestCase import default_user
from Products.RhaptosRepository.interfaces.IVersionStorage import IVersionStorage

from Products.RhaptosModuleStorage.Extensions import Install as DBInstall

from Testing import ZopeTestCase


ZopeTestCase.installProduct('RhaptosModuleEditor')
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

#class TestModuleVersionStorage(RhaptosTestCase):
class TestModuleVersionStorage:
    """Test the VersionStorage methods """

    def _safeDropDB(self):
        """Drop the test database, but don't error if it doesn't exist"""
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
        """Create a new test database"""
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
        """Drop the test user, but don't error if it doesn't exist"""
        try:
            DBInstall._dbadminexec(DB_OPTS, 'DROP USER %s' % DB_OPTS['user'], template=True)
        except psycopg.ProgrammingError, e:
            if 'does not exist' in str(e) or 'user owns database' in str(e):
                pass
            else:
                raise        

    def afterSetUp(self):
        RhaptosTestCase.afterSetUp(self)
        
        DB_OPTS.update(self.portal._dbopts)
        #print DB_OPTS

        # Blow away leftover test user/db from previous runs
        self._safeDropDB()
        self._safeDropUser()
        self._safeCreateDB()

        self.portal.portal_quickinstaller.installProduct('Archetypes')
        self.portal.portal_quickinstaller.installProduct('CatalogMemberDataTool')
        self.portal.portal_quickinstaller.installProduct('PloneLanguageTool')
        self.portal.portal_quickinstaller.installProduct('RhaptosRepository')
        self.portal.portal_quickinstaller.installProduct('RhaptosHitCountTool')
        self.portal.portal_quickinstaller.installProduct('RhaptosModuleEditor')
        self.portal.portal_quickinstaller.installProduct('CNXMLDocument')
        self.portal.portal_quickinstaller.installProduct('FSImportTool')
        self.portal.portal_quickinstaller.installProduct('RhaptosModuleStorage')

        self.content = self.portal.content
        self.storage = self.content.module_version_storage


        # XXX: This hack is required for several places in our code
        # where we depend on the 'desecured.getMemberById' method in
        # the RhaptosSite skin.  We should stop using this wherever
        # possible, but in the meantime...
        self.loginPortalOwner()
        self.portal.invokeFactory('Folder', 'desecured')
        self.portal.desecured.manage_addProduct['PythonScripts'].manage_addPythonScript('getMemberById')
        self.portal.desecured.getMemberById.ZPythonScript_edit('id', 'return context.portal_membership.getMemberById(id)')
        self.portal.desecured.getMemberById.manage_proxy(roles=('Manager',))
        self.logout()
        self.login()

        self.folder.invokeFactory('Module', 'ob1')
        self.ob1 = self.folder.ob1
        self.ob1.createTemplate(['http://cnx.rice.edu/cnxml'])
        self.ob1.license = 'http://creativecommons.org/licenses/by/3.0/'

        self.folder.invokeFactory('Document', 'doc1')
        self.doc1 = self.folder.doc1
        
    def beforeTearDown(self):
        self._safeDropUser()
        self._safeDropDB()

    def testGetUnPublishedVersionInfo(self):
        """getVersionInfo() must return None for objects not under version control"""
        self.assertEquals(self.storage.getVersionInfo(self.ob1), None)

    def testGetVersionInfo(self):
        """Publishing the first one"""
        message = 'TEST VI'
        objectId = self.content.publishObject(self.ob1, message)
        self.ob1.setBaseObject(objectId)
        self.ob1.updateMetadata()
        vi = self.storage.getVersionInfo(self.ob1)
        self.assertEqual(vi.objectId, 'm10000')
        self.assertEqual(vi.version, '1.1')
        self.assertEqual(vi.user, default_user)
        self.assertEqual(vi.state, 'public')

        # XXX: This currently fails because the module storage does not return the message
        #self.assertEqual(vi.message, message)

    def testGenerateId(self):
        """generateId() must generate unique IDs"""
        # XXX: Is there a better way to test this
        # XXX: It appears this test depends on the order the tests are run in.  If its not run first, it will fail
        self.assertEqual(self.storage.generateId(), 'm10000')
        self.assertEqual(self.storage.generateId(), 'm10001')
        self.assertEqual(self.storage.generateId(), 'm10002')
        self.assertEqual(self.storage.generateId(), 'm10003')
        self.assertEqual(self.storage.generateId(), 'm10004')
        self.assertEqual(self.storage.generateId(), 'm10005')

    def testHasObjectFalse(self):
        """hasObject must return false if no such object is stored"""
        self.failIf(self.storage.hasObject('m10000'))

    def testHasObjectTrue(self):
        """hasObject must return True if the object is stored"""
        message = 'TEST HASOBJECT'
        objectId = self.content.publishObject(self.ob1, message)
        self.ob1.setBaseObject(objectId)
        self.ob1.updateMetadata()
        self.failUnless(self.storage.hasObject(objectId))

    def testCountEmpty(self):
        """countObjects() must return 0 for an empty repository"""
        self.assertEqual(self.storage.countObjects(), 0)

    def testCountNonEmpty(self):
        """countObjects() must return correct number"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        self.ob1.setBaseObject(objectId)
        self.ob1.updateMetadata()

        self.assertEqual(self.storage.countObjects(), 1)

    def testCountNonEmpty(self):
        """countObjects() must return correct number for specified portal_type"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        self.ob1.setBaseObject(objectId)
        self.ob1.updateMetadata()
        self.assertEqual(self.storage.countObjects(portal_types=['Module']), 1)

    def testCountOtherPortalType(self):
        """countObjects() should not count objects of the wrong portal_type"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        self.ob1.setBaseObject(objectId)
        self.ob1.updateMetadata()
        self.assertEqual(self.storage.countObjects(portal_types=['Foo']), 0)

    def testGetObjectBadIdFails(self):
        """getObject() must raise KeyError for non-existant ID"""
        self.assertRaises(KeyError, self.storage.getObject, 'foobar')

    def testGetObjectBadVersionFails(self):
        """getObject() must raise KeyError for non-existant version"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        self.assertRaises(KeyError, self.storage.getObject, objectId, '1.7')

    def testGetObjectNoVersion(self):
        """getObject() must correctly return unversioned object"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        obj = self.storage.getObject(objectId)
        self.assertEquals(obj.getId(), objectId)

    def testGetObjectLatest(self):
        """getObject() must correctly return latest object"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        obj = self.storage.getObject(objectId, 'latest')
        self.assertEquals(obj.objectId, objectId)
        self.assertEquals(obj.version, '1.1')

    def testGetObjectVersion(self):
        """getObject() must correctly return versioned object"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        obj = self.storage.getObject(objectId, '1.1')
        self.assertEquals(obj.objectId, objectId)
        self.assertEquals(obj.version, '1.1')

    def testIsUnderVersionControlFalse(self):
        """isUnderVersionControl() must correctly return false for unversioned object"""
        self.assertEquals(self.storage.isUnderVersionControl(self.doc1), False)

    def testIsUnderVersionControlFalseModule(self):
        """isUnderVersionControl() must correctly return false for unversioned module"""
        self.assertEquals(self.storage.isUnderVersionControl(self.ob1), False)

    def testIsUnderVersionControlTrue(self):
        """isUnderVersionControl() must correctly return true for published module"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        obj = self.storage.getObject(objectId, '1.1')
        self.assertEquals(self.storage.isUnderVersionControl(obj), True)

    def testIsUnderVersionControlTrue(self):
        """isUnderVersionControl() must correctly return true for published module in workspace"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        self.assertEquals(self.storage.isUnderVersionControl(self.ob1), True)
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
