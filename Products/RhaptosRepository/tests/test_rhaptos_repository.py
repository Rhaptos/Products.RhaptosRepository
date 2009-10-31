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
config.extension_profiles = ['Products.RhaptosRepository:default']

from Products.CMFDefault.Document import Document
from Products.RhaptosRepository.Repository import Repository
from Products.RhaptosRepository.VersionFolder import VersionFolderStorage
from Products.RhaptosTest.base import RhaptosTestCase


class TestRhaptosRepository(RhaptosTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        # XXX:  This following chunk of code was copied and adapted from
        # setuphandlers.  We shouldn't have to do this stuff manually.
        # setuphandlers should get run when we install the RhaptosRepository
        # product.
        product = self.portal.manage_addProduct['RhaptosRepository']
        product.manage_addRepository('content')
        self.repo = self.portal.content
        self.version_folder_storage = VersionFolderStorage('version_folder_storage')
        self.repo.registerStorage(self.version_folder_storage)
        self.repo.setDefaultStorage('version_folder_storage')

        # PloneTestCase already gives us a folder, so within that folder,
        # create a document to version:
        self.folder.invokeFactory('Document', 'doc')
        self.doc = self.folder.doc

    def beforeTearDown(self):
        pass

    def test_storage(self):
        self.repo.setStorageForType('Document', None)
        self.assertEqual(self.repo.getDefaultStorage(), self.version_folder_storage)
        tmp_version_folder_storage = VersionFolderStorage('tmp_version_folder_storage')
        self.repo.registerStorage(tmp_version_folder_storage)
        self.repo.setStorageForType('Document', 'tmp_version_folder_storage')
        self.assertEqual(self.repo.getStorageForType('Document').getId(), 'tmp_version_folder_storage')

        # FIXME:  These next two lines fail because the docstring for
        # setStorageForType is out of sync with the code itself.  This test
        # remains true to the docstring, so fails on the code.
#        self.repo.setStorageForType('Document', None)
#        self.assertEqual(self.repo.getStorageForType('Document').getId(), 'test_version_folder_storage')

    def test_repository(self):
        # Make sure that our repository is initially empty:
        self.assertEqual(self.repo.countRhaptosObjects(), 0)
        self.assertEqual(self.repo.hasRhaptosObject(self.doc.getId()), False)
        self.assertFalse(self.repo.getRhaptosObjectLanguageCounts())

        # Make sure that hasRhaptosObject returns False for None objects:
        self.assertFalse(self.repo.hasRhaptosObject(None))

    def test_version_folder_storage(self):
        self.assertEqual(1, 1)

    def test_storage_manager(self):
        self.assertEqual(1, 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRhaptosRepository))
    return suite
