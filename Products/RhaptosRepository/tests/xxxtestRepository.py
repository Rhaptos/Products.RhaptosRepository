#
# RhaptosRepository tests
#

import os, sys, shutil, stat
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import tempfile
from BaseTestCase import BaseTestCase

class TestRepository(BaseTestCase):
    """Test the portal_fsimport tool's export function"""
    
    def testInterfaces(self):
        """Ensure that tool instances implement the correct interface"""
        from Products.RhaptosRepository.interfaces.IRepository import IRepository
        from Products.RhaptosRepository.interfaces.IVersionStorage import IStorageManager
        #from Products.ZopeVersionControl.IVersionControl import IVersionControl
        
        self.failUnless(IRepository.isImplementedBy(self.content))
        self.failUnless(IStorageManager.isImplementedBy(self.content))
        #self.failUnless(IVersionControl.isImplementedBy(self.content))

    def testHasRhaptosObjectWithNone(self):
        """hasRhaptosObject() must return False if None is given as the ID"""
        self.assertEquals(self.content.hasRhaptosObject(None), False)

    def testGetRhaptosObjectBadIdFails(self):
        """getRhaptosObject() must raise KeyError for non-existant ID"""
        self.assertRaises(KeyError, self.content.getRhaptosObject, 'foobar')

    def testGetHistoryWithNone(self):
        """getHistory must return for None ID"""
        self.assertEquals(self.content.getHistory(None), None)

    def testGetHistoryForUnpublished(self):
        """getHistory must return None for non-existant ID"""
        self.assertEquals(self.content.getHistory('foobar'), None)

        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestRepository))
        return suite

