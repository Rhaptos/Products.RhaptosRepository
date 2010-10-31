from zope.interface import Attribute, Interface

class IVersionedObject(Interface):
    """
    Interface for a specific version of an object in the repository
    """

    objectId = Attribute('objectId', 'The ID string of the object what this is a version of')

    version = Attribute('version', "A string representing this object's version")

    submitter = Attribute('submitter', "The username of the person who published this version of the object")

    submitlog = Attribute('submitlog', "The comment by the person who published this version of the object")

    def url():
        """Return the canonical URL used to access the object version"""

    def getParent():
        """Return the parent object from which this object derives, or None if no such object exists"""
