"""
ModuleView for RhaptosModuleEditor Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import re
import os
import tempfile
import shutil
import mimetypes
import OFS, zLOG, AccessControl
from DateTime.DateTime import DateTime, SyntaxError as DTSyntaxError
from urlparse import urlparse
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from ComputedAttribute import ComputedAttribute
from webdav.common import rfc1123_date
from Products.CMFCore.utils import getToolByName
from Products.CNXMLDocument.CNXMLFile import CNXMLFile
from Products.CNXMLDocument import XMLService
from Products.CNXMLDocument import CNXML_SEARCHABLE_XSL as baretext
from DBIterator import rhaptosdb_iterator

# for setting _p_mtime (ZODB modified time) on our transitory File objects
# see http://archive.netbsd.se/?ml=zope-dev&a=2000-03&t=3908618
from ZODB.TimeStamp import TimeStamp
def set_mtime(ob, t):
    """Set object 'ob' ZODB modified time to 't', which is a Zope DateTime. Useful for File/Image Last-Modified handling."""
    ts = apply(TimeStamp, t.toZone('GMT').parts()[:6])
    ob._p_serial = repr(ts)

class ModuleFile(rhaptosdb_iterator):
    """A wrapper around the db iterator to provide some file-type methods"""
    isPrincipiaFolderish = False
    
    def __init__(self, parent, *args, **kw):
        """Create ModuleFile, backed by DBIterator StreamIterator.
        See the init of that class for most of the init args. This adds 'parent'.
        """
        rhaptosdb_iterator.__init__(self, *args, **kw)
        self._parent = parent
        self.revised = parent.revised

    def seek(self, offset, whence=0):
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        elif whence == 2:
            self.pos = len(self)+offset

    def tell(self):
        return self.pos

    def read(self,size=None):
        cur = self.db.cursor()
        if size is None or size < 0:
            cur.execute('SELECT substr(file,%s) AS data %s' % (self.pos+1,self.statement))
            self.pos = len(self)
        else:
            cur.execute('SELECT substr(file,%s,%s) AS data %s' % (self.pos+1,size,self.statement))
            self.pos += size
        res =  cur.dictfetchone()
        if res:
            data = res['data']
        else:
            data = ''
        return data

    def __str__(self):
        self.pos=0
        return self.read()

    def modified(self):
        return getattr(self,'revised')
    
    def data(self):
        return self.__str__()
    
    def getPhysicalPath(self):
        return self._parent.getPhysicalPath() + (self.name,)

    def content_type(self):
        cur = self.db.cursor()
        cur.execute('SELECT mimetype %s' % (self.statement))
        res =  cur.dictfetchone()
        if res:
            return res['mimetype']
        else:
            return None
    

class ModuleView(SimpleItem):
    """Dyamically created Zope object for displaying Modules"""

    security = AccessControl.ClassSecurityInfo()
    
    meta_type = 'Rhaptos Module View'
    icon = 'module_icon.gif'
    isPrincipiaFolderish = 1
    state = 'public'
    actor = None
    getPendingCollaborations = None

    def __init__(self, id, objectId, data=None, **kwargs):
        # Since this is a versioned object, the id is the version
        self.id = id
        self.objectId = objectId
        self._data = data


    def _log(self, message, severity):
        zLOG.LOG("ModuleView", severity, "%s (%s)" % (message, self.REQUEST['PATH_INFO']))

    def _setLastModHeader(self):
        #print self.revised
        self.REQUEST.RESPONSE.setHeader('Last-Modified', rfc1123_date(self.revised))


    def __getitem__(self, name):
        """basic get item"""
        if name == self.getDefaultFilename():
            f = self.getDefaultFile()
        else:
            if name in self.objectIds():
                f = self.getFile(name)
            else:
                raise KeyError, name
        return f


    security.declarePublic('index_html')
    def index_html(self):
        """Default display method"""
        # If we got here without specifying the trailing slash, redirect
        if not self.REQUEST.PATH_INFO[-1].endswith('/'):
            path = self.REQUEST.URL1 + '/'
            if self.REQUEST.QUERY_STRING:
                path = path + '?' + self.REQUEST.QUERY_STRING
            self.REQUEST.RESPONSE.redirect(path, status=301)

        # Otherwise, do the default
        else:
            return self.default()

    security.declarePublic('isPublic')
    def isPublic(self):
        """Boolean answer true iff collection is in versioned repository.
        Based currently on value of 'state' attribute.
        """
        return True

    security.declarePublic('url')
    def url(self):
        """Return the canonical URL used to access the object"""
        return self.absolute_url() + '/'

    security.declarePrivate('_getDBProperty')
    def _getDBProperty(self, property):
        """Get module property from DB storage"""
        # Store local copy of DB data so we don't have to keep looking it up
        if not self._data:
            #self._log("Querying DB for %s" % self.objectId, zLOG.INFO)
            if not self.id or self.id == 'latest':
                data = self.portal_moduledb.sqlGetLatestModule(id=self.objectId)
            else:
                data = self.portal_moduledb.sqlGetModule(id=self.objectId, version=self.id)
            try:
                self._data = data[0]
            except IndexError:
                raise IndexError, "Couldn't find version %s of object %s" % (self.id, self.objectId)
        return getattr(self._data, property)


    security.declarePublic('getKeywords')
    def getKeywords(self):
        """Return list of keywords"""
        return tuple([row.word for row in self.portal_moduledb.sqlGetKeywords(ident=self.ident)])

    security.declarePublic('Title')
    def Title(self):
        """Return title; some performance optimizations over plain 'title' attribute."""
        if not hasattr(self,'_cataloging') and self.isLatestVersion(self):  # ...acquired from Repository
            # catalog retrieval only for 'latest'; we don't store values for old modules
            # _cataloging is a semaphore for when cataloging is going on right after publish
            try:
                cat = getToolByName(self, 'content').catalog
                mod = cat(objectId=self.objectId)
                if mod:
                    return mod[0].Title
            except AttributeError: # not be in content context?
                pass

        return self.title


    security.declarePublic('wrapAbstract')
    def wrapAbstract(self, terms, open_wrap_tag='<b>', close_wrap_tag='</b>'):
        """Wrap matches to list of terms with tags. Returns tuple of (excerpt,abstract)"""
        q = '&'.join(terms)
        res = self.portal_moduledb.sqlWrapAbstract(moduleid=self.objectId,
                    version=self.version, query=q, open_wrap_tag='OPEN_CNX_WRAP_TAG',
                    close_wrap_tag='CLOSE_CNX_WRAP_TAG')
        headline,abstract =res.tuples()[0]
        cutoff = 20

        headline_start = abstract.find(headline)

        if headline_start != -1:
            headline_end = headline_start + len(headline)
            head = abstract[:headline_start]
            tail = abstract[headline_end:]

            if len(' '.join(head.split()[2:])) > cutoff:
                headline = ' '.join(head.split()[:2])+" ... "+headline
            else:
                headline = head+headline

            if len(' '.join(tail.split()[:-2])) > cutoff:
                headline = headline+" ... "+' '.join(tail.split()[-2:])
            else:
                headline = headline + tail
        return (headline.replace('OPEN_CNX_WRAP_TAG',open_wrap_tag).replace('CLOSE_CNX_WRAP_TAG',close_wrap_tag),
                abstract.replace('OPEN_CNX_WRAP_TAG',open_wrap_tag).replace('CLOSE_CNX_WRAP_TAG',close_wrap_tag))

    security.declarePublic('wrapAbstract')
    def wrapBodyText(self, terms, open_wrap_tag='<b>', close_wrap_tag='</b>'):
        """Wrap matches to list of terms with tags. Returns tuple of (excerpt,fulltext)"""
        q = '&'.join(terms)
        res=self.portal_moduledb.sqlWrapText(text=self.bareText(), query=q, 
                             open_wrap_tag=open_wrap_tag, close_wrap_tag=close_wrap_tag)
        return (res[0].headline,res[0].fulltext)

    security.declarePublic('portal_type')
    portal_type = ComputedAttribute(lambda self: self._getDBProperty('portal_type'), 1)
    # FIXME: COMMENTED until such time as we want to have a different portal_type for ModuleView
    # see also Install.py
    #portal_type = ComputedAttribute(lambda self: "Published%s" % self._getDBProperty('portal_type'), 1)

    security.declarePublic('name')
    name = ComputedAttribute(lambda self: self._getDBProperty('name'), 1)
    title = name

    security.declarePublic('version')
    version = ComputedAttribute(lambda self: self._getDBProperty('version'), 1)

    security.declarePublic('doctype')
    doctype = ComputedAttribute(lambda self: self._getDBProperty('doctype'), 1)

    security.declarePublic('abstract')
    abstract = ComputedAttribute(lambda self: self._getDBProperty('abstract'), 1)

    security.declarePublic('license')
    license = ComputedAttribute(lambda self: self._getDBProperty('license'), 1)

    security.declarePublic('created')
    created = ComputedAttribute(lambda self: self._getDBProperty('created'), 1)

    security.declarePublic('revised')
    revised = ComputedAttribute(lambda self: self._getDBProperty('revised'), 1)

    security.declarePrivate('ident')
    ident = ComputedAttribute(lambda self: self._getDBProperty('ident'), 1)

    security.declarePublic('keywords')
    keywords = ComputedAttribute(getKeywords, 1)

    security.declarePublic('authors')
    authors = ComputedAttribute(lambda self: self._getDBProperty('authors'), 1)

    security.declarePublic('parentAuthors')
    parentAuthors = ComputedAttribute(lambda self: self._getDBProperty('parentAuthors'), 1)

    security.declarePublic('maintainers')
    maintainers = ComputedAttribute(lambda self: self._getDBProperty('maintainers'), 1)

    security.declarePublic('licensors')
    licensors = ComputedAttribute(lambda self: self._getDBProperty('licensors'), 1)

    security.declarePublic('submitter')
    submitter = ComputedAttribute(lambda self: self._getDBProperty('submitter'), 1)

    security.declarePublic('_links')
    _links = ComputedAttribute(lambda self: self.getContextLinks(), 1)

    security.declarePublic('language')
    language = ComputedAttribute(lambda self: self._getDBProperty('language'), 1)

    security.declarePublic('subject')
    subject = ComputedAttribute(lambda self: self._getDBProperty('subject'), 1)
    
    security.declarePublic('roles')
    roles = ComputedAttribute(lambda self: self._getDBProperty('roles'), 1)
    
    # collection attributes, which don't matter here, but set to make sure the catalog doesn't pick something else up
    # FIXME: a more general way to do this (probably defining all index/metadata names on the Repository object) when
    # types become more flexible.
    code = None
    collectionType = None
    institution = None
    instructor = None

    security.declarePrivate('getFile')
    def getFile(self, name):
        """Retrieve a module file from DB"""
        db_str = getattr(self,self.portal_moduledb.db).connection_string
        
        mf = ModuleFile(modid=self.objectId,version=self.version,name=name,db_connect=db_str,parent=self)
        try:
            # for when file is fetched on its own, we want to say some things about it;
            # we certainly don't want to over-ride the callers' response settings.
            response = self.REQUEST.RESPONSE
            if not response.headers.has_key('content-length'):
                response.setHeader('Content-Length', len(mf))
            content_type = mf.content_type()
            if content_type and not response.headers.has_key('content-type'):
                response.setHeader('Content-Type', content_type)
            if not response.headers.has_key('last-modified'):
                self._setLastModHeader()
        except AttributeError:
                pass
        return mf

        
    security.declarePrivate('getFileSize')
    def getFileSize(self, name):
        """Retrieve a module file size from DB"""
        res = self.portal_moduledb.sqlGetModuleFileSize(id=self.objectId,version=self.version,filename=name)

        if len(res) == 1:
            filesize = res[0][0]
            return filesize
        else:
           raise KeyError, "No such file %s/%s/%s" % (self.objectId,self.version,name)
        
    security.declarePrivate('getDoctype')
    def getDoctype(self):
        """Get module's document type"""
        return self._getDBProperty('doctype')


    security.declarePublic('getContextLinks')
    def getContextLinks(self, context=None):
        """Return a list of links for this module"""
        if context:
            # Assume context is the URL of a collection
            # FIXME: this isn't very robust...
            (scheme, netloc, path, params, query, fragment) = urlparse(context)
            portal_url = getToolByName(self, 'portal_url')
            portal_path = portal_url.getPortalPath()
            # if path includes portal path strip it out
            if path.startswith(portal_path):
                path = path[len(portal_path):]
            # Strip off the leading slash so the traversal will be done
            # from portal root, not Zope root
            if path.startswith('/'):
                path = path[1:]
            course = portal_url.getPortalObject().restrictedTraverse(path)
            lm_links = course.getContainedObject(self.objectId).getLinks()
        else:
            lm_links = self.getLinks()

        links = [{'url':l.target,
                  'title':l.title,
                  'type':l.category,
                  'strength': l.strength} for l in lm_links]
        return links

    security.declarePublic('getLinks')
    def getLinks(self):
        """Return a list of links for this module"""
        # Get versioned URL relative to root
        urltool = getToolByName(self, 'portal_url')
        source = '/'.join(('',) + urltool.getRelativeContentPath(self)[:-1] + (self.version, ''))  # '/content/m9000/2.34/'
        return self.portal_linkmap.searchLinks(source)
        
    security.declarePublic('getParent')
    def getParent(self):
        id = self._getDBProperty('parent_id')
        version = self._getDBProperty('parent_version')
        if id:
            return self.getRhaptosObject(id, version)
        
    security.declarePrivate('getVersion')
    def getVersion(self):
        """Return version string or None if version is 'latest'"""
        if self.id == 'latest':
            return None
        else:
            return self.id

                
    security.declarePublic('source')
    def source(self):
        """Get module source"""
        self.REQUEST.RESPONSE.setHeader('Content-Type', "application/xml")
        self._setLastModHeader()
        if self.REQUEST.REQUEST_METHOD == 'HEAD': return 
        return self.normalize()


    security.declarePrivate('default')
    def default(self):
        """Make render() the default method for viewing ZRhaptosModules"""
        REQUEST = self.REQUEST
        if REQUEST.get('format','') == 'pdf':
            self._setLastModHeader()
            if REQUEST.REQUEST_METHOD == 'HEAD':
                return  # HEAD short-circuiting
            elif self.id == 'latest':  # Redirect to specific version: 302 since it'll change w/ each publish
                path = self.REQUEST.URL2 + '/' + self.version 
                path = path + '/?' + self.REQUEST.QUERY_STRING
                self.REQUEST.RESPONSE.redirect(path, status=302)
                return
            if self.testIfModSince():
                #True is 'not modified'
                REQUEST.RESPONSE.setStatus(304)
                return
            return self.downloadPDF()
        else:
            return self.module_render()

    security.declarePrivate('testIfModSince')
    def testIfModSince(self):
        """Test if the current REQUEST has an 'If-Modified-Since' header, and if so, test it. 
        Returns True for 'not modified'. False means either 'was modified' or 'no header'"""
        
        ifmodsince = self.REQUEST.get_header('If-Modified-Since', None)
        try:
            if ifmodsince:
                ifmodsince = DateTime(ifmodsince)
        except DTSyntaxError:
            ifmodsince = None # bad date, just ignore, per spec. See also Zope's OFS/Image.py

        # short circuit for if-modified-since: spec recommends clients send value from 
        # previous Modified header, so the = case could be significant
        return bool (ifmodsince and self.revised <= ifmodsince)

    def HEAD(self, REQUEST, RESPONSE):
        """Retrieve resource information without a response body."""
        SimpleItem.HEAD(self, REQUEST, RESPONSE)
        if self.REQUEST.get('format','') == 'pdf':
            self._setLastModHeader()

    security.declarePublic('normalize')
    def normalize(self):
        """Get modules's normalized source"""
        return self.getDefaultFile().normalize()


    security.declarePrivate('downloadPDF')
    def downloadPDF(self):
        """Returns a PDF version of the module
        Checks for status in RhaptosPrintTool.  If it is 'failed', method returns
        if it is succeeded, tries to get PDF from RhaptosPrintTool.
        If is not there, the PDF is generated and added to RhaptosPrintTool
        
        Returns:
            PDF file or nothing
        """
        data = None
        fs_tool = getToolByName(self, 'portal_fsimport')
        printTool = getToolByName(self,'rhaptos_print')
        printStatus = printTool.getStatus(self.objectId, self.version, 'pdf')
        if printStatus == 'failed':
            return
        else:
            if printStatus != None and printStatus != '':
                data = printTool.getFile(self.objectId, self.version, 'pdf')
            if data == None and printStatus != 'locked':
                wd = tempfile.mkdtemp()
                export = self.module_export_cnxml()
                export_file = open(os.path.join(wd, 'export.cnxml'), 'wb')
                if type(export) is unicode:
                    export_file.write(export.encode('utf-8'))
                else:
                    export_file.write(export)
                export_file.close()
        
                files = self.objectIds()
                for fname in files:
                #FIXME should be someway to offload the file-from-db-to-filesystem
                    export = self.getFile(fname)
                    export_file = open(os.path.join(wd, fname), 'wb')
                    export_file.write(str(export))
                    export_file.close()
                
                pdf_tool = getToolByName(self, 'portal_pdflatex')
        
                params = {}
        
                data = pdf_tool.convertFSDirToPDF(wd, 'export.cnxml', **params)
                printTool.setFile( self.objectId,  self.version,'pdf',data)
                printTool.setStatus( self.objectId,  self.version,'pdf','succeeded')
        
                shutil.rmtree(wd)

        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s.pdf' % self.objectId) 

        return data


    security.declarePublic('checkout')
    def checkout(self, container):
        """Checkout a copy of the module"""

        files = self.objectIds()
        for fname in files:
            self._createFile(fname,self.getFile(fname).read(), container)

    def _createFile(self, name, body, container):
        """Create a file from a name and bits into the specified ZODB container"""

        typ, encoding = mimetypes.guess_type(name)

        #registry = getToolByName(self, 'content_type_registry')
        #if not registry:
        #    portal_type = 'File'
        #portal_type = registry.findTypeName(name, typ, body) or 'File'
        if name == self.getDefaultFilename():
            portal_type = "CNXML Document"
        else:
            portal_type = 'UnifiedFile'

        content = getattr(container, name, None)
        if not content:
            getToolByName(self, 'portal_types').constructContent(portal_type, container, name, file=body)
        else:
            # we may have existing index.cnxmls, for example
            content.update_data(body)


    security.declarePublic('getDefaultFilename')
    def getDefaultFilename(self):
        """Return filename used in the default 'view' of this module"""
        return 'index.cnxml'

    security.declarePublic('getDefaultFile')
    def getDefaultFile(self):
        """Return the file object used in the default 'view' of this module"""
        name = self.getDefaultFilename()
        content = self.getFile(name).read()
        portal_type = CNXMLFile
        f = portal_type(name, '', content, None, 'text/xml').__of__(self)
        return f

    security.declarePublic('SearchableText')
    def SearchableText(self):
        """Return the text of the module for searching"""
        content = self.getDefaultFile().getSource()
        bare = XMLService.transform(content,baretext)
        return bare

    security.declarePublic('objectIds')
    def objectIds(self):
        """Return the list of files in this module"""
        res = self.portal_moduledb.sqlGetModuleFilenames(id=self.objectId,version=self.version)
        if res:
            files = [r['filename'] for r in res]
        else:
            files = []
        return files


    security.declarePublic('getAboutActions')
    def getAboutActions(self):
        return [{'id':'module_render', 'url':'.', 'name':'View'},
                {'id':'about', 'url':'about', 'name':'About'},
                {'id':'history', 'url':'history', 'name':'History'},
                {'id':'print', 'url':'?format=pdf', 'name':'Print'}]

    security.declarePublic('rating')
    def rating(self):       
        # xxx: it seems impossibly difficult to just delegate to the wrapped
        # object.
        res = self.portal_moduledb.sqlGetRating(moduleid=self.objectId, version=self.version)
        if not res:
            return 0.0
        totalrating = res[0].totalrating
        votes = res[0].votes
        if votes == 0:
            return 0.0
        return round(totalrating * 1.0 / votes,1)

    security.declarePublic('numberOfRatings')
    def numberOfRatings(self):       
        # xxx: it seems impossibly difficult to just delegate to the wrapped
        # object.
        res = self.portal_moduledb.sqlGetRating(moduleid=self.objectId, version=self.version)
        if not res:
            return 0
        return res[0].votes

    # ---- Local role manipulations to allow group memners access

    security.declarePrivate('_getLocalRoles')
    def _getLocalRoles(self):
        """Query the database for the local roles in this workgroup"""
        # Give all maintainers the 'Maintainer' role
        dict = {}
        for m in self.maintainers:
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

    # Compatibility with CMF
    security.declarePublic('getIcon')
    def getIcon(self, *args):
        """CMF Combatibility method"""
        return self.icon

    # Set default roles for these permissions
    security.setPermissionDefault('Edit Rhaptos Object', ('Manager', 'Owner','Maintainer'))

InitializeClass(ModuleView)
