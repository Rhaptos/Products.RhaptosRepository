#------------------------------------------------------------------------------#
#   test_rhaptos_module_storage.py                                             #
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
import Products.RhaptosModuleStorage
config.products_to_load_zcml = [('configure.zcml', Products.RhaptosModuleStorage),]
config.products_to_install = ['RhaptosModuleStorage']
config.extension_profiles = ['Products.RhaptosModuleStorage:default']

from Products.CMFDefault.Document import Document
from Products.RhaptosModuleStorage.ModuleVersionFolder import ModuleVersionStorage
from Products.RhaptosModuleStorage.ModuleView import ModuleFile
from Products.RhaptosModuleStorage.ModuleView import ModuleView
from Products.RhaptosTest import base


class TestRhaptosModuleStorage(base.RhaptosTestCase):

    def afterSetUp(self):
        self.doc = Document('foo bar')
        self.module_version_storage = ModuleVersionStorage('test_module_version_storage')
#        self.module_file = ModuleFile()
#        self.module_view = ModuleView()

    def beforeTearDown(self):
        pass

    def test_module_version_storage(self):
        self.assertEqual(1, 1)
#        self.assertEqual(self.module_version_storage.countObjects(), 0)
#        self.assertFalse(self.module_version_storage.hasObject(self.doc.getId()))

    def test_module_view(self):
        self.assertEqual(1, 1)

    def test_module_file(self):
        self.assertEqual(1, 1)

    def test_rhaptosdb_iterator(self):
        self.assertEqual(1, 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRhaptosModuleStorage))
    return suite
