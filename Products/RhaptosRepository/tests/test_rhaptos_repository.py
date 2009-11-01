#------------------------------------------------------------------------------#
#   test_rhaptos_repository.py                                                 #
#                                                                              #
#       Authors:                                                               #
#       Rajiv Bakulesh Shah <raj@enfoldsystems.com>                            #
#                                                                              #
#           Copyright (c) 2009, Enfold Systems, Inc.                           #
#           All rights reserved.                                               #
#                                                                              #
#               This software is licensed under the Terms and Conditions       #
#               contained within the "LICENSE.txt" file that accompanied       #
#               this software.  Any inquiries concerning the scope or          #
#               enforceability of the license should be addressed to:          #
#                                                                              #
#                   Enfold Systems, Inc.                                       #
#                   4617 Montrose Blvd., Suite C215                            #
#                   Houston, Texas 77006 USA                                   #
#                   p. +1 713.942.2377 | f. +1 832.201.8856                    #
#                   www.enfoldsystems.com                                      #
#                   info@enfoldsystems.com                                     #
#------------------------------------------------------------------------------#
"""Unit tests.
$Id: $
"""


from Products.RhaptosTest import config
import Products.RhaptosRepository
config.products_to_load_zcml = [('configure.zcml', Products.RhaptosRepository),]
config.products_to_install = [
    'Archetypes', 'CMFCore', 'CMFDefault', 'MailHost', 'MimetypesRegistry',
    'PortalTransforms', 'RhaptosCollection', 'RhaptosHitCountTool',
    'RhaptosModuleEditor', 'RhaptosRepository', 'ZAnnot', 'ZCTextIndex',
]
config.extension_profiles = [
    'Products.RhaptosCollection:default', 'Products.RhaptosRepository:default',
]

from OFS.SimpleItem  import SimpleItem
from Products.RhaptosRepository.VersionFolder import VersionFolderStorage
from Products.RhaptosRepository.interfaces.IRepository import IRepository
from Products.RhaptosRepository.interfaces.IVersionStorage import IStorageManager
from Products.RhaptosRepository.interfaces.IVersionStorage import IVersionStorage
from Products.RhaptosTest.base import RhaptosTestCase


class DummyStorage(SimpleItem):
    __implements__ = (IVersionStorage)

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id


