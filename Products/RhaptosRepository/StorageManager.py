"""
Manager for pluggable version control storage implementations

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from zope.interface import implements

import AccessControl
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Globals import InitializeClass

from interfaces.IVersionStorage import IStorageManager, IVersionStorage

class StorageManager(BTreeFolder2):
    """Implementation of IStorageManager"""

    implements(IStorageManager)

    
    def __init__(self, id):
        BTreeFolder2.__init__(self, id)
        self._default_storage = None
        self._storage_map = {}
        self._all_storages = []

    def registerStorage(self, storage):
        """
        Register a storage implementation.

        storage: a persistent object implementing IVersionStorage

        raises TypeError if storage does not implement IVersionStorage
        raises ValueError if storage already registered
        """
        if not IVersionStorage.isImplementedBy(storage):
            raise TypeError, "Storage must implement IVersionStorage"""

        id = storage.getId()
        if self.hasObject(id):
            raise ValueError, "Object with ID %s already exists" % id
            
        self._setObject(id, storage)
        self._all_storages.append(id)

    def getStorage(self, id):
        """
        Return the specified storage implementation.

        Raises KeyError if there is no storage registered with the provided ID
        """
        try:
            return getattr(self, id)
        except AttributeError:
            raise KeyError, "No such storage %s" % id


    def removeStorage(self, id):
        """
        Remove a storage implementation.

        Raises KeyError if there is no storage registered with the provided ID
        """

        # If this is the default remove it
        if self._default_storage == id:
            self._default_storage = None
        
        self._delObject(id)
        self._all_storages.remove(id)
        
    def listStorages(self):
        """
        Return a list of the IDs of registered storage implementations.
        """
        return self._all_storages

    def setDefaultStorage(self, id):
        """
        Set the default storage to be used when a specific storage is
        not set for a given portal_type

        id: the ID of the default storage or None to set no default

        Raises KeyError if there is no storage registered with the provided ID
        """
        if id is not None and not self.hasObject(id):
            raise KeyError, "No such storage %s" % id
        self._default_storage = id

    def getDefaultStorage(self):
        """
        Return default storage implementation object or None if there
        isn't one currently set
        """
        default = self._default_storage
        if default is not None:
            default = self.getStorage(default)
        return default
        
    def setStorageForType(self, portal_type, id):
        """
        Set the storage to be used for objects of 'portal_type'

        If ID is None, set to default storage

        Raises KeyError if there is no storage registered with the provided ID
        """
        if id is not None and not self.hasObject(id):
            raise KeyError, "No such storage %s" % id
        self._storage_map[portal_type] = id
        self._p_changed = 1

    def getStorageForType(self, portal_type):
        """
        Return the storage implementation object used for the specified portal_type.
        """

        id = self._storage_map.get(portal_type, self._default_storage)
        if id is not None:
            try:
                return self.getStorage(id)
            except KeyError:
                # Current selected storage is invalid.  We'll leave it
                # as is in case it becomes valid later.  In the
                # meantime, we'll return the default storage
                return self.getDefaultStorage()

InitializeClass(StorageManager)
