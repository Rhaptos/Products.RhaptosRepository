from zope.interface import Interface, Attribute


class IVersionStorage(Interface):
    """
    Interface for pluggable version control storage implementation
    """

    def getId():
        """
        Return the storage's identifier
        """
    
    def generateId():
        """
        Return a unique identifier
        """

    # -- Parts borrowed from IVersionControl
    
    def isUnderVersionControl(object):
        """
        Return True if the given object is under version control
        """

    def applyVersionControl(object):
        """
        Place the object under version control

        Returns a unique identifier associated with this object's
        version history
        """

    def isResourceUpToDate(object):
        """
        Return True if the object is the most recently checked in version
        """    

    def getVersionInfo(object):
        """
        Get version storage information about the object.

        Returns an object implementing IVersionInfo or None if the
        object is not under version control.
        """
        
    def checkinResource(object, message='', user=None):
        """
        Checkin a new version of an object to the repository

        object  : the new object
        message : a string describing the changes
        user    : the name of the user creating the new version
        """

    # FIXME: [un]checkoutResource, updateResource?
        
    # -- Other methods --

    def hasObject(id):
        """
        Return True if an object with the specified ID exists
        """

    def getObject(id, version=None):
        """
        Return the object with the specified ID and version

        If there is no such object, it will raise a KeyError
        """

    def getObjects(objects):
        """
        Return sequence of objects with specified ID and versions

        objects must be a list of (id, version) tuples
        """

    def deleteObject(id, version=None):
        """
        Delete the specified object from storage.

        If version is None, delete all versions of the object,
        otherwise delete only the specified version.

        Raises IntegrityError if the object cannot be deleted because
        it is referenced by other objects
        """

    def getHistory(id):
        """
        Return the version history of the object as a list.

        Each item in the list will implement the **** interface
        """

    def countObjects(portal_types=None):
        """
        Return the number of objects stored for the specified portal_types.

        If portal_types is None, return the total number of objects stored
        """

    def search(query, portal_types=None):
        """
        Search the storage
        """

    def searchDateRange(start, end):
        """
        Search for objects whose latest version is within the specified date range

        start and end must be DateTime objects
        """

    # FIXME: These are here for backward compatibility.  Do we need them?
    def createVersionFolder(object):
        """
        Create a new version folder instance inside the repository
        """

    def getVersionFolder(id):
        """
        Retrieve version folder instance for a specific ID
        """


class IStorageManager(Interface):
    """
    Interface for manging storage mechanisms
    """

    def registerStorage(storage):
        """
        Register a storage implementation.

        storage: a persistent object implementing IVersionStorage

        raises TypeError if storage does not implement IVersionStorage
        raises ValueError if storage already registered
        """

    def getStorage(id):
        """
        Return the specified storage implementation.

        Raises KeyError if there is no storage registered with the provided ID
        """

    def removeStorage(id):
        """
        Remove a storage implementation.

        Raises KeyError if there is no storage registered with the provided ID
        """
        
    def listStorages():
        """
        Return a list of the IDs of registered storage implementations.
        """

    def setDefaultStorage(id):
        """
        Set the default storage to be used when a specific storage is
        not set for a given portal_type

        id: the ID of the default storage or None to set no default

        Raises KeyError if there is no storage registered with the provided ID
        """

    def getDefaultStorage():
        """
        Return default storage implementation object or None if there
        isn't one currently set
        """
        
    def setStorageForType(portal_type, id):
        """
        Set the storage to be used for objects of 'portal_type'

        If ID is None, set to default storage

        Raises KeyError if there is no storage registered with the provided ID
        """

    def getStorageForType(portal_type):
        """
        Return the storage implementation object used for the specified portal_type.
        """

class IVersionInfo(Interface):
    """
    Interface for version information.
    """

    objectId = Attribute('objectId', "A ID string acting as a unique object identifier in the repository")

    version = Attribute('version', "A string representing this object's version")

    user = Attribute('user', "The name of the user who checked in this version of the object")

    message = Attribute('message', "Optional comment by the user who checked in the object")

    timestamp = Attribute('timestamp', "DateTime object indicating when the object was checked in")
