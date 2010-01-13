## Script (Python) "getTitleByFirstChar"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=x,y
##title=
##

return cmp(context.stripArticles(x.Title).lower(),context.stripArticles(y.Title).lower())
