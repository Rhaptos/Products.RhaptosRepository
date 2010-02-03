## Script (Python) "getContentByKeyword"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=keyword
##title=
##

objects = context.catalog(keywords = keyword, sort_on='sortTitle')

return objects
