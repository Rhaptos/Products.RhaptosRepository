from zope.interface import Attribute, Interface

################################################################
# IVersionFolder Interface
################################################################

class IVersionFolder(Interface):
    """
    Interface for version container in the repository
    """

    latest = Attribute('latest', 'The latest revision of this object.  Must implement the IVersionedObject interface')
    
    def url():
        """Return the URL to access the last version of the object"""

    def createVersion(object, submitter, submitlog):
        """Commit a new version of the object to the repository

           object      : the new object
           submitter   : the user creating the new version
           submitlog   : a string describing the changes
        """

    def getHistory():
        """Return the version history of the object as a list.  Each item in the list will implement the **** interface"""
