"""
Initialize RhaptosRepository Product

Author: Brent Hendricks and Ross Reedstrom
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

# Monkeypatch on PloneLanguageTool
import languageConstants

#import Repository
#import VersionFolder
from Extensions.ObjectResult import ObjectResult
from Products.RhaptosModuleStorage.Extensions.DBModule import DBModuleSearch

from Products.CMFCore import utils, CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import setDefaultRoles

import sys
this_module = sys.modules[ __name__ ]

product_globals = globals()

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())

# Allow access to shlex for search parsing
from AccessControl import allow_module, allow_class
import shlex
allow_module('shlex')
allow_module('Products.RhaptosRepository.Extensions')
allow_module('Products.RhaptosRepository.Extensions.ObjectResult')
allow_class(ObjectResult)
allow_module('Products.RhaptosModuleStorage.Extensions')
allow_module('Products.RhaptosModuleStorage.Extensions.DBModule')
allow_class(DBModuleSearch)
"""
contentConstructors = (Repository.manage_addRepository,)
contentClasses = (Repository.Repository,)

z_bases = utils.initializeBasesPhase1(contentClasses, this_module)

def initialize(context):

    utils.initializeBasesPhase2( z_bases, context )
    utils.ContentInit(Repository.Repository.meta_type,
                      content_types = contentClasses,
                      permission = CMFCorePermissions.AddPortalContent,
                      extra_constructors = contentConstructors,
                      fti = Repository.factory_type_information).initialize(context)
    
    # register class for Copy Support (validaton fails if user can't 'add' it)
    context.registerClass(
        VersionFolder.VersionFolder,
        permission=CMFCorePermissions.AddPortalContent,
        constructors=(VersionFolder.manage_addVersionFolderForm,
                      VersionFolder.manage_addVersionFolder),
        icon='www/VersionFolder.gif',
    )
"""
