"""
Folder for RhaptosModuleStorage Product

Authors: Brent Hendricks, Ross Reedstrom, Kyle Clarkson
(C) 2005,2006,2007 Rice University


This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import zLOG
import re
import os
import Acquisition
import AccessControl
from psycopg import ProgrammingError, IntegrityError
from ZODB.POSException import ConflictError
from OFS.SimpleItem import SimpleItem
from OFS.Traversable import Traversable
from OFS.PropertyManager import PropertyManager
from ExtensionClass import Base
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import package_home
from DateTime import DateTime
from zope.component import getAdapter
from zope.event import notify
from ComputedAttribute import ComputedAttribute
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.RhaptosModuleEditor.ModuleEditor import ModuleEditor
from Products.RhaptosRepository.VersionFolder import incrementMinor, VersionInfo
from Products.RhaptosRepository.Repository import Repository
from Products.RhaptosRepository.interfaces.IVersionStorage import IVersionStorage
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from Products.CNXMLTransforms.config import GLOBALS as CNXMLTRANSFORMS_GLOBALS
from Products.CNXMLTransforms.config import PROJECTNAME as CNXMLTRANSFORMS

from ModuleView import ModuleView
from ModuleDBTool import CommitError
from event import ModuleRatedEvent
from interfaces.rating import IRateable
from config import RATE_MODULE_PERMISSION

PUNCT_REGEXP = re.compile(r'([.,\'"~`@#$%^&*={}\[\]|\\:;<>/+\(\)!? 	])')

class ModuleVersionStorage(SimpleItem):

    __implements__ = (IVersionStorage)

    def __init__(self, id):
        self.id = id

    def generateId(self):
        """Create a unique ID for this object"""
        return 'm%d' % self.portal_moduledb.sqlGetNextModuleId()[0].moduleid

    def hasObject(self, id):
        """Return True if an object with the specified id is located in this storage"""
        return bool(self.portal_moduledb.sqlModuleExists(id=id))
    
    def createVersionFolder(self, object):
        """Create a new version folder instance inside the repository"""
        if not self.isUnderVersionControl(object):
             self.applyVersionControl(object)
        objectId = object.objectId
        folder = ModuleVersionStub(objectId, storage=self.id)
        self.aq_parent._setObject(objectId, folder, set_owner=0)

    def getVersionFolder(self, id):
        """Retrieve version folder instance for a specific ID"""
        return self.aq_parent[id]

    def getVersionInfo(self, object):
        objectId = getattr(object.aq_base, 'objectId', None)
        if objectId is None:
            return None

        # XXX: This should be stored in an __version_storage__ annotation on all objects, regardless of state
        state = object.state
        if state != 'public':
            object = object.getBaseObject()

        # XXX: Rather than omit the message we could subclass VersionInfo to dynamically retrieve it
        return VersionInfo(objectId, object.version, object.submitter, None, object.revised, object.state)

    def getHistory(self, id):
        """Return the module history"""
        return self.portal_moduledb.sqlGetHistory(id=id)

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

    def isUnderVersionControl(self, object):
        """Return true if the object is under version control"""
        # XXX: This should be be checking __version_storage__ if it existed...
        return getattr(object.aq_base, 'objectId', None) is not None and getattr(object.aq_base, 'version', None) is not None

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
        
        # The module if new if it has no history
        new = not self.getHistory(objectId)
        vf = self.getVersionFolder(objectId)

        if new:
            version = "1.1"
        else:
            # Sanity check: if latest version isn't the base of these changes, it's a problem
            # if not self.isLatestVersion(object):
            if (object.version != vf.latest.version):
                raise CommitError, "Version mismatch: version %s checked out, but latest is %s" % (object.version, vf.latest.version)
            version = incrementMinor(object.version)
            
            # We don't actually create a persistent object, but the user should have the permission
            # to do so (unless this is a new module...)
            if not _checkPermission(AddPortalContent, vf):
                raise Unauthorized, "You are not authorized to revise this module"

        # Explicity set repository/versioning metadata
        # FIXME: This should be taken care of by the workflow tool
        object.version = version
        revised = DateTime()
        object.revised = revised
        object.submitter = user
        object.submitlog = message

        # Create new metadata from template
        # FIXME: we should also change the ID in the text if appropriate
        file = object.getDefaultFile()
        file.setMetadata(object.getMetadata())
        file.setTitle(object.Title())

        # Update the database
        self.portal_moduledb.insertModuleVersion(object)

        # Insert links into the database
        source = '/'.join(['', vf.absolute_url(relative=1), version, ''])
        for link in object.getLinks():
            self.portal_linkmap.addLink(source, link.target, link.title, link.category, link.strength)

# Put it in the catalog 
#   Uses a sentinel so certain methods that access the catalog (Title) 
#   can short circuit
        modview = vf.latest
        modview._cataloging = True
        self.catalog.catalog_object(modview)
        del modview._cataloging


    def notifyObjectRevised(self, object, origobj=None):
        """One of this storage's objects was revised.
           We should trigger a more specific event.
    
        """
        ### This should be registered to the event for ObjectPublication
        ### once we have access to Zope3 events.  Something like:
        ### zope.event.notify(VersionFolderRevisionPublished)

        objmethod = getattr(object, 'notifyObjectRevised', None)
        if not objmethod is None:
            objmethod(origobj)

        ### For now, we're just going to call these directly, but in the future,
        ### it should subscribe to the event for VersionFolders being published
        # lens notification
        self.lens_tool.notifyLensContainedObject(object)
        
        # queue insertions
        qtool = getToolByName(self, 'queue_tool')
        key = "modexport_%s" % object.objectId
        dictRequest = { "id":object.objectId,
                        "version":object.version }
        script_location = 'SCRIPTSDIR' in os.environ and os.environ['SCRIPTSDIR'] or '.'
        qtool.add(key, dictRequest,
                  "%s/create_and_store_pub_module_export.zctl" % script_location)
        ### End Event System Hack

    def deleteObject(self, objectId, version=None):
        """
        Delete the specified object from storage.

        If version is None, delete all versions of the object,
        otherwise delete only the specified version.

        Raises IntegrityError if the object cannot be deleted because
        it is referenced by other objects
        """

        # Error if module is in a published course
        courses = self.catalog(containedModuleIds=objectId)
        if courses:
            raise IntegrityError, "Cannot delete: object %s in courses: %s" % (objectId, [c.objectId for c in courses])
        if version:
            try:
                #Remove the module from the database
                self.portal_moduledb.sqlDeleteModule(id=objectId, version=version)
            except IntegrityError, foo:
                raise IntegrityError, "Cannot delete: object %s version %s  has other works derived from it." % (objectId,version)
        else:
            try:
                #Remove the module from the database
                self.portal_moduledb.sqlDeleteModule(id=objectId)
            except IntegrityError, foo:
                raise IntegrityError, "Cannot delete: object %s has other works derived from it." % objectId
            
            #Delete the ZODB ModuleVersionStub
            self.aq_parent._delObject(objectId)
        
        #XXX:Should this be done here, or in Repository.py?
        #Remove any links that point to the module
        #self.portal_linkmap.deleteLinks(id, version)
    
    def getObject(self, id, version=None, **kw):
        """
        Return the object with the specified ID and version

        If there is no such object, it will raise a KeyError

        If version is None, return a 'version-less' object
        """
        # XXX: If version is None we should return the latest version,
        # but we're stuck for bw-compatibility right now
        try:
            ob = self.getVersionFolder(id)
        except AttributeError:
            raise KeyError, id
        if version:
            ob = ob._getModuleVersion(version, **kw)
        return ob
    
    def getObjects(self, objects):
        """
        Return sequence of objects with specified ID and versions

        objects must be a list of (id, version) tuples
        """
        return [self.getObject(obj[0],obj[1]) for obj in objects]
        
    def countObjects(self, portal_types=None):
        """
        Return the number of objects in the storage.

        If portal_types is specified, limit the results to objects of
        the given portal_types
        """

        count = self.portal_moduledb.sqlCountModules(portal_types=portal_types)[0].count
        
        return count

    def getLanguageCounts(self, portal_types=None):
        """Returns a list of tuples of language codes and count of objects 
        using them, ordered by number of objects, descending

        If portal_types is specified, limit the results to objects of
        the given portal_types
        """

        if type(portal_types) == type(''):
            portal_types = [portal_types]

        langs = list(self.portal_moduledb.sqlGetLanguageCounts(portal_types=portal_types).tuples())
        langs.sort(lambda x,y: cmp(y[1],x[1]))
        return langs
        
    def getObjectsByRole(self, role, user_id):
        """Return a list with all objects where the user has the specified role"""

        if role+'s' in self.catalog.indexes():
            cs =  list(self.catalog({role+'s':user_id,'portal_type':'Module'}))
        else:
            cs =  []
        m = self.portal_membership.getMemberById(user_id)
        for c in cs:
            c.weight = 0
            c.matched = {m.fullname:[role]}
            c.fields = {role:[m.fullname]}

        return cs

# Revist this, see if it's the pluggable brain issue
#        try:
#            return list(self.portal_moduledb.sqlGetModulesByRole(user=user_id, role=role))
#        except ProgrammingError:
#            return []

    def search(self, query, portal_types=None,weights={}, restrict=[], min_rating=0):
        """
        Search the storage
        Default match weights: 
            fulltext (fulltext) = 1
            keyword  (keyword) = 10 
            Author   (name/id)(author) = 10 
            title    (title) = 100
            ObjectId (objectid) = 1000
        """
        if not hasattr(self,'default_search_weights'):
            self.default_search_weights = {
                    'fulltext':1,
                    'abstract':1,
                    'keyword':10,
                    'author':50, 
					'translator':40,
                    'editor':20,
					'maintainer':10,
					'licensor':10,
                    'institution':10, 
                    'exact_title':100,
                    'title':10,
					'parentAuthor':0,
                    'containedIn':200,
                    'objectid':1000}
        if not weights:
            weights = self.default_search_weights
        else:
            for w in self.default_search_weights.keys():
               weights.setdefault(w,0)
        
        dbquery,uncook = self.cookSearchTerms(query)
        results = []
        if dbquery:
            # Note: This converts the lazymap to a regular list
            results.extend(self.portal_moduledb.sqlSearchModules(query=dbquery,weights=weights,required=restrict,min_rating=min_rating))

        newmatched={}
	newfields={}
        for r in results:
            for m,v in r.matched.items(): 
                for u in uncook[m]:
                    newmatched[u] = v
            r.matched.clear()
            r.matched.update(newmatched)
            newmatched.clear()

            for m,v in r.fields.items(): 
		newfields[m]=reduce(lambda x,y:x+y,[uncook[t] for t in v],[])
            r.fields.clear()
            r.fields.update(newfields)
            newfields.clear()

        return results

    def searchDateRange(self, start, end):
        """
        Search for objects whose latest version is within the specified date range

        start and end must be DateTime objects
        """
        return self.portal_moduledb.sqlSearchModulesByDate(start=start,end=end)

    # XXX: Included for backwards compatability:
    def isLatestVersion(self, object):
        """
        Return True if the object is the most recently checked in version
        """
        return self.isResourceUpToDate(object)


    def cookSearchTerms(self, terms):
        lex = self.catalog.lexicon

        query = []
        reverse = {}
        for t in terms:
            if (lex.parseTerms(t)):
                #term is not all stopwords. Use the below to avoid stripping stopwords from inside quoted query strings, like "Science and Technology"
                term = ' '.join(lex._pipeline[lex.getPipelineNames().index('StopWordAndSingleCharRemover')].process([t.strip().lower()]))
            else:
                term = ''
            reverse.setdefault(term,[]).append(t)

	# unique the terms, in case any collided
        query = filter(None,reverse)

        return query, reverse

class ModuleVersionStub(SimpleItem, PropertyManager):
    """Zope object to hold versions of an object"""

    meta_type = 'Module Version Folder'
    security = ClassSecurityInfo()

    __allow_access_to_unprotected_subobjects__ = 1

    manage_options = PropertyManager.manage_options + SimpleItem.manage_options

    # Special 'latest' attribute points to most recent version
    security.declarePublic('latest')
    latest = ComputedAttribute(lambda self: self._getModuleVersion('latest'), 1)

    def __init__(self, id, storage, **kwargs):
        #Acquisition.__init__(self, id, **kwargs)
        #self.__name__ = id
        self.id = id
        self.storage = storage
        self._endorsed = False

    def __getitem__(self, name):
        version = self._getModuleVersion(name)
        if not version:
            raise KeyError, name
        return version

    security.declarePublic('getId')
    def getId(self):
        """Return my ID"""
        return self.id

    security.declarePrivate('_getModuleVersion')
    def _getModuleVersion(self, version, **kwargs):
        #self._log("Module %s: retrieving version %s" % (self.id, version), zLOG.INFO)
        if version == 'latest':
            return ModuleView(version, self.id, **kwargs).__of__(self)
        else:
            versions = [h.version for h in self.aq_parent.getHistory(self.id)]
            if version in versions:
                return ModuleView(version, self.id, **kwargs).__of__(self)
            else:
                raise KeyError, version

    security.declarePublic('index_html')
    def index_html(self):
        """ Redirect to latest version """
        path = self.REQUEST.URL1 + '/latest/'
        if self.REQUEST.QUERY_STRING:
            path = path + '?' + self.REQUEST.QUERY_STRING
        self.REQUEST.RESPONSE.redirect(path, status=301)
    
    security.declarePrivate('_log')
    def _log(self, message, severity):
        zLOG.LOG("ModuleVersionStub", severity, "%s (%s)" % (message, self.REQUEST['PATH_INFO']))

    security.declarePublic('url')
    def url(self):
        """Return the canonical URL used to access the latest version"""
        return self.absolute_url() + '/latest/'

    def getHistoryCount(self):
        """Return the number of versions of the object"""
        return len(self.aq_parent.getHistory(self.id))
    
    # FIXME: These should be in a skin
    _created = PageTemplateFile('zpt/created', globals())
    security.declareProtected('Edit Rhaptos Object', 'postUpdate')
    def postUpdate(self):
        """Allow users to post updates over the web"""

        # GET on this method does nothing
        if self.REQUEST['REQUEST_METHOD']=="GET":
            self.REQUEST.RESPONSE.setStatus(204)
            return

        if self.REQUEST.has_key('moduleText'):
            content = self.REQUEST['moduleText']        
        elif self.REQUEST.has_key('BODY'):
            content = self.REQUEST['BODY']
        else:
            raise CommitError, "No text provided"

        try:
            baseVersion = self.REQUEST['baseVersion']
        except KeyError:
            raise CommitError, "No base version specified"

        try:
            message = self.REQUEST['message']
        except KeyError:
            raise CommitError, "No commit message specified"

        # Checkout latest copy to a temp folder
        tmp = ModuleEditor('latest').__of__(self)
        tmp.setState('published')
        tmp.checkout(self.id)
        self._log("Checking out working copy of module %s" % self.id, zLOG.BLATHER)

        # Update module text and validate it
        file = tmp.getDefaultFile()
        file.manage_upload(content)
        results = file.validate()
        if results:
            raise CommitError, "Module text not valid: %s" % results
        else:
            self.content.publishRevision(tmp, message)

        # Pretend like we're going to delete the temporary folder so it gets unindexed
        #tmp.manage_beforeDelete(folder, self)
        del tmp
        
        # If its successful, return nothing
        self.REQUEST.RESPONSE.setStatus(201)
        url = self.latest.absolute_url()
        self.REQUEST.RESPONSE.setHeader('Location', url)
        return self._created(url=url)

    # ---- Local role manipulations to allow group memners access
    security.declarePrivate('_getLocalRoles')
    def _getLocalRoles(self):
        """Query the database for the local roles in this workgroup"""
        # Give all maintainers the 'Maintainer' role
        dict = {}
        try:
            for m in self.latest.maintainers:
                dict[m] = ['Maintainer']
        except IndexError:
            pass  # module couldn't be located, but don't explode
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

    # Set default roles for these permissions
    security.setPermissionDefault('Edit Rhaptos Object', ('Manager', 'Owner','Maintainer'))

    security.declareProtected('Edit Rhaptos Object', 'endorse')
    def endorse(self, REQUEST=None):
        """Set endorsed to True"""
        self._endorsed = True
        if REQUEST is not None:
            msg = _("You have endorsed the module")
            getToolByName(self, 'plone_utils').addPortalMessage(msg)
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected('Edit Rhaptos Object', 'denounce')
    def denounce(self, REQUEST=None):
        """Set endorsed to False"""
        self._endorsed = False
        if REQUEST is not None:
            msg = _("You have removed the endorsement from the module")
            getToolByName(self, 'plone_utils').addPortalMessage(msg)
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(View, 'endorsed')
    def endorsed(self):       
        return getattr(self, '_endorsed', False)

    security.declareProtected(View, 'canEndorse')
    def canEndorse(self):
        # todo: check that module is associated with an open lens
        pms = getToolByName(self, 'portal_membership')
        member = pms.getAuthenticatedMember()
        return member.has_permission('Edit Rhaptos Object', self)

    security.declareProtected(RATE_MODULE_PERMISSION, 'rate')
    def rate(self, value, REQUEST=None):
        """
        Register a rate

        params:
            value: a non-negative integer not greater than 5

        return:
            nothing
        """
        if (value > 5) or (value < 0):
            if REQUEST is not None:
                msg = _("Your rating (%s) is invalid" % value)
                getToolByName(self, 'plone_utils').addPortalMessage(msg)
                REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            return

        # Stop a user from rating twice or more
        pm = getToolByName(self, 'portal_membership')
        member = pm.getAuthenticatedMember()
        adapted = getAdapter(member, IRateable)
        if adapted.hasRating(self.id):
            if REQUEST is not None:
                msg = _("You have already rated this module")
                getToolByName(self, 'plone_utils').addPortalMessage(msg)
                REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
            return

        adapted.rate(self.id, value)
        self.portal_moduledb.sqlRegisterRating(moduleid=self.id, version=self.latest.version, rating=value)
        notify(ModuleRatedEvent(self))
           
        if REQUEST is not None:
            msg = _("Your rating has been registered")
            getToolByName(self, 'plone_utils').addPortalMessage(msg)
            REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(View, 'rating')
    def rating(self):
        """
        Return the average rating

        return:
            the average rating
        """
        res = self.portal_moduledb.sqlGetRating(moduleid=self.id, version=self.latest.version)
        if not res:
            return 0.0
        totalrating = res[0].totalrating
        votes = res[0].votes
        if votes == 0:
            return 0.0
        return round(totalrating * 1.0 / votes, 1)

    security.declareProtected(View, 'numberOfRatings')
    def numberOfRatings(self):
        """
        Return the number of times the item was rated
        """
        res = self.portal_moduledb.sqlGetRating(moduleid=self.id, version=self.latest.version)
        if not res:
            return 0
        return res[0].votes

    #security.declareProtected('Edit Rhaptos Object', 'setGoogleAnalyticsTrackingCode')
    security.declarePublic('setGoogleAnalyticsTrackingCode')
    def setGoogleAnalyticsTrackingCode(self, GoogleAnalyticsTrackingCode):
        """set the Google Analytics Tracking Code"""
        self._GoogleAnalyticsTrackingCode = GoogleAnalyticsTrackingCode

    security.declarePublic('getGoogleAnalyticsTrackingCode')
    def getGoogleAnalyticsTrackingCode(self):
        """set the Google Analytics Tracking Code"""
        if hasattr(self,'_GoogleAnalyticsTrackingCode'):
            return self._GoogleAnalyticsTrackingCode
        else:
            return None

InitializeClass(ModuleVersionStub)

