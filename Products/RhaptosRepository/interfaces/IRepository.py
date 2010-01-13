from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


class IRepository(Interface):
    """
    Interface for the Rhaptos version repository
    """

    def getRhaptosObject(id, version=None):
        """Returns the object with the specified ID and version

        If a version is specified, the returned object will support
        the IVersionedObject interface, otherwise it will support
        the IVersionFolder interface.
        
        If there is no such object, it will raise a KeyError
        """

    def publishObject(object, message):
        """
        Publish an object for the first time in the repository
        
        object: the object to place under version control.  It must
        implement IMetadata.
        message: a string log message by the user
           
        returns: unique ID string for the new object
        """

    def publishRevision(object, message):
        """
        Publish a revision of an object in the repository
        
        object: the object to place under version control.  It must
        implement IMetadata and IVersionedObject
        message: a string log message by the user

        raises CommitError if object is not already under version control
        """

    def searchRepository():
        """Search the repository for content

        Accepts parameters via the REQUEST object:

        words: search string
        similar: If set to 'yes', assume the search string is a
                 content ID and search for similar content

        """
        
