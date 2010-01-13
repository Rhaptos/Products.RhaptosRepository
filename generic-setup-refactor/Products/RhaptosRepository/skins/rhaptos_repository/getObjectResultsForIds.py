## Script (Python) "getObjectResultsForIds"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=[]
##title=
##

# If it is a id-weight tuple, pass in the weight
# otherwise, just pass in the id
from Products.RhaptosModuleStorage.Extensions.DBModule import DBModuleSearch


objs=[]
if same_type(ids[0],()):
    for o in ids:
        catres =context.content.catalog(objectId=o[0])
	if catres:
            ob = DBModuleSearch(catres[0],weight=o[1],matched={},fields={})
            objs.append(ob)
else:
    for o in ids:
        catres =context.content.catalog(objectId=o[0])
	if catres:
            ob = DBModuleSearch(catres[0],weight=0,matched={},fields={})
            objs.append(ob)
return objs
