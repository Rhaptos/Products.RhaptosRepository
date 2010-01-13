## Script (Python) "collections"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=  
##title= Return an RSS feed of collections, sorted by revision

context.REQUEST.set('portal_type','Collection')
return state
