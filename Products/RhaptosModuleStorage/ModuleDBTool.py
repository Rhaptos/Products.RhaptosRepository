"""
ModuleDBTool.py

Provide checkin/checkout support between ModuleDB repository and ZODB

Authors: Brent Hendricks, Ross Reedstrom
(C) 2005-2010 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import os
import re
import md5
from psycopg2 import Binary
import zLOG
import AccessControl
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import View, ManagePortal

from interfaces.portal_moduledb import portal_moduledb as IModuleDBTool
from ZSQLFile import ZSQLFile

class CommitError(StandardError):
    """An error occurred while attempting to commit a version store"""

class ModuleDBTool(UniqueObject, SimpleItem):
    """Provide access to data stored in SQL for objects stored with RhaptosModuleStorage"""


    __implements__ = (IModuleDBTool)

    id = 'portal_moduledb'
    meta_type = 'Module DB Tool'
    security = AccessControl.ClassSecurityInfo()

    sqlModuleExists = ZSQLFile('sql/moduleExists', globals(), __name__='sqlModuleExists')
    sqlCountModules = ZSQLFile('sql/countModules', globals(), __name__='sqlCountModules')
    sqlGetModulesByAuthors = ZSQLFile('sql/getModulesByAuthors', globals(), __name__='sqlGetModulesByAuthors')
    sqlGetModulesByRole = ZSQLFile('sql/getModulesByRole', globals(), __name__='sqlGetModulesByRole')
    sqlGetModulesByKeyword = ZSQLFile('sql/getModulesByKeyword', globals(), __name__='sqlGetModulesByKeyword')
    sqlGetModulesByTitle = ZSQLFile('sql/getModulesByTitle', globals(), __name__='sqlGetModulesByTitle')
    sqlGetModulesByLanguage = ZSQLFile('sql/getModulesByLanguage', globals(), __name__='sqlGetModulesByLanguage')
    sqlInsertFTIWords = ZSQLFile('sql/insertFTIWords', globals(), __name__='sqlInsertFTIWords')
    sqlGetPeoplebyName = ZSQLFile('sql/getPeoplebyName', globals(), __name__='sqlGetPeoplebyName')
    sqlDeleteModule = ZSQLFile('sql/deleteModule', globals(), __name__='sqlDeleteModule')
    sqlGetModule = ZSQLFile('sql/getModule', globals(), __name__='sqlGetModule')
    sqlGetModules = ZSQLFile('sql/getModules', globals(), __name__='sqlGetModules')
    sqlGetLatestModule = ZSQLFile('sql/getLatestModule', globals(), __name__='sqlGetLatestModule')
    sqlGetNewestModules = ZSQLFile('sql/getNewestModules', globals(), __name__='sqlGetNewestModule')
    sqlGetKeywords = ZSQLFile('sql/getKeywords', globals(), __name__='sqlGetKeywords')
    sqlGetHistory = ZSQLFile('sql/getHistory', globals(), __name__='sqlGetHistory')
    sqlGetNextModuleId = ZSQLFile('sql/getNextModuleId', globals(), __name__='sqlGetNextModuleId')
    sqlInsertNewVersion = ZSQLFile('sql/insertNewVersion', globals(), __name__='sqlInsertNewVersion')
    sqlGetAbstractID = ZSQLFile('sql/getAbstractID', globals(), __name__=='sqlGetAbstractID')
    sqlInsertAbstract = ZSQLFile('sql/insertAbstract', globals(), __name__='sqlInsertAbstract')
    sqlGetKeywordID = ZSQLFile('sql/getKeywordID', globals(), __name__=='sqlGetKeywordID')
    sqlInsertKeyword = ZSQLFile('sql/insertKeyword', globals(), __name__='sqlInsertKeyword')
    sqlInsertModuleKeyword = ZSQLFile('sql/insertKeywords', globals(), __name__='sqlInsertModuleKeyword')
    sqlInsertModuleOptionalRole = ZSQLFile('sql/insertOptionalRoles', globals(), __name__='sqlInsertModuleOptionalRole')
    sqlGetLicense = ZSQLFile('sql/getLicense', globals(), __name__='sqlGetLicense')
    sqlGetTags = ZSQLFile('sql/getTags', globals(), __name__='sqlGetTags')
    sqlSearchModules = ZSQLFile('sql/searchModules', globals(), __name__='sqlSearchModules')
    sqlSearchModulesByDate = ZSQLFile('sql/searchModulesByDate', globals(), __name__='sqlSearchModulesByDate')
    sqlGetKeywordByFirstChar = ZSQLFile('sql/getKeywordByFirstChar', globals(), __name__='sqlGetKeywordByFirstChar')
    sqlGetLanguageCounts = ZSQLFile('sql/getLanguages', globals(), __name__='sqlGetLanguageCounts')
    sqlWrapAbstract = ZSQLFile('sql/wrapAbstract', globals(), __name__='sqlWrapAbstract')
    sqlWrapText = ZSQLFile('sql/wrapText', globals(), __name__='sqlWrapText')
    sqlInsertModuleTag = ZSQLFile('sql/insertTag', globals(), __name__='sqlInsertModuleTag')
    sqlRegisterRating = ZSQLFile('sql/registerRating', globals(), __name__='sqlRegisterRating')
    sqlDeregisterRating = ZSQLFile('sql/deregisterRating', globals(), __name__='sqlDeregisterRating')
    sqlGetRating = ZSQLFile('sql/getRating', globals(), __name__='sqlGetRating')
    sqlGetModuleFile = ZSQLFile('sql/getModuleFile', globals(), __name__='sqlGetModuleFile')
    sqlGetModuleFileSize = ZSQLFile('sql/getModuleFileSize', globals(), __name__='sqlGetModuleFileSize')
    sqlGetModuleFilenames = ZSQLFile('sql/getModuleFilenames', globals(), __name__='sqlGetModuleFilenames')
    sqlGetFileByMd5 = ZSQLFile('sql/getFileByMd5', globals(), __name__='sqlGetFileByMd5')
    sqlInsertFile = ZSQLFile('sql/insertFile', globals(), __name__='sqlInsertFile')
    sqlInsertModuleFile = ZSQLFile('sql/insertModuleFile', globals(), __name__='sqlInsertModuleFile')

    # Member-data functions
    sqlGetAuthorByFirstChar = ZSQLFile('sql/getAuthorByFirstChar', globals(), __name__='sqlGetAuthorByFirstChar')
    sqlInsertMember = ZSQLFile('sql/insertMemberData', globals(), __name__='sqlInsertMember')
    sqlUpdateMember = ZSQLFile('sql/updateMemberData', globals(), __name__='sqlUpdateMember')

    ##   ZMI methods
    manage_options=(( {'label':'Overview', 'action':'manage_overview'},
                      {'label':'Configure', 'action':'manage_moduledb_properties'},
                      ) + SimpleItem.manage_options
                    )

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('zpt/explainModuleDBTool', globals() )

    security.declareProtected(ManagePortal, 'manage_moduledb_properties')
    manage_moduledb_properties = PageTemplateFile('zpt/editModuleDBTool', globals() )

    def __init__(self, db=None):
        self.db = db

    security.declareProtected(ManagePortal, 'setDB')
    def setDB(self, db):
        self.db = db

    security.declareProtected(ManagePortal, 'manage_editModuleDBTool')
    def manage_editModuleDBTool(self, connection, REQUEST=None):
        """Edit the ModuleDBTool parameters"""

        self.db = connection

        if REQUEST:
            return self.manage_moduledb_properties(manage_tabs_message="ModuleDBTool updated")

    security.declarePublic('getLicenseData')
    def getLicenseData(self, url):
        """
        Get all the information about a given license from the database table.
        Returns a dictionary with keys: code, label, name, url, and version.
        Examples of code, label, and version: 'by', 'CC-BY 3.0', '3.0'.
        """
        # FIXME: not the best place for this; should be somewhere in RhaptosContent probably
        licensedata = self.sqlGetLicense(url=url)[0]
        licensedict = {}
        for f in ['code', 'label', 'name', 'url', 'version']:
            licensedict[f] = licensedata[f]
        return licensedict

    def insertModuleVersion(self, object):
        """Insert new module version into the database"""

        # Get ID of (possibly new) abstract
        abstractId = self._getAbstractID(object.abstract)

        # Get ID of license
        try:
            licenseId = self.sqlGetLicense(url=object.license)[0].licenseid
        except IndexError:
            raise CommitError, "Unknown license: %s" % object.license

        # Set state to 'submitted'
        stateId = 1

        # Put new version of module into the DB
        parentObj = object.getParent()
        parent = parentObj and parentObj.ident or None
        self.sqlInsertNewVersion(moduleid=object.objectId,
                                 portal_type=object.portal_type,
                                 version=object.version,
                                 name=object.title,
                                 created=object.created.HTML4(),
                                 authors=object.authors,
                                 maintainers=object.maintainers,
                                 licensors=object.licensors,
                                 parentauthors=object.parentAuthors,
                                 abstractid=abstractId, stateid=stateId, licenseid=licenseId,
                                 doctype=getattr(object, 'doctype', ''),  # 0.6 loses doctype attr
                                 submitter=object.submitter,
                                 submitlog=object.submitlog,
                                 parent=parent, language=object.language)

        # Put the file objects in the files table
        for fob in object.objectValues():
            if hasattr(fob,'data'): #It's a file object
                fid = self._getFileID(fob)
                self.sqlInsertModuleFile(moduleid=object.objectId, version=object.version, fileid=fid, filename=fob.id,mimetype=fob.content_type)

        # Put non-blank keywords into module-keyword table
        for word in [' '.join(w.strip().split()) for w in object.keywords if w.strip()]:
            keywordId = self._getKeywordID(word)
            self.sqlInsertModuleKeyword(moduleid=object.objectId, version=object.version, keywordid=keywordId)

        #Insert optional roles, if any
        for role in object.optional_roles.keys():
            value = getattr(object,role.lower()+'s',None)
            if value:
                self.sqlInsertModuleOptionalRole(moduleid=object.objectId, version=object.version,rolename=role,persons=value)

        if type(object.subject) == type(''):
            self.sqlInsertModuleTag(moduleid=object.objectId, version=object.version,tag=object.subject)
        else:
            for subj in object.subject:
                self.sqlInsertModuleTag(moduleid=object.objectId, version=object.version,tag=subj)

        # Put fulltext index words in place
        if object.SearchableText():
            self.sqlInsertFTIWords(moduleid=object.objectId, version=object.version, modulecontents=object.SearchableText())

    def _getAbstractID(self, abstract):
        """Return a unique (possibly new) ID for abstract text"""

        result = self.sqlGetAbstractID(abstract=abstract)
        if not len(result): # If the abstract doesn't already exist, insert it
            self.sqlInsertAbstract(abstract=abstract)
            result = self.sqlGetAbstractID(abstract=abstract)
        return result[0].id

    def _getKeywordID(self, word):
        """Return a unique (possibly new) ID for keyword"""
        result = self.sqlGetKeywordID(word=word)
        if not len(result): # If the keyword doesn't already exist, insert it
            self.sqlInsertKeyword(word=word)
            result = self.sqlGetKeywordID(word=word)
        return result[0].id

    def _getFileID(self,fileob):
        """Return the fileid for a file, stored in the DB"""
        m=md5.new(fileob.data).hexdigest()
        res = self.sqlGetFileByMd5(md5=m)
        for r in res:
            if r.file == fileob.data:
                return r.fileid
        res = self.sqlInsertFile(file = Binary(fileob.data))
        return res[0].fileid

InitializeClass(ModuleDBTool)
