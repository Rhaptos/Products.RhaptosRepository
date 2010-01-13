# CMFTestCase

from Testing import ZopeTestCase
import transaction

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('MailHost')
ZopeTestCase.installProduct('RhaptosModuleStorage')
ZopeTestCase.installProduct('ZPsycopgDA')


from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
import time

portal_name  = 'portal'
portal_owner = 'portal_owner'
#default_user = ZopeTestCase._user_name


class CMFTestCase(ZopeTestCase.PortalTestCase):
    pass

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


# Create a Plone site in the test (demo-) storage
#app = ZopeTestCase.app()
#setupCMFSite(app)
#ZopeTestCase.close(app)

