## Script (Python) "expanded_query"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
# Create a URL aquery string for expanded_browse_ pages. Drops 0 values for b_start.

from ZTUtils import make_query

if kw.has_key('b_start') and not int(kw['b_start']): del kw['b_start']

return make_query(**kw)