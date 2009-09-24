## Script (Python) "search_form_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
objectId = REQUEST.get('objectId','')

if objectId:
    try:
        object = context.content.getRhaptosObject(objectId, 'latest')
    except KeyError:
        return []
            
started = DateTime().timeTime()
results = context.getObjectResultsForIds([(s[0],s[2]) for s in context.portal_similarity.getSimilarContent(object)])
REQUEST.set('time', '%.3f' % (DateTime().timeTime()-started))
REQUEST.set('matched_terms','')
REQUEST.set('ignored_terms','')
REQUEST.set('term_results', '')


return results
