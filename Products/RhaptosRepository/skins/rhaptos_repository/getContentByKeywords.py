## Script (Python) "getModulesByKeywords"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=keywords
##title=
##

objects = {}

for k in keywords:
    objects[k] = context.catalog(keywords = k, sort_on='sortTitle')

return objects
