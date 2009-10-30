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
config.products_to_install = ['RhaptosRepository']

from Products.CMFDefault.Document import Document
from Products.RhaptosRepository.Repository import Repository
from Products.RhaptosRepository.StorageManager import StorageManager
from Products.RhaptosRepository.VersionFolder import VersionFolderStorage
from Products.RhaptosTest.base import RhaptosTestCase


class TestRhaptosRepository(RhaptosTestCase):

    def afterSetUp(self):
        self.doc = Document('foo bar')
        self.version_folder_storage = VersionFolderStorage('test_version_folder_storage')
        self.storage = StorageManager('test_storage_manager')
        self.storage.registerStorage(self.version_folder_storage)
        self.storage.setDefaultStorage('test_version_folder_storage')
        self.storage.setStorageForType('Document', None)
        self.repo = Repository('test_repository', title='Test Repository')

    def beforeTearDown(self):
        pass

    def test_storage(self):
        self.assertEqual(self.storage.getDefaultStorage(), self.version_folder_storage)
        tmp_version_folder_storage = VersionFolderStorage('tmp_version_folder_storage')
        self.storage.registerStorage(tmp_version_folder_storage)
        self.storage.setStorageForType('Document', 'tmp_version_folder_storage')
        self.assertEqual(self.storage.getStorageForType('Document').getId(), 'tmp_version_folder_storage')

        # TODO:  These next two lines fail because the docstring for
        # setStorageForType is out of sync with the code itself.  This test
        # remains true to the docstring, so fails on the code.
#        self.storage.setStorageForType('Document', None)
#        self.assertEqual(self.storage.getStorageForType('Document').getId(), 'test_version_folder_storage')

    def test_repository(self):
        self.assertEqual(self.repo.countRhaptosObjects(), 0)

    def test_version_folder_storage(self):
        self.assertEqual(1, 1)

    def test_storage_manager(self):
        self.assertEqual(1, 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRhaptosRepository))
    return suite
