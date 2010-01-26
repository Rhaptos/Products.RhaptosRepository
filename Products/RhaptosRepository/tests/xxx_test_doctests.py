import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

#ztc.installProduct('ContentLicensing')

# Set up a Plone site, and apply our custom extension profile
PROFILES = ('Products.RhaptosCollection:default',)
ptc.setupPloneSite(extension_profiles=PROFILES)

import Products.RhaptosCollection

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', Products.RhaptosCollection)
            #zcml.load_config('overrides.zcml', Products.RhaptosCollection)
            ztc.installPackage('Products.RhaptosCollection')
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        doctestunit.DocFileSuite(
            'static.txt', package='Products.RhaptosCollection.tests',
            setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='Products.RhaptosCollection.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # FIXME
        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'profile.txt', package='Products.RhaptosCollection.tests',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='Products.RhaptosCollection',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
