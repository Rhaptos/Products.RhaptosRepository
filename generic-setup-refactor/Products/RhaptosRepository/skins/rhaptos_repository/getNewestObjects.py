## Script (Python) "getNewestObjects"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=number=5, new=None, portal_type=None, sort_on='revised', sort_order='descending'
##title=
##
# Returns 'number' results for recent changes. Sort attributes are like for ZCatalog.
# The 'new' specifies all changes if None, only new content if True, and only revisions
# to existing content if False. Is this too tricksy?

num=int(number)

cat_query={'sort_on':'revised','sort_order':'descending'}
if portal_type:
    cat_query['portal_type']=portal_type
if num:
    # I don't really understand this; Kyle says it's a performance enhancement
    # but I need to understand the implications before doing anything to it.
    n=num
    objects = []
    last_size = 0
    while len(objects) < num:
        objects = []
        cat_query['sort_limit']=n
        objects = list(context.catalog(cat_query))[:n]
        if last_size == len(objects):
            # We must have tried all the objects
            num = 0
        else:
            last_size = len(objects)
        
        # this could probably stand to be factored out...
        if new is True:
            objects = [o for o in objects if o.getHistoryCount==1]
        elif new is False:
            objects = [o for o in objects if o.getHistoryCount > 1]
        n = n*2
else:
    objects = list(context.catalog(cat_query))
    if new is True:
        objects = [o for o in objects if o.getHistoryCount==1]
    elif new is False:
        objects = [o for o in objects if o.getHistoryCount > 1]

if int(number):
    return objects[:int(number)]
else:
    return objects
    