class TestRhaptosRepository(RhaptosTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        # FIXME:  This following chunk of code was copied and adapted from
        # setuphandlers.  We shouldn't have to do this stuff manually.
        # setuphandlers should get run when we install the RhaptosRepository
        # product.
        product = self.portal.manage_addProduct['RhaptosRepository']
        product.manage_addRepository('content')
        self.repo = self.portal.content
#        self.version_folder_storage = VersionFolderStorage('version_folder_storage')
#        self.repo.registerStorage(self.version_folder_storage)
#        self.repo.setDefaultStorage('version_folder_storage')

        # PloneTestCase already gives us a folder, so within that folder,
        # create a document and a collection to version.
        self.folder.invokeFactory('Document', 'doc')
        self.doc = self.folder.doc

        # FIXME:  Somehow, get Collection to be an installable type.
#        self.folder.invokeFactory('Collection', 'col')
#        self.col = self.folder.col

    def beforeTearDown(self):
        pass

    def test_storage_interface(self):
        # Make sure that the repository implements the expected interface.
        self.failUnless(IStorageManager.isImplementedBy(self.repo))

    def test_storage_register_incorrect_interface(self):
        # Make sure that registerStorage raises a TypeError if the storage
        # doesn't implement IVersionStorage.
        self.assertRaises(TypeError, self.repo.registerStorage, 'foo', None)

    def test_storage_register(self):
        # Make sure that registerStorage actually registers a storage.
        storage = DummyStorage('foo')
        self.repo.registerStorage(storage)
        self.failUnless('foo' in self.repo.listStorages())

    def test_storage_register_dupe_ids(self):
        # Make sure that registerStorage raises a ValueError when registering
        # two storages with the same ID.
        storage1 = DummyStorage('foo')
        storage2 = DummyStorage('foo')
        self.repo.registerStorage(storage1)
        self.assertRaises(ValueError, self.repo.registerStorage, storage2)

    def test_storage_get_nonexistent_id(self):
        # Make sure that getStorage raises a KeyError when trying to get a
        # non-existent storage.
        self.assertRaises(KeyError, self.repo.getStorage, 'foo')

    def test_storage_acquisition_wrappers(self):
        # Make sure that the acquisition wrappers are correctly being set on
        # storages.
        storage = DummyStorage('foo')
        self.repo.registerStorage(storage)
        self.assertEqual(self.repo, self.repo.getStorage('foo').aq_parent)

    def test_storage_default(self):
        # We haven't set a default storage, so make sure that getDefaultStorage
        # returns None.
        self.assertEqual(self.repo.getDefaultStorage(), None)

        # Make sure that we can set the default storage...
        storage = DummyStorage('foo')
        self.repo.registerStorage(storage)
        self.repo.setDefaultStorage('foo')
        self.assertEqual(self.repo.getDefaultStorage().aq_base, storage)

        # ...and reset the default storage to None.
        self.repo.setDefaultStorage(None)
        self.assertEqual(self.repo.getDefaultStorage(), None)

        # Make sure that removing the default storage resets the default
        # storage to None.
        self.repo.setDefaultStorage('foo')
        self.assertEqual(self.repo.getDefaultStorage().aq_base, storage)
        self.repo.removeStorage('foo')
        self.assertEqual(self.repo.getDefaultStorage(), None)

    def test_storage_set_for_type(self):
        # Make sure that setStorageForType raises a KeyError when trying to set
        # an unregistered storage for a type.
        self.assertRaises(KeyError, self.repo.setStorageForType, 'Document', 'foo')

        # When a storage for a type isn't set, and the default storage isn't
        # set, and we get the storage for the type, make sure we get None.
        self.assertEqual(self.repo.getStorageForType('Document'), None)

        # When a storage for a type isn't set, and the default storage is set,
        # and we get the storage for the type, make sure we get the default
        # storage.
        storage1 = DummyStorage('foo')
        self.repo.registerStorage(storage1)
        self.repo.setDefaultStorage('foo')
        self.assertEqual(self.repo.getStorageForType('Document').aq_base, storage1)

        # Make sure that we can set and get a storage for a type.
        storage2 = DummyStorage('bar')
        self.repo.registerStorage(storage2)
        self.repo.setStorageForType('Document', 'bar')
        self.assertEqual(self.repo.getStorageForType('Document').aq_base, storage2)

        # When we remove the storage for the type, then get the storage for the
        # type, make sure we get the default storage.
        self.repo.removeStorage('bar')
        self.assertEqual(self.repo.getStorageForType('Document').aq_base, storage1)

        # When a storage for a type is set then removed, and when the default
        # storage isn't set, and we get the storage for the type, make sure we
        # get None.
        self.repo.setDefaultStorage(None)
        self.repo.registerStorage(storage2)
        self.repo.setStorageForType('Document', 'bar')
        self.repo.removeStorage('bar')
        self.assertEqual(self.repo.getStorageForType('Document'), None)

    def test_repository_interface(self):
        # Make sure that the repository implements the expected interface.
        self.failUnless(IRepository.isImplementedBy(self.repo))

    def test_repository_empty(self):
        # Make sure that our repository is initially empty.
        self.assertEqual(self.repo.countRhaptosObjects(), 0)
        self.assertEqual(self.repo.hasRhaptosObject(self.doc.getId()), False)
        self.assertFalse(self.repo.getRhaptosObjectLanguageCounts())

    def test_repository_has_object(self):
        # Make sure that hasRhaptosObject returns False for None objects.
        self.assertFalse(self.repo.hasRhaptosObject(None))

        # Make sure that hasRhaptosObject raises a KeyError for a non-existent
        # ID.
        self.assertRaises(KeyError, self.repo.getRhaptosObject, 'foo')

    def test_repository_get_history(self):
        # Make sure that getHistory returns None for None and unpublished
        # objects.
        self.assertEqual(None, self.repo.getHistory(None))
        self.assertEqual(None, self.repo.getHistory('foo'))

    def test_version_folder_storage_interface(self):
        # Make sure that the version folder storage implements the expected
        # interface.
        version_folder_storage = VersionFolderStorage('version_folder_storage')
        self.repo.registerStorage(version_folder_storage)
        self.version_folder_storage = self.repo.version_folder_storage
        self.failUnless(IVersionStorage.isImplementedBy(self.version_folder_storage))

    def test_version_folder_storage_generate_id(self):
        # Make sure that the version folder storage generates unique IDs.
        version_folder_storage = VersionFolderStorage('version_folder_storage')
        self.repo.registerStorage(version_folder_storage)
        self.version_folder_storage = self.repo.version_folder_storage
        for count in range(1, 9999):
            id = 'col1' + str(count).rjust(4, '0')
            self.assertEqual(self.version_folder_storage.generateId(), id)

    def test_version_folder_storage_get_version_info(self):
        # Make sure that getVersionInfo returns None for non-versioned objects.
        version_folder_storage = VersionFolderStorage('version_folder_storage')
        self.repo.registerStorage(version_folder_storage)
        self.repo.setDefaultStorage('version_folder_storage')
        self.version_folder_storage = self.repo.version_folder_storage
        self.assertEqual(self.version_folder_storage.getVersionInfo(self.doc), None)

        # Publish a document to be versioned.  FIXME: This doesn't work because
        # 'Collection' isn't an installable type.
#        self.repo.publishObject(self.col, 'initial commit')

    def test_version_folder_storage(self):
        version_folder_storage = VersionFolderStorage('version_folder_storage')
        self.repo.registerStorage(version_folder_storage)
        self.version_folder_storage = self.repo.version_folder_storage

    def test_storage_manager(self):
        self.assertEqual(1, 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRhaptosRepository))
    return suite
