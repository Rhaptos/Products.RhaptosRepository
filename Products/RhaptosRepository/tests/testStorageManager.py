#
# RhaptosRepository tests
#

import os, sys, shutil, stat
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import tempfile
from OFS.SimpleItem  import SimpleItem

from BaseTestCase import BaseTestCase
from Products.RhaptosRepository.interfaces.IVersionStorage import IVersionStorage, IStorageManager

class DummyStorage(SimpleItem):

    __implements__ = (IVersionStorage)

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id


class TestStorageManager(BaseTestCase):
    """Test the StorageManager functions """
        
    def testInterfaces(self):
        """Ensure that tool instances implement the correct interface"""
        self.failUnless(IStorageManager.isImplementedBy(self.content))

    def testRegisterNonStorage(self):
        """registerStorage must raise TypeError if storage does not implement IVersionStorage"""
        self.assertRaises(TypeError, self.content.registerStorage, 'foo', None)

    def testRegisterDuplicateStorage(self):
        """registerStorage must raise ValueError if storage already registered with that ID"""
        name = 'dummy'
        s1 = DummyStorage(name)
        s2 = DummyStorage(name)
        self.content.registerStorage(s1)
        self.assertRaises(ValueError, self.content.registerStorage, s2)

    def testRegisterStorage(self):
        """registerStorage must register storage object"""
        name = 'dummy'
        s = DummyStorage(name)
        self.content.registerStorage(s)
        self.failUnless(name in self.content.listStorages())
        self.assertEqual(s, self.content.getStorage(name).aq_base)

    def testGetStorageBad(self):
        """getStorage must rairse KeyError if ID not registered"""
        self.assertRaises(KeyError, self.content.getStorage, 'foo')
        
    def testGetStorageWorks(self):
        """getStorage must return the correct storage"""
        s1 = DummyStorage('foo')
        s2 = DummyStorage('bar')
        self.content.registerStorage(s1)
        self.content.registerStorage(s2)
        self.assertEqual(s2, self.content.getStorage('bar').aq_base)

    def testGetStorageAcquisitionWrapper(self):
        """getStorage must return the correct storage"""
        s1 = DummyStorage('foo')
        self.content.registerStorage(s1)
        self.assertEqual(self.content, self.content.getStorage('foo').aq_parent)

    def testRemoveStorageBad(self):
        """removeStorage must raise KeyError if ID not registered"""
        self.assertRaises(KeyError, self.content.removeStorage, 'foo')

    def testRemoveStorageWorks(self):
        """removeStorage must correctly remove the specified storage"""
        s1 = DummyStorage('foo')
        s2 = DummyStorage('bar')
        self.content.registerStorage(s1)
        self.content.registerStorage(s2)
        self.content.removeStorage('foo')
        storages = self.content.listStorages()
        self.failUnless('bar' in storages)
        self.failIf('foo' in storages)
        
    def getDefaultReturnsNone(self):
        """getDefaultStorage must return None if there is no default"""
        self.assertEqual(None, self.content.getDefaultStorage())
        
    def setDefaultStorageBad(self):
        """setDefaultStorage must raise KeyError if ID not registered"""
        self.assertRaises(KeyError, self.content.setDefaultStorage, 'foo')

    def setDefaultStorageWorks(self):
        """getDefaultStorage must return correct storage when set"""
        s1 = DummyStorage('foo')
        s2 = DummyStorage('bar')
        self.content.registerStorage(s1)
        self.content.registerStorage(s2)
        self.content.setDefaultStorage('foo')
        self.assertEqual(s1, self.content.getDefaultStorage().aq_base)

    def testGetDefaultStorageAcquisitionWrapper(self):
        """getStorage must return the correct storage"""
        s1 = DummyStorage('foo')
        self.content.registerStorage(s1)
        self.content.setDefaultStorage('foo')
        self.assertEqual(self.content, self.content.getDefaultStorage().aq_parent)

    def setDefaultStorageToNoneWorks(self):
        """setDefaultStorage with None as argument must clear default"""
        s1 = DummyStorage('foo')
        self.content.registerStorage(s1)
        self.content.setDefaultStorage('foo')
        self.content.setDefaultStorage(None)
        self.assertEqual(None, self.content.getDefaultStorage())

    def testRemoveDefaultResetsDefault(self):
        """getDefaultStorage must return None if the default gets removed"""
        s1 = DummyStorage('foo')
        self.content.registerStorage(s1)
        self.content.setDefaultStorage('foo')
        self.content.removeStorage('foo')
        self.assertEqual(None, self.content.getDefaultStorage())

    def setStorageForTypeBad(self):
        """setStorageForType must raise KeyError if ID not registered"""
        self.assertRaises(KeyError, self.content.setStorageForType, 'Document', 'foo')

    def setStorageForTypeWorks(self):
        """setStorageForType must correctly register portal type"""
        s1 = DummyStorage('foo')
        self.content.registerStorage(s1)
        self.content.setStorageForType('Document', 'foo')
        self.assertEqual(s1, self.getStorageForType('Document').aq_base)

    def getStorageForTypeReturnsDefault(self):
        """getStorageForType returns default storage is not set"""
        s1 = DummyStorage('foo')
        self.content.registerStorage(s1)
        self.content.setDefaultStorage('foo')
        self.assertEqual(s1, self.content.getStorageForType('Document').aq_base)

    def getStorageForTypeReturnsNoneDefault(self):
        """getStorageForType returns None if default storage is not set"""
        self.assertEqual(None, self.content.getStorageForType('Document'))

    def testRemoveTypeResetsPortalTypesToDefault(self):
        """getStorageForType must return default if set storage is removed"""
        s1 = DummyStorage('foo')
        s2 = DummyStorage('bar')
        self.content.registerStorage(s1)
        self.content.registerStorage(s2)
        self.content.setDefaultStorage('foo')
        self.content.setStorageForType('Document', 'bar')
        self.content.removeStorage('bar')
        self.assertEqual(s1, self.content.getStorageForType('Document').aq_base)

    def testRemoveTypeResetsPortalTypesToNoneDefault(self):
        """getStorageForType must return None if set storage is removed and no default"""
        s = DummyStorage('bar')
        self.content.registerStorage(s)
        self.content.setDefaultStorage(None)
        self.content.setStorageForType('Document', 'bar')
        self.content.removeStorage('bar')
        self.assertEqual(None, self.content.getStorageForType('Document'))

        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestStorageManager))
        return suite

