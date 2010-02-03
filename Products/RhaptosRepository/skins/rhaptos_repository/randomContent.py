## Script (Python) "randomContent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=portal_type=None
##title= Redirect to a random content item
##

CUTOFF_FACTOR = 0.02

counts = context.portal_hitcount.getHitCounts()
if len(counts):
    cutoff = counts[0][1] * CUTOFF_FACTOR
    objects = [o[0] for o in counts if o[1] > cutoff]
    
    if len(objects) == 0:
        objects = [o[0] for o in counts]
    
    # Filter by portal_type
    # FIXME: Yuck.  Peeking at objectIds to determine portal_type is bad hack.
    if portal_type == 'Module':
        objects = [o for o in objects if o.startswith('m')]
    elif portal_type == 'Collection':
        objects = [o for o in objects if o.startswith('c')]

    if len(objects):
        objectId = random.choice(objects)
        return context.REQUEST.RESPONSE.redirect('%s/content/%s/latest/' % (context.portal_url(),objectId))
    else:
        return None
else: return None
