from Products.ManagableIndex.FieldIndex import FieldIndex
from Products.ManagableIndex.KeywordIndex import KeywordIndex
from Products.ManagableIndex.ValueProvider import ExpressionEvaluator
from Products.CMFCore.Expression import Expression
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.RhaptosRepository.LatestReference import addLatestReference
from Products.ZCatalog.Catalog import CatalogError
from Products.RhaptosRepository.interfaces.IVersionStorage import IVersionStorage
from BTrees import OOBTree

from StringIO import StringIO

class Empty:
    def __init__(self, **kw):
        self.__dict__.update(kw)

def referenceUpgrade(self):
    """Upgrade to the new LatestReference object"""
    catalog = self.content.catalog
    for c in self.content.objectValues():
        v = c.latest.version
        title = c.latest.Title()
        c.manage_delObjects(['latest'])
        addLatestReference(c, 'latest', title, str(v))
        catalog.catalog_object(c.latest)

def fixTitleCatalog(self):
    """Change the title attributes to Title in catalog"""
    catalog = self.content.catalog
    catalog.delIndex('title')

    extra = Empty(doc_attr = 'Title', index_type = 'Okapi BM25 Rank', lexicon_id = 'lexicon')
    catalog.addIndex('Title', 'ZCTextIndex', extra)

    catalog._catalog.indexes['sortTitle'].sortTitle._updateProperty('Name','Title')
    catalog.delColumn('title')

    catalog.refreshCatalog()


def convertToBTree(self):
    """Convert the repository to a BTreeFolder"""

    orig_content = self.content
    q_tool = getToolByName(self, 'portal_quickinstaller')
    q_tool.uninstallProducts(['RisaRepository'])
    self.manage_delObjects(['content'])
    q_tool.installProduct('RisaRepository')
    new_content = self.content

    for o in orig_content._objects:
        new_content._setOb(o['id'], getattr(orig_content, o['id']))

    # Migrate various attributes
    new_content.title = orig_content.title
    new_content._nextCollectionId = orig_content._nextCollectionId
    new_content.right_slots = orig_content.right_slots
    new_content.workflow_history = orig_content.workflow_history 

    # FIXME: migrate security settings
    new_content.manage_permission('Add portal content', ('Member',), acquire=1)
    
    # Don't list children in plone navigation portlet
    p_tool = getToolByName(self, 'portal_properties')
    try:
        l = list(p_tool.navtree_properties.parentMetaTypesNotToQuery)
    except:
        pass
    else:
        l.append('RISA Repository')
        p_tool.navtree_properties._updateProperty('parentMetaTypesNotToQuery', tuple(l))

    

def hitCountUpgrade(self):
    """Upgrade the installed tool"""
    out = StringIO()
    out.write("Upgrading Risa Repository\n")

    content = getToolByName(self, 'content')

    fi=FieldIndex('sortTitle')
    content.catalog._catalog.addIndex('sortTitle', fi)
    fi._updateProperty('PrenormalizeTerm', 'python: value.lower()')
    fi._updateProperty('TermType', 'string')
    fi.sortTitle._updateProperty('Name', 'title')
    fi.sortTitle._updateProperty('Normalizer', 'python: here.stripArticles(value)')

    extra=Empty()
    extra.indexed_attrs='keywords'
    content.catalog.addIndex('keywordscase', 'KeywordIndex', extra)

    content.catalog.delColumn('icon')
    content.catalog.addColumn('getIcon')
    content.catalog.addColumn('url')
    content.catalog.addColumn('authors')
    content.catalog.addColumn('instructor')

    out.write("Upgraded catalog\n")

    types_tool = getToolByName(self, 'portal_types')
    # Plone1 version
    #types_tool.Repository._actions = ({'id':'view', 'name':'Browse', 'action':'browse_content', 'permissions':('View',),'visible':0},)

    types_tool.Repository._actions = [ActionInformation('view', title='Browse', action='browse_content', permissions=(permissions.View),visible=0)]

    out.write("Upgraded actions\n")

    right_slots = ['here/portlet_newest_content/macros/portlet', 'here/portlet_hits/macros/portlet']
    content._setProperty('right_slots', right_slots, type='lines')

    out.write("Upgraded portlets\n")

    content.catalog.refreshCatalog()
    out.write("Refreshed catalog\n")

    return out.getvalue()

def storageDispatchUpgrade(self):
    from Products.RhaptosRepository.VersionFolder import VersionFolderStorage

    repos = getToolByName(self, 'content')

    repos.catalog.addIndex('portal_type', 'FieldIndex')
    repos.catalog.refreshCatalog()

    repos._default_storage = None
    repos._storage_map = {}
    repos.registerStorage(VersionFolderStorage('version_folder_storage'))
    repos.setDefaultStorage('version_folder_storage')
    repos.version_folder_storage._next_id = repos._nextCollectionId

    for c in repos.objectValues('Version Folder'):
        c.storage = 'version_folder_storage'

