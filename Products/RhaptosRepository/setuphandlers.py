from Products.Archetypes.Extensions.utils import install_subskin
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.utils import getToolByName
from Products.RhaptosRepository import Repository, product_globals as GLOBALS
from Products.RhaptosRepository.VersionFolder import VersionFolderStorage
from cStringIO import StringIO
import string


def setupRepository(context):
    """Register RhaptosRepository with the necessary tools"""
    logger = context.getLogger('rhaptos-repository')
    if context.readDataFile('rhaptosrepository.txt') is None:
        logger.info('Nothing to import.')
        return

    portal = context.getSite()

    REPOS_NAME = 'content'
    content = getattr(portal, REPOS_NAME, None)
    if not content:
        logger.info("Adding Repository '%s'" % REPOS_NAME)
        portal.manage_addProduct['RhaptosRepository'].manage_addRepository(
                REPOS_NAME)
        content = portal[REPOS_NAME]
        
        # Register VersionFolder storage
        content.registerStorage(VersionFolderStorage('version_folder_storage'))
        content.setDefaultStorage('version_folder_storage')
    else:
        logger.info("Upgrading existing Repository '%s'" % REPOS_NAME)
        # we only upgrade metadata at the moment, but we should do the same for
        # indexes (and other things) when we have to touch those
        changemeta = content._set_metadata()
        if changemeta:
            logger.info("...added metadata fields: %s; updating" % list(changemeta))
            logger.info("Recatalog your content catalog from the live URL")

            # ideally we would do this, but it gets the 'url' field wrong, and also getIcon
            # getIcon we could perhaps patch to call it relative, but url not so much.
            #cat = content.catalog
            #objs = cat.searchResults()
            #for brain in objs:
                #obj = brain.getObject()
                #cat.catalog_object(obj, update_metadata=1, idxs=['Title']) 
                                                           ## no idxs==all, so pick one cheap one

    # Set the portlet
    logger.info("Customizing repository portlets")
    right_slots = [
                  'here/portlet_login/macros/portlet',
                  'here/portlet_loggedin/macros/portlet',
                  'here/portlet_repository_stats/macros/portlet',
                  'here/portlet_recentview/macros/portlet'
                  ]
    ids = content.propertyIds()
    if ('right_slots' not in ids):
        logger.info("...new property created")
        content.manage_addProperty('right_slots', [], 'lines')
    else:
        logger.info("...previous contents: " + str(content.right_slots))
    logger.info("...setting right_slots to: " + str(right_slots))
    content._updateProperty('right_slots', right_slots)

    logger.info("done.")

def addRoles(context):
    if context.readDataFile('rhaptosrepository.txt') is None:
        return
    portal = context.getSite()
    portal.acl_users.addRole('Publisher')
