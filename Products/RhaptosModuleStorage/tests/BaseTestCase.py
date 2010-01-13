# BaseTestCase

from Testing import ZopeTestCase
import transaction

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFDiffTool')
ZopeTestCase.installProduct('MailHost')
ZopeTestCase.installProduct('PageTemplates', quiet=1)
ZopeTestCase.installProduct('PythonScripts', quiet=1)
ZopeTestCase.installProduct('ExternalMethod', quiet=1)

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
import time

portal_name  = 'portal'
portal_owner = 'portal_owner'
default_user = ZopeTestCase._user_name


class BaseTestCase(ZopeTestCase.PortalTestCase):

    def getPortal(self):
        '''Returns the portal object.'''
        return self.app[portal_name]

    def createMemberarea(self, member_id):
        '''Creates a minimal, no-nonsense memberarea.'''
        membership = self.portal.portal_membership
        catalog = self.portal.portal_catalog
        # Owner
        uf = self.portal.acl_users
        user = uf.getUserById(member_id)
        if user is None:
            raise ValueError, 'Member %s does not exist' % member_id
        user = user.__of__(uf)
        # Home folder
        members = membership.getMembersFolder()
        members.manage_addPloneFolder(member_id)
        folder = membership.getHomeFolder(member_id)
        folder.changeOwnership(user)
        folder.__ac_local_roles__ = None
        folder.manage_setLocalRoles(member_id, ['Owner'])
        # Personal folder
        folder.manage_addPloneFolder(membership.personal_id)
        personal = membership.getPersonalFolder(member_id)
        personal.changeOwnership(user)
        personal.__ac_local_roles__ = None
        personal.manage_setLocalRoles(member_id, ['Owner'])
        catalog.unindexObject(personal)

    def loginPortalOwner(self):
        '''Use if you need to manipulate the portal itself.'''
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)


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
        app[id].manage_addProduct['CMFDiffTool'].manage_addTool('CMF Diff Tool')
        # Log out
        noSecurityManager()
        transaction.commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


# Create a Plone site in the test (demo-) storage
app = ZopeTestCase.app()
setupCMFSite(app)
ZopeTestCase.close(app)

