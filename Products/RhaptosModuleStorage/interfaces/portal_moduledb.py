# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# Written by Brent Hendricks

"""Interface for providing checkout/checkin between MODULEDB repository and ZODB"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_moduledb(Interface):
    """Encapsulate MODULEDB access"""

    id = Attribute('id','Must be set to "portal_moduledb"')

    def importObject(obj, message, version=None):
        """Import a new object into the MODULEDB repository"""

    def checkout(container, id, version=None):
        """Checkout MODULEDB working dir to the specified container"""

    def checkin(obj, message, version=None):
        """Submit changed files to repository"""

    def getFile(path, version=None):
        """Retrieve a file within a particular version of a module"""

    def getWorkingDir(path, version=None):
        """Checkout a module and return the working directory"""
