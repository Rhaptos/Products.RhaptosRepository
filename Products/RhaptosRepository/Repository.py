"""
Zope Object to Access RhaptosRepository Product

Author: Brent Hendricks and Ross Reedstrom
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import AccessControl
import zLOG
from DateTime import DateTime
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import UniqueObject, getToolByName, _getViewFor
from Products.CMFCore import permissions
from Products.CMFCore.DynamicType import DynamicType
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCTextIndex.ZCTextIndex import PLexicon, ZCTextIndex
from Products.ManagableIndex.KeywordIndex import KeywordIndex
from Products.ManagableIndex.FieldIndex import FieldIndex
from Products.ManagableIndex.ValueProvider import ExpressionEvaluator
from Products.ZCTextIndex.Lexicon import StopWordAndSingleCharRemover
from Products.ZCTextIndex.ZCTextIndex import PLexicon
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer
from Products.RhaptosModuleStorage.ModuleDBTool import CommitError

from Products.RhaptosModuleStorage.Extensions.DBModule import DBModuleSearch
from StorageManager import StorageManager
from OAI import OAIHandler
from Products.RhaptosCacheTool.Cache import nocache, cache

from interfaces.IRepository import IRepository
from interfaces.IVersionStorage import IStorageManager

from psycopg2 import IntegrityError, ProgrammingError

from Products.PloneLanguageTool.availablelanguages import languageConstants

def cmpTitle(x, y):
    """A method to provide a comparison between the titles of two record objects.
    Uses the sortTitle attribute if available; Title otherwise. Does case-less comparison.
    Returns a 'cmp' compatible value, suitable for use in a 'sort'.
    """
    return int(cmp(x.sortTitle and x.sortTitle.lower() or x.Title.lower(),
                    y.sortTitle and y.sortTitle.lower() or y.Title.lower()))

manage_addRepositoryForm = PageTemplateFile('zpt/manage_addRepositoryForm',
                                            globals(),
                                            __name__='manage_addRepositoryForm')

def manage_addRepository(self, id, title='', REQUEST=None):
    ''' '''

    id=str(id)
    self=self.this()

    self._setObject(id, Repository(id, title))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

factory_type_information = (
    {'id': 'Repository',
     'content_icon': 'repository_icon.gif',
     'meta_type': 'Repository',
     'description': ('An version repository for the Rhaptos system'),
     'product': 'RhaptosRepository',
     'factory': 'manage_addRepository',
     'immediate_view': '',
     'actions': ({'id': 'view',
                  'name': 'Browse',
                  'action': 'browse_content',
                  'permissions': (permissions.View,)},
                 )
     },
    )

class Empty: pass

class Repository(UniqueObject, DynamicType, StorageManager, BTreeFolder2):
    """Rhaptos Version Repository tool"""

    __implements__ = (IRepository, StorageManager.__implements__, DynamicType.__implements__)

    meta_type = 'Repository'

    security = AccessControl.ClassSecurityInfo()
    # Fake out the types tool since we can't really use the Factory creation method
    portal_type = 'Repository'

    dsw = default_search_weights = {'fulltext':1,'abstract':1,'subject':10,'keyword':10,
                              'author':50,  'translator':40,'editor':20, 'maintainer':10, 
			      'licensor':10, 'institution':10, 'exact_title':100, 'title':10, 
			      'language':5, 'containedIn':200, 'parentAuthor':0, 
			      'containedAuthor':0, 'objectid':1000}
    
    # placeholder attributes for otherwise-not-present catalog columns/indexes
    fields = {}
    matched = {}
    weight = 0
    sortTitle = None    # FIXME: I don't think this should even be a column; nothing provides it. A fine index, though.

    default_browse_batch_size = 50

    __allow_access_to_unprotected_subobjects__ = 1

    # ZMI methods
    manage_options=( BTreeFolder2.manage_options +
                     ( { 'label' : 'Overview',
                         'action' : 'manage_overview'
                         },
                       { 'label' : 'Catalog',
                         'action' : 'manage_catalog'
                         })
                   )

    manage_overview = DTMLFile( 'explainRepository', globals() )


    def manage_catalog(self, REQUEST=None):
        """Access to the ZCatalog of versioned objects"""
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.catalog.absolute_url()+'/manage_catalogView')


    def __init__(self, id, title=''):
        """Initialize Repository object"""
        StorageManager.__init__(self, id)
        self.OAI = OAIHandler('OAI')
        self.title = title
        self._create_catalog()
        self._create_cache() #results cache needs better invalidation code - consider fake=True if you're getting conflicts on publish

    #  Copied from PortalContent 
    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self)
        if getattr(aq_base(view), 'isDocTemp', 0):
            return view(self, self.REQUEST)
        else:
            return view()

    index_html = __call__
    
    security.declarePublic("Title")
    def Title(self):
        """Fulfil new-ish interface expectations for title (so we work with breadcrumbs, etc)"""
        return self.title

    security.declarePrivate("_create_catalog")
    def _create_catalog(self):
        """Creates the ZCatalog instance for versioned objects"""
        self.catalog = ZCatalog('catalog')
        lexicon = PLexicon('lexicon', '' , Splitter(), CaseNormalizer(), StopWordAndSingleCharRemover())
        self.catalog._setObject('lexicon', lexicon)

        ZCText_extras = Empty()
        ZCText_extras.doc_attr = 'abstract'
        ZCText_extras.index_type = 'Okapi BM25 Rank'
        ZCText_extras.lexicon_id = 'lexicon'
        self.catalog.addIndex('abstract', 'ZCTextIndex', ZCText_extras)
        ZCText_extras.doc_attr = 'Title'
        self.catalog.addIndex('Title', 'ZCTextIndex', ZCText_extras)
        ZCText_extras.doc_attr = 'institution'
        self.catalog.addIndex('institution', 'ZCTextIndex', ZCText_extras)
        ZCText_extras.doc_attr = 'keywords'
        self.catalog.addIndex('keywordstext', 'ZCTextIndex', ZCText_extras)

        self.catalog.addIndex('atomicInstitution', 'FieldIndex', {'indexed_attrs':'institution'})
        self.catalog.addIndex('authors', 'KeywordIndex')
        self.catalog.addIndex('parentAuthors', 'KeywordIndex')
        self.catalog.addIndex('maintainers', 'KeywordIndex')
        self.catalog.addIndex('language', 'KeywordIndex')
        self.catalog.addIndex('modified', 'DateIndex')
        self.catalog.addIndex('revised', 'DateIndex')
        self.catalog.addIndex('objectId', 'FieldIndex')
        self.catalog.addIndex('portal_type', 'FieldIndex')
        self.catalog.addIndex('containedModuleIds', 'KeywordIndex')
        self.catalog.addIndex('subject', 'KeywordIndex')

        extra=Empty()
        extra.indexed_attrs='keywords'
        self.catalog.addIndex('keywordscase', 'KeywordIndex',extra)

        ki= KeywordIndex('keywords')
        self.catalog._catalog.addIndex('keywords', ki)
        ki._updateProperty('PrenormalizeTerm', 'python: value.lower()')
        ki._updateProperty('TermType', 'string')
        ki.keywords._updateProperty('Normalizer', 'python: [k.lower() for k in value]')

        ki=KeywordIndex('baselanguage')
        self.catalog._catalog.addIndex('baselanguage',ki)
        ki._updateProperty('PrenormalizeTerm', "python: value[:(value.find('-') > 0 ) and value.find('-') or len(value)]")
        ki.baselanguage._updateProperty('Name','language')
        ki.baselanguage._updateProperty('Normalizer', "python: [value[:(value.find('-') > 0 ) and value.find('-') or len(value)]]")

        fi=FieldIndex('sortTitle')
        self.catalog._catalog.addIndex('sortTitle',fi)
        fi._updateProperty('PrenormalizeTerm', 'python: value.lower()')
        fi._updateProperty('TermType', 'string')
        fi.sortTitle._updateProperty('Name', 'Title')
        fi.sortTitle._updateProperty('Normalizer', 'python: here.stripArticles(value)')

        fi=FieldIndex('parent')
        self.catalog._catalog.addIndex('parent',fi)
        fi.parent._updateProperty('Name', 'getParent')
        fi.parent._updateProperty('Normalizer', 'python:value.objectId')

        ki=KeywordIndex('translators')
        self.catalog._catalog.addIndex('translators',ki)
        ki._delObject('translators')
        ee=ExpressionEvaluator()
        ee.id='translators'
        ki._setObject(ee.id,ee)
        ki.translators._updateProperty('Expression',"python: lambda o: o.roles['translators']")

        ki=KeywordIndex('editors')
        self.catalog._catalog.addIndex('editors',ki)
        ki._delObject('editors')
        ee=ExpressionEvaluator()
        ee.id='editors'
        ki._setObject(ee.id,ee)
        ki.editors._updateProperty('Expression',"python: lambda o: o.roles['editors']")

        self._set_metadata()

        self._p_changed=1

    security.declarePrivate("_addColumn")
    def _addColumn(self, fieldname, *args, **kw):
        """Create a metadata field on the content catalog if it doesn't already exist.
        Call as you would 'self.catalog.addColumn'.
        Returns 'fieldname' if that name is actually added; None if it exists.
        """
        if fieldname not in self.catalog.schema():
            self.catalog.addColumn(fieldname, *args, **kw)
            return fieldname
        return None

    security.declarePrivate("_set_metadata")
    def _set_metadata(self):
        """Create the metadata fields on the content catalog.
        This is called by upgrade script and installation, so adding a role here plus reinstall
        is all that's necesary for additional metadata.
        Return tuple of added fields if we actually changed something (so the caller can update metadata.)
        Empty tuple (false) if no change.
        """
        added = set([None])
        added.add(self._addColumn('Title'))
        added.add(self._addColumn('abstract'))
        added.add(self._addColumn('authors'))
        added.add(self._addColumn('language'))
        added.add(self._addColumn('code'))
        added.add(self._addColumn('collectionType'))
        added.add(self._addColumn('created'))
        added.add(self._addColumn('fields', {}))
        added.add(self._addColumn('getHistoryCount'))
        added.add(self._addColumn('getIcon'))
        added.add(self._addColumn('institution'))
        added.add(self._addColumn('instructor'))
        added.add(self._addColumn('keywords'))
        added.add(self._addColumn('language'))
        added.add(self._addColumn('license'))
        added.add(self._addColumn('maintainers'))
        added.add(self._addColumn('matched', {}))
        added.add(self._addColumn('meta_type'))
        added.add(self._addColumn('objectId'))
        added.add(self._addColumn('portal_type'))
        added.add(self._addColumn('revised'))
        added.add(self._addColumn('roles'))
        added.add(self._addColumn('sortTitle'))
        added.add(self._addColumn('subject'))
        added.add(self._addColumn('submitter'))
        added.add(self._addColumn('url'))
        added.add(self._addColumn('version'))
        added.add(self._addColumn('weight', 0))
        added.remove(None)
        return tuple(added)

    security.declarePrivate("_create_cache")
    def _create_cache(self,fake=False):
        """Creates the cache object for results sets"""
        if fake:
            self._setObject('cache', nocache('cache'))
        else:
            self._setObject('cache', cache('cache'))

        self._p_changed=1

    def log(self, message, severity=zLOG.INFO):
        zLOG.LOG("RhaptosRepository", severity, "%s (%s)" % (message, self.REQUEST['PATH_INFO']))


    def _getStorageForObjectId(self, id):
        """Return the storage implementation associated with the given ID"""
        stub = self[id]
        return self.getStorage(stub.storage)

    def hasRhaptosObject(self, id):
        """Returns true if an object with the given ID exists in the repository"""
        return bool(self.hasObject(id))

    def countRhaptosObjects(self, portal_types=None):
        """Returns the number of objects in the repository of the given type, or all types"""

        # Build mapping of storage -> list of portal_types to query
        storages = {}
        # If no portal_types, search everything
        if not portal_types:
            for name in self.listStorages():
                storages[name] = None

        while portal_types:
            pt = portal_types.pop()
            storage = self._storage_map.get(pt, self._default_storage)
            storages.setdefault(storage, []).append(pt)

        count = 0
        for name, portal_types in storages.items():
            storage = self.getStorage(name)
            count += storage.countObjects(portal_types)

        return count
                

    def getRhaptosObjectLanguageCounts(self, portal_types=None):
        """Returns a list of tuples of language codes and count of objects using them, ordered by number of objects, descending"""

        # Build mapping of storage -> list of portal_types to query
        storages = {}
        # If no portal_types, search everything
        if not portal_types:
            for name in self.listStorages():
                storages[name] = None
        elif type(portal_types) == type(''):
            portal_types=[portal_types]

        while portal_types:
            pt = portal_types.pop()
            storage = self._storage_map.get(pt, self._default_storage)
            storages.setdefault(storage, []).append(pt)

        langdict = {}
        for name, portal_types in storages.items():
            storage = self.getStorage(name)
            for l,c in storage.getLanguageCounts(portal_types):
                langdict[l] = langdict.setdefault(l,0) + c
        langs=langdict.items()
        langs.sort(lambda x,y: cmp(y[1],x[1]))

        return langs
                

    def langLookup(self,langs=None):
        """Accesses the languageConstants monkeypatch on PloneLanguageTool, which
           generates a static dictionary of language codes, native and English language
           names, and regional variant names from PLT's own specialized dictionaries."""
        lcdict=languageConstants
        if type(langs)==type(''):
          langs=langs.split(',')
        if not langs:
          return lcdict
        else:
          returnDict={}
          for k in langs:
            returnDict[k]=lcdict[k]                    
          return returnDict 

    def getRhaptosObject(self, id, version=None, **kwargs):
        """Returns the object with the specified ID"""
        return self._getStorageForObjectId(id).getObject(id, version, **kwargs)

    security.declarePublic("getHistory")
    def getHistory(self, id):
        """Returns the history of the object with the specified ID or None if there is no such ID in the repository"""
        try:
            return self._getStorageForObjectId(id).getHistory(id)
        except KeyError:
            return None
        
    security.declarePrivate("deleteRhaptosObject")
    def deleteRhaptosObject(self, objectId, version=None, **kwargs):
        """Deletes all the objects with the specified ID"""

        if not self.hasRhaptosObject(objectId):
            raise KeyError, objectId

        return self._getStorageForObjectId(objectId).deleteObject(objectId, version)
    
        self.cache.clearSearchCache()

        #FIXME: this shouldn't be done here, but with some sort of event system
        getToolByName(self,'portal_similarity').deleteSimilarity(objectId, version)
        getToolByName(self,'portal_linkmap').deleteLinks(objectId, version)


    def _doGet(self, id, version=None, **kwargs):
        return self._getStorageForObjectId(id).getObject(id, version, **kwargs)

    def getRhaptosObjects(self, objects):
        """Returns a list of objects as defined by the list of id,version tuples"""
        return [self.hasRhaptosObject(oid) and self._getStorageForObjectId(oid).getObject(oid,ver) for oid, ver in objects]

    def publishObject(self, object, message):
        """
        Publish an object for the first time in the repository

        Creates a new folder to hold the version history of this
        object and create the first version of the object, returning
        the new unique ID for this object
        """
        storage = self.getStorageForType(object.portal_type)
        objectId = storage.applyVersionControl(object)
        storage.createVersionFolder(object)
        user = AccessControl.getSecurityManager().getUser().getUserName()
        storage.checkinResource(object, message, user)

        self.cache.clearSearchCache()
        
        #FIXME: these things shouldn't be done here, but with some sort of event system
        # hitcount update
        hitcount = getToolByName(self, 'portal_hitcount', None)
        if hitcount:
            hitcount.registerObject(objectId, DateTime())

        # storage events (mostly collection printing, at the moment)
        pubobj = storage.getObject(objectId, 'latest')
        storage.notifyObjectRevised(pubobj, None)

        # Removing this 'event' until Lens V2
        #if object.getParent():
            ### FIXME: We really want the Zope3 event system for this.
            ### Once we get that, we'll want to use something to the effect of:
            ### zope.event.notify(ObjectRevisionPublished)
            #self.lens_tool.notifyLensDerivedObject(object)
            ### End Event System Hack

        return objectId


    def publishRevision(self, object, message):
        """
        Publish a revision of an object in the repository

        object: the object to place under version control.  It must
        implement IMetadata and IVersionedObject
        message: a string log message by the user
        baseVersion: the version of the object this is based on

        returns: unique ID string for the new object
        """

        if not self.isUnderVersionControl(object):
            raise CommitError, "Cannot publish revision of object %s not under version control" % object.getId()

        # handle to original object to preserve locked status, if necessary;
        # we could look this up after publication (and would have to with proper events),
        # but that would be version inspection
        origobj = object.getPublishedObject().latest
        
        storage = self.getStorageForType(object.portal_type)
        user = AccessControl.getSecurityManager().getUser().getUserName()
        storage.checkinResource(object, message, user)
        self.cache.clearSearchCache()

        ### FIXME: We really want the Zope3 event system for these.
        ### Once we get that, we'll want to use something to the effect of:
        ### zope.event.notify(ObjectRevisionPublished)
        try: # Grab the now-published version
            pubobj = object.getPublishedObject().latest
        except AttributeError:
            pass
        
        # lens events
        self.lens_tool.notifyLensRevisedObject(pubobj)
        
        # storage events (mostly collection printing, at the moment)
        storage.notifyObjectRevised(pubobj, origobj)
        
        # notice of change to all containing collections, latest version only
        container_objs = self.catalog(containedModuleIds=pubobj.objectId)
        for col in container_objs:
            colobj = col.getObject()
            colobj.notifyContentsRevised()

        ### End Event System Hack


    def isUnderVersionControl(self, object):
        """Returns true if the object is under version control"""
        return self.getStorageForType(object.portal_type).isUnderVersionControl(object)

    def isLatestVersion(self, object):
        """Returns true if object is the most recent revision of an object"""
        return self.getStorageForType(object.portal_type).isLatestVersion(object)
        
    def getVersionInfo(self, object):
        return self.getStorageForType(object.portal_type).getVersionInfo(object)
        
    def searchRepositoryByDate(self, start, end, REQUEST=None):
        """Search repository by date: start and end"""
        result = []

        for name in self.listStorages():
            s = self.getStorage(name)
            objects = s.searchDateRange(start, end)
            result.extend(objects)

        result.sort(lambda x, y: cmp(x.revised, y.revised))

        return result

    security.declarePublic("cookSearchTerms")
    def cookSearchTerms(self, query):
        """return the cooked search terms, as well as the uncook dictionary, aggregated across storages"""

        allcooked = []
        alluncook = {}
        for name in self.listStorages():
            s = self.getStorage(name)
            cooked,uncook = s.cookSearchTerms(query)
            for c in cooked:
                if not c in allcooked:
                    allcooked.append(c)
                    alluncook.setdefault(c,[]).extend(uncook[c])
            # Deal w/ stop words: must be stopped by _all_ searches
            # FIXME this code might now work, but is currently not exercised
            # since both storages use equivalent code for cookSearchTerms
            if alluncook.has_key(''):
                for s in alluncook['']:
                    if s not in uncook['']:
                        alluncook[''].remove(s)
            else:
                alluncook.update(uncook)

        return allcooked,alluncook
    
    def searchRepository(self, query, query_type="weakAND", weights=dsw, field_queries={}, sorton='weight',recent=False,use_cache=True,min_rating=0):
        """Search the repository: portal_types defaults to all types w/ storage objects
        Default weights are stored in default_search_weights on the repository
        """
        if not weights:
            weights = self.default_search_weights #AKA: dsw

        fq_list = field_queries.items()
        fq_list.sort()
        searchhash = str(query) + str(query_type) + str(weights) + str(fq_list)
        cached_res = self.cache.resultsCacheLookup(searchhash, sorton, recent)
        if use_cache and cached_res:
            result,term_results = cached_res
            return result,term_results,searchhash

        else:
            cached_sort = None
            # Build mapping of storage -> list of portal_types to query
            storages = {}
            # If no portal_types, search everything
            if not field_queries.has_key('portal_types'):
                for name in self.listStorages():
                    storages[name] = None

            else:
                for pt in field_queries.pop('portal_types')[0]:
                    storage = self._storage_map.get(pt, self._default_storage)
                    storages.setdefault(storage, []).append(pt)

            result = []
            skipped = []
            matched = []
            term_results = {}

