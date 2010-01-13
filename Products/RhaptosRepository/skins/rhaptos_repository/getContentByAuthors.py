## Script (Python) "getContentByAuthors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=authors
##title=
##
from Products.AdvancedQuery import In, And, Not, Eq, Or

objects = {}
for author in authors:
    query = Or( In('authors',author), In('editors',author), In('translators',author))
    # From what I can tell this sorting isn't working correctly, but I don't think
    # it really matters... all this script is used for is to get the raw numbers.
    objects[author] = context.catalog.evalAdvancedQuery(query,('sortTitle',))

return objects
