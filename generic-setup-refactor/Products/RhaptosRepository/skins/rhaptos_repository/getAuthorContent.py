## Script (Python) "getAuthorContent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member, sortkey, reverse=False
##title=
##
from Products.AdvancedQuery import In, And, Not, Eq

results = {}
content = context.content.getContentByAuthor(member)
objectIds = [o.objectId for o in content]

eobjects = context.content.getContentByRole('editor',member)
eids = [o.objectId for o in eobjects]

tobjects = context.content.getContentByRole('translator',member)
tids = [o.objectId for o in tobjects]

for o in eobjects:
    if o.objectId not in objectIds:
        objectIds.append(o.objectId)
        content.append(o)
        
for o in tobjects:
    if o.objectId not in objectIds:
        objectIds.append(o.objectId)
        content.append(o)

for o in content:
    if o.objectId in eids:
        for e in eobjects:
            if e.objectId == o.objectId:
                #eob = eobjects.pop(eobjects.index(e))
                #eids.remove(e.objectId)
                o.fields.update(e.fields)
    if o.objectId in tids:
        for t in tobjects:
            if t.objectId == o.objectId:
                #tob = tobjects.pop(tobjects.index(t))
                #tids.remove(t.objectId)
                  # ... the above bit is probably supposed to be an optimization, but:
                  # doing a pop of the thing we're in is questionable, and
                  # the tobjects.index(t) fails in a mixed collection/module list,
                  # because mybrains don't like cmp against wrapped results
                o.fields.update(t.fields)
        
modules = [o for o in content if o.portal_type == 'Module']
forks = context.content.getContentByRole('parentAuthor', member)
moduleIds = [m.objectId for m in modules]
query = And( In('containedModuleIds', moduleIds), Not( Eq('authors', member)) )
containers = context.content.catalog.evalAdvancedQuery(query)

mobjects = context.content.getContentByRole('maintainer', member)
maintainerObjects = [m for m in mobjects if m.objectId not in objectIds]

#contrib_objects = [o for o in eobjects+tobjects if o.objectId not in objectIds]
#content.extend(contrib_objects)

results['content'] = content
results['containers'] = containers
results['forks'] = forks
results['m_content'] = maintainerObjects

for k,l in results.items():
    results[k] = list(l)
    results[k].sort(lambda x, y: cmp(getattr(x, sortkey), getattr(y, sortkey)))

if reverse:
    map(lambda x: x.reverse(), results.values())

return results
