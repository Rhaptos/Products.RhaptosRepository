#
# RhaptosRepository tests
#

import os, sys, shutil, stat
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from BaseTestCase import BaseTestCase
from Products.RhaptosRepository.interfaces.IVersionStorage import IVersionStorage

class TestVersionFolderStorage(BaseTestCase):
    """Test the VersionStorage methods """

    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)
        self.storage = self.portal.content.version_folder_storage

    def testInterfaces(self):
        """Ensure that tool instances implement the correct interface"""
        self.failUnless(IVersionStorage.providedBy(self.storage))

    def testGetVersionInfoNonVersioned(self):
        """getVersionInfo() must return None for objects not under version control"""
        self.assertEquals(self.storage.getVersionInfo(self.doc1), None)

    def testGetVersionInfo(self):
        message = 'TEST VI'
        # XXX: This currently fails because VersionFolderStorage expects objects to have a getState() method
        self.content.publishObject(self.doc1, message)
        vi = self.storage.getVersionInfo(self.doc1)

    def testGenerateId(self):
        """generateId() must generate unique IDs"""
        # XXX: Is there a better way to test this
        self.assertEqual(self.storage.generateId(), 'col10001')
        self.assertEqual(self.storage.generateId(), 'col10002')
        self.assertEqual(self.storage.generateId(), 'col10003')
        self.assertEqual(self.storage.generateId(), 'col10004')
        self.assertEqual(self.storage.generateId(), 'col10005')
    
    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestVersionFolderStorage))
        return suite

