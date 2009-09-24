"""
Folder to hold versions of an object for RhaptosRepository Product 

Author: Brent Hendricks and Ross Reedstrom
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import zLOG
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.PortalFolder import PortalFolder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime
from ComputedAttribute import ComputedAttribute
from Products.RhaptosModuleStorage.ModuleDBTool import CommitError
from LatestReference import addLatestReference

from interfaces.IVersionStorage import IVersionStorage

HISTORY_FIRST_ID = 10000

# dummy add methods to support copy
from Globals import DTMLFile
manage_addVersionFolderForm=DTMLFile('www/addform', globals())
def manage_addVersionFolder(self, id, title=''):
    pass

class VersionFolderStorage(SimpleItem):

    __implements__ = (IVersionStorage)

    def __init__(self, id):
        self.id = id
        self._next_id = HISTORY_FIRST_ID

    def generateId(self):
        """Create a unique ID for this object"""
        self._next_id = self._next_id + 1
        return 'col%d' % self._next_id

    def hasObject(self, id):
        """Return True if an object with the specified id is located in this storage"""
        # XXX: Should we do something more in intelligent?
        return hasattr(self.aq_parent.aq_base, id)
    
    def createVersionFolder(self, object):
        """Create a new version folder instance inside the repository"""
        if not self.isUnderVersionControl(object):
            self.applyVersionControl(object)
        objectId = object.objectId
        folder = VersionFolder(objectId, storage=self.id)
        self.aq_parent._setObject(objectId, folder, set_owner=0)

    def getVersionFolder(self, id):
        """Retrieve version folder instance for a specific ID"""
        return getattr(self.aq_parent.aq_explicit, id)

    def getVersionInfo(self, object):
        objectId = getattr(object.aq_base, 'objectId', None)
        if objectId is None:
            return None

        # XXX: This should be stored in an __version_storage__ annotation
        state = object.getState()
        if object.getState() != 'public':
            object = object.getBaseObject()

        return VersionInfo(objectId, object.getVersion(), object.submitter, object.submitlog, object.getRevised(), state)

    def getHistory(self, id):
        """Return the object history"""
        # Sort by date of revision (DSU sort from Ch 2.6 python patterns)
        vf = self.getVersionFolder(id)
        tmp = [(r.revised, r) for r in vf.objectValues() if r.meta_type != 'Latest Reference']
        tmp.sort()
        tmp.reverse()
        return [revision for date, revision in tmp]

    def isUnderVersionControl(self, object):
        """Return true if the object is under version control"""
        # XXX: This should be be checking __version_storage__ if it existed...
        return getattr(object.aq_base, 'objectId', None) is not None and getattr(object.aq_base, 'version', None) is not None

    def applyVersionControl(self, object):
        """
        Place the object under version control

        Returns a unique identifier associated with this object's
        version history
        """
        if self.isUnderVersionControl(object):
            raise VersionControlError('The resource is already under version control.')

        objectId = self.generateId()
        object.objectId = objectId
        return objectId
    
    def isResourceUpToDate(self, object):
        """
        Return True if the object is the most recently checked in version
        """    
        version = object.version
        try:
            latest = object.aq_parent.latest
        except AttributeError:
            # XXX: This is broken.  Why do we return True if we can't
            # find latest?  Because otherwise checked-out content
            # would should a 'This content is not latest' warning.
            # That should be fixed elsewhere
            return True
        return latest.version == version

    def checkinResource(self, object, message='', user=None):
        """
        Checkin a new version of an object to the repository

        object  : the new object
        message : a string describing the changes
        user    : the name of the user creating the new version
        """

        objectId = object.objectId
        vf = self.getVersionFolder(objectId)
        
        # Initialize history if it doesn't exist yet
        if not vf.objectIds():
            version = "1.1"
            addLatestReference(vf, 'latest', '', version)
        else:
            # Sanity check: if latest version isn't the base of these changes, it's a problem
            # if not self.isLatestVersion(object):
            version = object.getVersion()
            if (version != vf.latest.getVersion()):
                raise CommitError, "Version mismatch: version %s checked out, but latest is %s" % (version, vf.latest.getVersion())
            version = incrementMinor(version)
            
        # Clone the object as a new revision of this collection
        #self._log("Cloning %s" % obj, zLOG.INFO)
        zLOG.LOG("VersionFolder", zLOG.INFO, "Cloning %s (%s)" % (object, self.REQUEST['PATH_INFO']))
        vf.manage_clone(object, version)
        clone = getattr(vf, version)

        # Explicity set repository/versioning metadata
        # FIXME: This should be taken care of by the workflow tool
        try:
            clone.setVersion(version)
        except AttributeError:
            clone.version = version
        try:
            clone.setRevised(DateTime())
        except AttributeError:
            clone.revised = DateTime()
        clone.submitter = user
        clone.submitlog = message
        # The state must be public so the object uses the correct method for viewing (ewwww!)
        clone.state = 'public'

        # Reset the 'latest' reference
        vf.latest.edit(clone.Title(), version)
        self.catalog.catalog_object(vf.latest)

    def notifyObjectRevised(self, object, origobj=None):
        """One of this storage's objects was revised.
           We should trigger a more specific event.
        """
        objmethod = getattr(object, 'notifyObjectRevised', None)
        if not objmethod is None:
            objmethod(origobj)
        
    def getObject(self, id, version=None, **kw):
        """
        Return the object with the specified ID and version

        If there is no such object, it will raise a KeyError

        If version is None, return a 'version-less' object
        """
        # XXX: If version is None we should return the latest version,
        # but we're stuck for bw-compatibility right now
        try:
            ob = getattr(self.aq_parent, id)
        except AttributeError:
            raise KeyError, id

        if version:
            try:
                ob = getattr(ob, version)
            except AttributeError:
                raise KeyError, version

        return ob

    def getObjects(self, objects):
        """
        Return sequence of objects with specified ID and versions

        objects must be a list of (id, version) tuples
        """
        
        return [self.getObject(obj[0],obj[1]) for obj in objects]

    def deleteObject(self, objectId, version=None):
        """
        Delete the specified object from storage.

        If version is None, delete all versions of the object,
        otherwise delete only the specified version.

        Raises IntegrityError if the object cannot be deleted because
        it is referenced by other objects
        """

        children = self.aq_parent.catalog(parent=objectId)

        if version:
            vf = self.getVersionFolder(objectId)
            history = self.getHistory(objectId)
        else:
            history = []
        # This 'if' block depends on the variables set in the previous one
        if len(history) > 1:
                
            if ([c for c in children if c.getObject().getParent().version == version]):
                raise IntegrityError, "Cannot delete: object %s version %s has other works derived from it." % (objectId,version)

            # Repoint latest if necessary 
            if vf.latest.getVersion() == version:
                previous = history[1]
                vf.latest.edit(previous.Title(), previous.getVersion())
                self.aq_parent.catalog.catalog_object(vf.latest)

            vf.manage_delObjects(version)
        else:
            # Or, just blow it away if it's the whole collection
            if children:
                raise IntegrityError, "Cannot delete: object %s has other works derived from it." % objectId
            self.aq_parent.manage_delObjects(objectId)
    
    def countObjects(self, portal_types=None):
        """
        Return the number of objects in the storage.

        If portal_types is specified, limit the results to objects of
        the given portal_types
        """

        count = 0
        if portal_types:
            for pt in portal_types:
                count += len(self.catalog(portal_type=pt))
        else:
            count = len(self.catalog(portal_type='Collection'))

        return count

    def getLanguageCounts(self, portal_types=None):
        """Return a list of tuples of language code: object counts"""

        if type(portal_types) == type(''):
            portal_types = [portal_types]
        
        cat = self.catalog

        if not portal_types or 'Collection' in portal_types:
            langcount=[]
            langs = list(cat.Indexes['language'].uniqueValues())
            for l in langs:
                langcount.append((l,len(cat(language=l,portal_type='Collection'))))
            langcount.sort(lambda x,y: cmp(y[1],x[1]))
            return langcount
        else:
            return None


    def getObjectsByRole(self, role, user_id):
        """Return a list with all objects where the user has the specified role"""

        if role+'s' in self.catalog.indexes():
            cs =  list(self.catalog({role+'s':user_id,'portal_type':'Collection'}))
        else:
            cs =  []

        
        m = self.portal_membership.getMemberById(user_id)
        for c in cs:
            c.weight = 0
            c.matched = {m.fullname:[role]}
            c.fields = {role:[m.fullname]}

        return cs


    def search(self, query, portal_types=None, weights={}, restrict=[], min_rating=0):
        """
        Search the storage

        params:
            min_rating: not used in this method but required by API
        """
        
        if not weights:
            if hasattr(self,'default_search_weights'):
                weights = self.default_search_weights
            else:
                weights = {'fulltext':1,'abstract':1,'keyword':10, 'author':50, 'translator':40,
			'editor':20, 'maintainer':10, 'licensor':10, 'subject':10,'institution':10,
			'language':5, 'exact_title':100, 'title':10, 'containedIn':200, 'objectid':1000,
			'containedAuthor':0, 'maintainer':0,'parentAuthor':0}


	person_fields = [k for k in weights.keys() if k in ['author','translator','editor','maintainer'] and weights[k]]

        # Query is a list of words, need to remove stopwords
        cooked,uncook = self.cookSearchTerms(query)

        # Search by exact objectid match, then Title, then institution, keywords, abstract, then authors
        objects = {}
        for cooked_term in cooked:
            for w in uncook[cooked_term]:
                quoted = '"' + w + '"'
                if weights.has_key('language') and weights['language']:
                    cs = self.catalog({'baselanguage':w,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight += weights['language']
                        object.matched.setdefault(w,[]).append('language')
                        object.fields.setdefault('language',[]).append(w)
                
                if weights.has_key('subject') and weights['subject']:
                    cs = self.catalog({'subject':w,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight += weights['subject']
                        object.matched.setdefault(w,[]).append('subject')
                        object.fields.setdefault('subject',[]).append(w)
                
                if weights.has_key('objectid') and weights['objectid']:
                    cs = self.catalog({'objectId':w,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight += weights['objectid']
                        object.matched.setdefault(w,[]).append('objectid')
                        object.fields.setdefault('objectid',[]).append(w)
                
                if weights.has_key('containedIn') and weights['containedIn']:
                    cs = self.catalog({'containedModuleIds':w,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight += weights['containedIn']
                        object.matched.setdefault(w,[]).append('containedIn')
                        object.fields.setdefault('containedIn',[]).append(w)
                
                if weights.has_key('exact_title') and weights['exact_title']:
                    cs = self.catalog({'Title':quoted,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight += weights['exact_title']
                        object.matched.setdefault(w,[]).append('title')
                        object.fields.setdefault('title',[]).append(w)
                    
                if weights.has_key('title') and weights['title']:
                    cs = self.catalog({'Title':'"*'+w+'*"','portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight += weights['title']
                        object.matched.setdefault(w,[]).append('title')
                        object.fields.setdefault('title',[]).append(w)
                    
                if weights.has_key('institution') and weights['institution']:
                    cs = self.catalog({'institution':quoted,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight += weights['institution']
                        object.matched.setdefault(w,[]).append('institution')
                        object.fields.setdefault('institution',[]).append(w)
                    
                if weights.has_key('keyword') and weights['keyword']:
                    cs = self.catalog({'keywords':w,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight  += weights['keyword']
                        object.matched.setdefault(w,[]).append('keyword')
                        object.fields.setdefault('keyword',[]).append(w)

                    cs = self.catalog({'keywordstext':quoted,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight  += weights['keyword']/10
                        object.matched.setdefault(w,[]).append('keyword')
                        object.fields.setdefault('keyword',[]).append(w)
                    
                    
                if weights.has_key('abstract') and weights['abstract']:
                    cs = self.catalog({'abstract':quoted,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight  += weights['abstract']
                        object.matched.setdefault(w,[]).append('abstract')
                        object.fields.setdefault('abstract',[]).append(w)
    
                if weights.has_key('containedAuthor') and weights['containedAuthor']:
                    cs = self.catalog({'containedModuleAuthors':w,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight  += weights['containedAuthor']
                        object.matched.setdefault(w,[]).append('containedAuthor')
                        object.fields.setdefault('containedAuthor',[]).append(w)
    
                if weights.has_key('parentAuthor') and weights['parentAuthor']:
                    cs = self.catalog({'parentAuthors':w,'portal_type':'Collection'})
                    for c in cs:
                        c.weight = 0
                        c.matched={}
                        c.fields={}
                        object = objects.setdefault(c.objectId, c)
                        object.weight  += weights['parentAuthor']
                        object.matched.setdefault(w,[]).append('parentAuthor')
                        object.fields.setdefault('parentAuthor',[]).append(w)
    
                if person_fields:
                # Get potential authorids, then find objects with those ids
                    authors = self.portal_moduledb.sqlGetPeoplebyName(query=[w])
                    for author in authors:
			for field in person_fields:
                                cs = self.catalog({field+'s':author.personid,'portal_type':'Collection'})
                                for c in cs:
                                    c.weight = 0
                                    c.matched={}
                                    c.fields={}
                                    object = objects.setdefault(c.objectId, c)
                                    object.weight  += weights[field] 
                                    object.matched.setdefault(w,[]).append(field)
                                    object.fields.setdefault(field,[]).append(w)
    
        result = objects.values()
        if result is not None:
            result.sort(lambda x,y: y.weight-x.weight)
        else:
            result = []

        return result


    def searchDateRange(self, start, end):
        """
        Search for objects whose latest version is within the specified date range

        start and end must be DateTime objects
        """
        result = []

        # ZCatalog DateIndex range search doesn't pay attention to
        # order of arguments.  Return no results if range is backwards
        if end < start:
            return result

        # XXX: Do we really need all this stuff with weights since there's only one criterion?
        objects = {}
        cs = self.catalog(revised={'query': [start,end], 'range': 'minmax'},portal_type='Collection')
        for c in cs:
            c.weight = 0
            objects.setdefault(c.objectId, c).weight += 1000

        result = objects.values()
        result.sort(lambda x,y: y.weight-x.weight)
        return result
    
    def cookSearchTerms(self, terms):
        lex = self.catalog.lexicon
        uncook = {}
        for ct, t in [(' '.join(lex.parseTerms(term)),term) for term in terms]:
            uncook.setdefault(ct,[]).append(t)
        results = filter(None, uncook)

        return results, uncook

    # XXX: Included for backwards compatability:
    def isLatestVersion(self, object):
        """
        Return True if the object is the most recently checked in version
        """
        return self.isResourceUpToDate(object)
                                            
class VersionFolder(PortalFolder):
    """Zope object to hold versions of an object"""

    meta_type = 'Version Folder'
    security = ClassSecurityInfo()

    def __init__(self, id, title='', storage=None):
        PortalFolder.__init__(self, id, title)
        self.storage = storage

    security.declarePublic('index_html')
    def index_html(self):
        """ Redirect to latest version """
        path = self.REQUEST.URL1 + '/latest/'
        if self.REQUEST.QUERY_STRING:
            path = path + '?' + self.REQUEST.QUERY_STRING
        self.REQUEST.RESPONSE.redirect(path, status=301)

    security.declarePublic('view')
    def view(self):
        """Plain view of the object, new Plone style."""
        self.index_html()

    security.declarePublic('url')
    def url(self):
        """Return the canonical URL used to access the latest version"""
        return self.absolute_url() + '/latest/'
 
    def getHistoryCount(self):
        """Return the number of versions of the object"""
        # FIXME: We really shouldn't be hardcoding the meta_type, but
        # this prevents all the subobjects from being woken up
        return len(self.objectIds(['Collection']))

    def manage_beforeDelete(self, object, container):
        PortalFolder.manage_beforeDelete(self, object, container)
        self.catalog.uncatalog_object(self.latest.absolute_url_path())

    # ---- Local role manipulations to allow group memners access
    security.declarePrivate('_getLocalRoles')
    def _getLocalRoles(self):
        """Query the database for the local roles in this workgroup"""
        # Give all maintainers the 'Maintainer' role
        dict = {}
        for m in self.latest.maintainers:
            dict[m] = ['Maintainer']
        return dict

    __ac_local_roles__ = ComputedAttribute(_getLocalRoles, 1)

    def manage_addLocalRoles(self, userid, roles, REQUEST=None):
        """Set local roles for a user."""
        pass

    def manage_setLocalRoles(self, userid, roles, REQUEST=None):
        """Set local roles for a user."""
        pass

    def manage_delLocalRoles(self, userids, REQUEST=None):
        """Remove all local roles for a user."""
        pass

    def setGoogleAnalyticsTrackingCode(self, GoogleAnalyticsTrackingCode):
        """set the Google Analytics Tracking Code"""
        self._GoogleAnalyticsTrackingCode = GoogleAnalyticsTrackingCode

    def getGoogleAnalyticsTrackingCode(self):
        """set the Google Analytics Tracking Code"""
        if hasattr(self,'_GoogleAnalyticsTrackingCode'):
            return self._GoogleAnalyticsTrackingCode
        else:
            return None

    # Set default roles for these permissions
    security.setPermissionDefault('Edit Rhaptos Object', ('Manager', 'Owner','Maintainer'))


class VersionInfo:

    def __init__(self, objectId, version, user, message, timestamp, state):
        self.objectId = objectId
        self.version = version
        self.user = user
        self.message = message
        self.timestamp = timestamp
        self.state = state


# Utility functions

# FIXME: we need a more robust way to do this
def incrementMinor(version):
    i = 0
    while i < len(version):
        if version[i] == '.':
            major = version[:i]
            minor = version[i+1:]
        i = i + 1

    #(major, minor) = getMajorMinor(version)
    minor = str(int(minor) + 1)
    return major + '.' + minor

def incrementMajor(version):
    i = 0
    while i < len(version):
        if version[i] == '.':
            major = version[:i]
            minor = version[i+1:]
        i = i + 1

    #(major, minor) = getMajorMinor(version)
    major = str(int(major) + 1)
    minor = '0'
    return major + '.' + minor

InitializeClass(VersionFolder)
