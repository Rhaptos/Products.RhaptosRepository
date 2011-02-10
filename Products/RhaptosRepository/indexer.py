from zope.interface import Interface
from plone.indexer.decorator import indexer

from Acquisition import aq_base

@indexer(Interface)
def keywords(obj):
    values = getattr(aq_base(obj), 'keywords', [])
    result = []
    for value in values:
        result.append(value.lower())
    return result

@indexer(Interface)
def baselanguage(obj):
    values = getattr(aq_base(obj), 'baselanguage', [])
    result = []
    for value in values:
        result.append(value.split('-')[0])
    return result

@indexer(Interface)
def sortTitle(obj):
    value = getattr(aq_base(obj), 'sortTitle', '')
    return obj.stripArticles(value.lower())

@indexer(Interface)
def parent(obj):
    value = obj.getParent() 
    return value.objectId

@indexer(Interface)
def translators(obj):
    return obj.roles['translators']

@indexer(Interface)
def editors(obj):
    return obj.roles['editors']
