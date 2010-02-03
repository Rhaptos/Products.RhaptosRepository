## Script (Python) "expanded_searchhash"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=qs
##title=
##
# Create a parameter string from query string for expanded_browse_ pages. Drops values for b_start/b_size.
# With template id should be unique hash key.

# we might do this with make_query, but order might change, leading to less cache efficiency

omit = ('b_size', 'b_start', 'cachekey', 'view_mode', 'sorton', 'recent', 'filename','template')

# reformat with 'omit's missing
from ZTUtils import url_query
newurl = url_query(context.REQUEST, omit=omit)

# strip host
newurlparts = newurl.split('/')
newurl = '/'.join(newurlparts[3:])

return newurl
