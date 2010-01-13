## Script (Python) "getTitleByFirstChar"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=firstletter
##title=
##

objects = context.catalog(sortTitle='^'+firstletter,sortTitle_match='regexp',sort_on='sortTitle')
#for o in objects:
#    o.fields={}
return objects