#            restrict = [(t,v[0]) for t,v in field_queries.items() if v[1] == 'AND'] 
            restrict = None
            
            # First, the 'anywhere' query
            if query:
                for name, portal_types in storages.items():
                    storage = self.getStorage(name)
                    result.extend(storage.search(query, portal_types, weights, restrict, min_rating=min_rating))
                    
                result,skipped,matched = applyQueryType(result,query,query_type)
                term_results['any'] = (skipped,matched)

            # Now the rest.
            fq_list = field_queries.items()
            # sort by limit - all limit fields after result fields: this is needed for the intersect logic
            fq_list.sort(lambda x,y: cmp(x[1][2],y[1][2]))

            for field,(fquery,fquery_type,f_limit) in fq_list:
                fq_weights = {}
                if type(field) == type(()):
                    for f in field:
                        fq_weights[f] = self.default_search_weights[f]
                else:
                    fq_weights[field] = self.default_search_weights[field]

                fres = []
                for name, portal_types in storages.items():
                    storage = self.getStorage(name)
                    fres.extend(storage.search(fquery, portal_types, weights=fq_weights, restrict=restrict,min_rating=min_rating))

                fres,fskipped,fmatched = applyQueryType(fres,fquery,fquery_type)
                term_results[field] = (fskipped,fmatched)


                # intersect each result set with the previous ones. Each 
                # field_query is ANDed with the others (including the 
                # 'anywhere' query), IFF one of the previous searches had a matching term,
                # and this search had a matching term. This 'weakAND' drops any field that had
                # all of its terms dropped. The 'matched' dictionaries of each result object are updated
                # Since limit fields are last, they will not add to result set
                # if nothing before them matched.

                if fmatched:
                    if matched:
                        result_dict = dict([(r.objectId,r) for r in result])
                        result = [r for r in fres if r.objectId in result_dict]
                        for r in result:
                           for t,f in result_dict[r.objectId].matched.items():
                               r.matched.setdefault(t,[]).extend(f)
                           for t,f in result_dict[r.objectId].fields.items():
                               r.fields.setdefault(t,[]).extend(f)
                           r.weight += result_dict[r.objectId].weight
                    elif not f_limit:
                        result = fres
                        matched = fmatched

            result = self.sortSearchResults(result, sorton, recent)
            self.cache.resultsCacheInject(searchhash, (result,term_results,sorton,recent))
               
            return self.wrapResults(result),term_results,searchhash

    def wrapResults(self,results):
        """wrap list of results from pluggable brains or catalog record 
           searches to standalone DBModuleSearch objects that can be 
           pickled, and thus cached or stored in a session variable.
           This method is idempotent, so can safely be called on lists m
           """
        return [isinstance(res,DBModuleSearch) and res or DBModuleSearch(res) for res in results]

    security.declarePublic("sortSearchResults")
    def sortSearchResults(self, result, sorton,recent=False):
        """sort a result set"""

        def sort_rating(a, b):
            return cmp(getattr(b, 'rating', 0), getattr(a, 'rating', 0))

        if sorton=='weight':        
            result.sort(lambda x,y: int(y.weight-x.weight or cmpTitle(x,y)))
        elif sorton=='popularity':
            hc_tool = getToolByName(self, 'portal_hitcount', None)
            result.sort(lambda x,y: cmp(hc_tool.getPercentileForObject(y.objectId,recent), hc_tool.getPercentileForObject(x.objectId,recent)))
        elif sorton=='views':
            hc_tool = getToolByName(self, 'portal_hitcount', None)
            result.sort(lambda x,y: cmp(hc_tool.getHitCountForObject(y.objectId,recent), hc_tool.getHitCountForObject(x.objectId,recent)))
        elif sorton=='language':
            result.sort(lambda x,y: int(cmp(x.language,y.language) or cmpTitle(x,y)))
        elif sorton=='revised':
            result.sort(lambda x,y: int(cmp(y.revised,x.revised) or cmpTitle(x,y)))
        elif sorton=='title':
            result.sort(cmpTitle)
        elif sorton=='portal_type':
            result.sort(lambda x,y: int(cmp(x.portal_type,y.portal_type) or hasattr(y,'weight') and hasattr(x,'weight') and (y.weight-x.weight) or cmpTitle(x,y)))
        elif sorton == 'rating':
            result.sort(sort_rating)

        return self.wrapResults(result)
    
    def getContentByAuthor (self, authorid):
        """Return all content by a particular author"""

        return self.getContentByRole('author',authorid)
    
    def getContentByRole(self, role, user_id):
        """Return all content by where the user has the specified role"""

        storages = {}
        for name in self.listStorages():
            storages[name] = None
            
        content = []
        for name in storages.keys():
            storage = self.getStorage(name)
            content.extend(storage.getObjectsByRole(role, user_id))
            
        return content

def applyQueryType(result,query,query_type):
    #unique the query list
    #avoid dicts throughout, to preserve query term order
    r=[]
    for i in query:
        if not r.count(i):
            r.append(i)
    query=r

    if result:
        allres = [o for o in result if len(o.matched) == len(query)]
        matches = []
        for o in result:
            matches.extend(o.matched)
             
        zeros = [term for term in query if matches.count(term) == 0 ]
        if zeros:
            somelen = len(query) - len(zeros)
            someres = [o for o in result if len(o.matched) == somelen]
            someterms =  [t for t in query if t not in zeros]
        else:
            someres = allres
            someterms = query

        if query_type == 'AND':
            return allres, zeros, someterms
        elif query_type == 'weakAND':
            return someres, zeros, someterms
        elif query_type =='OR':
            return result, zeros, someterms
    else:
        return result, query, []
    
InitializeClass(Repository)