def addGetHistoryCount(self):
    """add a getHistoryCount column to the catalog"""
    self.content.catalog.addColumn('getHistoryCount')
    self.content.catalog.addIndex('maintainers', 'KeywordIndex')
    self.content.catalog.addColumn('maintainers')
    self.content.catalog.addColumn('submitter')
    self.content.catalog.refreshCatalog()

def catalogModuleStubs(self):
    """Catalog the module metadata from the module stub objects"""
    try:
      self.content.catalog.addIndex('language', 'KeywordIndex')
      self.content.catalog.addColumn('language')
    except CatalogError:
      pass

    for o in self.content.objectValues('Module Version Folder'):
        obj = o.latest
        self.content.catalog.catalog_object(obj)

    self.content.catalog.refreshCatalog()

def installRepositoryStatsPortlet(self):

    content = getToolByName(self, 'content')

    ids = content.propertyIds()
    if ('right_slots' not in ids):
        content.manage_addProperty('right_slots', [], 'lines')
    right_slots = ['here/portlet_login/macros/portlet',
                   'here/portlet_loggedin/macros/portlet',
                   'here/portlet_pending/macros/portlet',
                   'here/portlet_repository_stats/macros/portlet']
    content._updateProperty('right_slots', right_slots)
    
    if ('left_slots' not in ids):
        content.manage_addProperty('left_slots', [], 'lines')
    left_slots = []
    content._updateProperty('left_slots', left_slots)

    out = StringIO()
    out.write("Upgraded portlets\n")

def addCatalogStuff(self):
    """add a baselanguage column to catalog"""

    ki=KeywordIndex('baselanguage')
    self.catalog._catalog.addIndex('baselanguage',ki)
    ki._updateProperty('PrenormalizeTerm', "python: same_type(value,'') and value.decode('utf-8') or value")
    ki.baselanguage._updateProperty('Name','language')
    ki.baselanguage._updateProperty('Normalizer', "python: [value[:(value.find('-') > 0 ) and value.find('-') or len(value)]]")

    self.catalog.reindexIndex('baselanguage', REQUEST=None)

    self.catalog.addIndex('subject', 'KeywordIndex')
    self.catalog.reindexIndex('subject', REQUEST=None)

    self.catalog.addColumn('collectionType')
    self.catalog.addColumn('sortTitle')
    self.catalog.addColumn('fields',{})
    self.catalog.addColumn('matched',{})

def addTranslators(self):
    ki=KeywordIndex('translators')
    self.catalog._catalog.addIndex('translators',ki)
    ki._delObject('translators')
    ee=ExpressionEvaluator()
    ee.id='translators'
    ki._setObject(ee.id,ee)
    ki.translators._updateProperty('Expression',"python: lambda o: o.roles['translators']")
    self.catalog.reindexIndex('translators', REQUEST=None)

def addEditors(self):
    ki=KeywordIndex('editors')
    self.catalog._catalog.addIndex('editors',ki)
    ki._delObject('editors')
    ee=ExpressionEvaluator()
    ee.id='editors'
    ki._setObject(ee.id,ee)
    ki.editors._updateProperty('Expression',"python: lambda o: o.roles['editors']")
    self.catalog.reindexIndex('editors', REQUEST=None)

def fixBaseLanguage(self):
    ki=self.catalog.Indexes['baselanguage']
    ki._updateProperty('PrenormalizeTerm', "python: same_type(value,'') and value.decode('utf-8') or value")

def addSearchPortlet(self):
    """add a new portlet before the repository stats portlet for recent searches"""
    rs = list(self.right_slots)
    if 'here/portlet_search_history/macros/portlet' not in rs:
        if 'here/portlet_repository_stats/macros/portlet' in rs:
            rs.insert(rs.index('here/portlet_repository_stats/macros/portlet'),'here/portlet_search_history/macros/portlet')
        else:
            rs.append('here/portlet_search_history/macros/portlet')
        self.right_slots = tuple(rs)

def addParentAuthors(self):
    self.catalog.addIndex('parentAuthors', 'KeywordIndex')

def addContainedModuleAuthors(self):
    self.catalog.addIndex('containedModuleAuthors', 'KeywordIndex')

def addKeywordstext(self):

    extra = Empty(doc_attr = 'keywords', index_type = 'Okapi BM25 Rank', lexicon_id = 'lexicon')
    self.catalog.addIndex('keywordstext', 'ZCTextIndex', extra)

def addSearchCache(self):
    self.searches = OOBTree.OOBTree()

def fixStorageLists(self):
    self._all_storages = [o.getId() for o in self.objectValues() if IVersionStorage.providedBy(o)]


from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer
from Products.ZCTextIndex.Lexicon import StopWordAndSingleCharRemover
from Products.ZCTextIndex.ZCTextIndex import PLexicon
def swapUnicodeAwareLexicon(self):
    cat = self.catalog
    newlex = PLexicon('lexicon', '' ,Splitter(), CaseNormalizer(), StopWordAndSingleCharRemover())
    cat._delObject('lexicon')
    cat._setObject('lexicon', newlex)


