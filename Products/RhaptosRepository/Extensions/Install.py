from Products.Archetypes.Extensions.utils import install_subskin
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.utils import getToolByName
from Products.RhaptosRepository import Repository, product_globals as GLOBALS
from Products.RhaptosRepository.VersionFolder import VersionFolderStorage
from cStringIO import StringIO
import string

import zLOG
def log(msg, out=None, severity=zLOG.INFO):
    zLOG.LOG("RhaptosRepository: Install", severity, msg)
    if out: print >> out, msg

def install(self):
    """Register RhaptosRepository with the necessary tools"""
    out = StringIO()

    urltool = getToolByName(self, 'portal_url')
    portal = urltool.getPortalObject();

    # Setup the types tool
    typestool = getToolByName(self, 'portal_types')
    for t in Repository.factory_type_information:
        if t['id'] not in typestool.objectIds():
            cfm = apply(FactoryTypeInformation, (), t)
            typestool._setObject(t['id'], cfm)
            log('Registered with the types tool', out)
        else:
            log('Object "%s" already existed in the types tool' % (t['id']), out)

    # Setup the skins
    log("Installing subsksins", out)
    install_subskin(self, out, GLOBALS)

    # Add the repository
    REPOS_NAME = 'content'
    content = getattr(portal, REPOS_NAME, None)
    if not content:
        log("Adding Repository '%s'" % REPOS_NAME, out)
        portal.manage_addProduct['RhaptosRepository'].manage_addRepository('content')
        content = portal[REPOS_NAME]
        
        # Register VersionFolder storage
        content.registerStorage(VersionFolderStorage('version_folder_storage'))
        content.setDefaultStorage('version_folder_storage')
    else:
        log("Upgrading existing Repository '%s'" % REPOS_NAME, out)
        # we only upgrade metadata at the moment, but we should do the same for
        # indexes (and other things) when we have to touch those
        changemeta = content._set_metadata()
        if changemeta:
            log("...added metadata fields: %s; updating" % list(changemeta), out)
            log("Recatalog your content catalog from the live URL", out)

            # ideally we would do this, but it gets the 'url' field wrong, and also getIcon
            # getIcon we could perhaps patch to call it relative, but url not so much.
            #cat = content.catalog
            #objs = cat.searchResults()
            #for brain in objs:
                #obj = brain.getObject()
                #cat.catalog_object(obj, update_metadata=1, idxs=['Title']) 
                                                           ## no idxs==all, so pick one cheap one

    # Set the portlet
    log("Customizing repository portlets", out)
    right_slots = [
                  'here/portlet_login/macros/portlet',
                  'here/portlet_loggedin/macros/portlet',
                  'here/portlet_repository_stats/macros/portlet',
                  'here/portlet_recentview/macros/portlet'
                  ]
    ids = content.propertyIds()
    if ('right_slots' not in ids):
        log("...new property created", out)
        content.manage_addProperty('right_slots', [], 'lines')
    else:
        log("...previous contents: " + str(content.right_slots), out)
    log("...setting right_slots to: " + str(right_slots), out)
    content._updateProperty('right_slots', right_slots)

    log("done.", out)
    return out.getvalue()

