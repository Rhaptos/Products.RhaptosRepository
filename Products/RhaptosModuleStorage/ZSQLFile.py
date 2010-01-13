"""
ZSQLFile for RhaptosModuleStorage Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.ExtZSQL import ExtZSQLFactory
from OFS.SimpleItem import SimpleItem
from App.Common import package_home
import os.path

class ZSQLFile(SimpleItem):

    meta_type = "ZSQLFile"

    def __init__(self, path, _prefix=None, __name__=None):

        # Figure out where the file is
        if _prefix is None: _prefix=SOFTWARE_HOME
        elif type(_prefix) is not type(''):
            _prefix = package_home(_prefix)

        # Default to a reasonable name
        if not __name__:
            __name__=os.path.split(path)[-1]

        # Default to '.sql' extension
        if not os.path.splitext(path)[1]:
            path = path + '.sql'
        self.path = os.path.join(_prefix, path)

        self.id = __name__


    def __call__(self, aq_parent=None, **kw):
        factory = ExtZSQLFactory.getFactory(self.db)
        if not aq_parent:
            aq_parent = self.aq_parent
        func = factory.getStatement(self.path, aq_parent)
        return func(**kw)
