## Script (Python) "getAuthorContent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sortkey
##title=
##
from ZTUtils import make_query

url = '/'.join([context.REQUEST.URL0] + context.REQUEST.get('traverse_subpath', []))
old_sortkey = context.REQUEST.get('sortkey', 'Title')
old_reverse = context.REQUEST.get('reverse', False)

if sortkey != old_sortkey:
    reverse = False
else:
    reverse = not old_reverse

return url + '?' + make_query(sortkey=sortkey, reverse=reverse)
