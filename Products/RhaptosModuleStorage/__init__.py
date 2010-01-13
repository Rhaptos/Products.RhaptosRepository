"""
Initialize RhaptosModuleStorage Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
import sys
from Products.CMFCore import utils
import ModuleDBTool
#import ModuleVersionFolder

this_module = sys.modules[ __name__ ]
product_globals = globals()
tools = ( ModuleDBTool.ModuleDBTool,)

def initialize(context):
    utils.ToolInit('Module DB Tool',
                    tools = tools,
                    icon='tool.gif' 
                    ).initialize( context )
