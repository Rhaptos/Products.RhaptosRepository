from zope.app.annotation.attribute import AttributeAnnotations
from BTrees.OOBTree import OOBTree

class Rateable(AttributeAnnotations):
    def __init__(self, obj):
        self.obj = obj
        if not self.has_key('ratings'):
            self['ratings'] = OOBTree()


    def rate(self, objectId, rating):
        self['ratings'][objectId] = rating

    def hasRating(self, objectId):
        return self['ratings'].has_key(objectId)

    def getRating(self, objectId):
        return self['ratings'][objectId]
