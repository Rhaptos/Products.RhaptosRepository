## Script (Python) "collection_popularity"
##title = truncate a string
##bind container = container
##bind context = context
##bind namespace=
##bind script = script
##bind subpath = traverse_subpath
##parameters =
c_hits={}
courses = context.catalog({'portal_type':'Collection'})
for c in courses:
    c_hits[c.objectId] = context.portal_hitcount.getHitCountForObject(c.objectId,0)
    mods = c.getObject().containedModuleIds()
    for m in mods:
        inc = context.portal_hitcount.getHitCountForObject(m,0)
        c_hits[c.objectId] = c_hits[c.objectId] + inc
    c_hits[c.objectId] = (c.Title,c_hits[c.objectId],(c_hits[c.objectId]*1.0)/(len(mods)+1))
clist=c_hits.items()
clist.sort(lambda x,y: cmp(y[1][1],x[1][1]))
return clist
    
