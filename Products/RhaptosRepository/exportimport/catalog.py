from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from Products.CMFCore.utils import getToolByName


def importCatalogTool(context):
    """Import catalog tool.
    """
    site = context.getSite()
    tool = getToolByName(site.content, 'catalog', None)
    if tool is None:
        logger = context.getLogger('Rhaptos Repository Catalog')
        logger.debug('Nothing to import.')
        return

    importObjects(tool, '', context)

def exportCatalogTool(context):
    """Export catalog tool.
    """
    site = context.getSite()
    tool = getToolByName(site.content, 'catalog', None)
    if tool is None:
        logger = context.getLogger('Rhaptos Repository Catalog')
        logger.debug('Nothing to export.')
        return

    exportObjects(tool, '', context)
