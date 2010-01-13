# BaseTestCase

from Products.RhaptosSite.tests.RhaptosTestCase import RhaptosTestCase
from Testing import ZopeTestCase
from Products.RhaptosRepository.Extensions import Install
import transaction

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('MailHost')
ZopeTestCase.installProduct('RhaptosRepository')
ZopeTestCase.installProduct('ZCTextIndex')


from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
import time

portal_name  = 'portal'
portal_owner = 'portal_owner'
default_user = ZopeTestCase._user_name


class BaseTestCase(RhaptosTestCase):

    def afterSetUp(self):
        #Install.install(self.portal)
        self.content = self.portal.content
        self.folder.invokeFactory('Document', 'doc1')
        self.doc1 = self.folder.doc1

def setupCMFSite(app=None, id=portal_name, quiet=0):
    '''Creates a CMF site.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet: ZopeTestCase._print('Adding CMF Site ... ')
        # Add user and log in
        uf = app.acl_users
        uf._doAddUser(portal_owner, '', ['Manager'], [])
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)
        # Add CMF Site
        app.manage_addProduct['CMFDefault'].manage_addCMFSite(id, '', create_userfolder=1)
        # Log out
        noSecurityManager()
        transaction.commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


