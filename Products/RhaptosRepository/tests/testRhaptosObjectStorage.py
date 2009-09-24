#
# RhaptosRepository tests with Rhaptos Content
#

import os, sys, shutil, stat
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from BaseTestCase import BaseTestCase
#from Products.CMFPlone.tests.PloneTestCase import PloneTestCase, default_user
from Products.RhaptosRepository.interfaces.IVersionStorage import IVersionStorage

from Testing import ZopeTestCase

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('RhaptosCollection')
ZopeTestCase.installProduct('RhaptosRepository')
ZopeTestCase.installProduct('RhaptosHitCountTool')
ZopeTestCase.installProduct('RhaptosModuleEditor')
ZopeTestCase.installProduct('ZAnnot')

#class TestRhaptosObjectStorage(PloneTestCase):
class TestRhaptosObjectStorage(BaseTestCase):
    """
    Test the VersionStorage methods with RhaptosObjects

    XXX: These tests are failing with a strange KeyError possible because of the manage_clone in createVersion()
    """

    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)

        self.portal.portal_quickinstaller.installProduct('PloneLanguageTool')
        
        self.storage = self.content.version_folder_storage
        self.folder.invokeFactory('Collection', 'ob1')
        self.ob1 = self.folder.ob1

#        self.folder.invokeFactory('Document', 'doc1')
#        self.doc1 = self.folder.doc1

    def testGetUnPublishedVersionInfo(self):
        """getVersionInfo() must return None for objects not under version control"""
        self.assertEquals(self.storage.getVersionInfo(self.ob1), None)

##     def testGetVersionInfo(self):
##         """Publishing the first one"""
##         message = 'TEST VI'
##         #self.ob1.publishContent(message)
##         objectId = self.content.publishObject(self.ob1, message)
##         self.ob1.setBaseObject(objectId)
##         self.ob1.updateMetadata()
##         self.ob1.logAction('submit', message)
##         vi = self.storage.getVersionInfo(self.ob1)
##         self.assertEqual(vi.objectId, 'col10001')
##         self.assertEqual(vi.version, '1.1')
##         self.assertEqual(vi.message, message)
##         self.assertEqual(vi.user, default_user)
##         self.assertEqual(vi.state, 'public')

    def testHasObjectFalse(self):
        """hasObject must return false if no such object is stored"""
        self.failIf(self.storage.hasObject('col10001'))

    def testHasObjectTrue(self):
        """hasObject must return True if the object is stored"""
        objectId = self.content.publishObject(self.ob1, 'foo')
        #self.ob1.setBaseObject(objectId)
        #self.ob1.updateMetadata()
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

        self.assertEqual(self.storage.countObjects(['Collection']), 1)

    def testCountOtherPortalType(self):
        """countObjects() should not count objects of the wrong portal_type"""
        # XXX: Thus currently fails because the DB queries are not aware of portal_types yet
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        self.ob1.setBaseObject(objectId)
        self.ob1.updateMetadata()

        self.assertEqual(self.storage.countObjects(portal_types=['Foo']), 0)

    def testGetObjectBadIdFails(self):
        """getObject() must raise KeyError for non-existant ID"""
        # XXX: Currently fails because ModuleVersionStorage blindly returns an object if even if doesn't exist in the DB
        self.assertRaises(KeyError, self.storage.getObject, 'foobar')

    def testGetObjectBadVersionFails(self):
        """getObject() must raise KeyError for non-existant version"""
        message = 'TEST PUBLISH'
        objectId = self.content.publishObject(self.ob1, message)
        # XXX: Currently fails because ModuleVersionStorage blindly returns an object if even if doesn't exist in the DB
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


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestRhaptosObjectStorage))
        return suite

