## Script (Python) "expanded_browse_popularity_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# organize results data for expanded popularity view
# hopefully to turn into a Zope 3 view.

request = context.REQUEST
content = context.portal_url.getPortalObject().content
searchhash = context.expanded_searchhash(request.form)

sorton = request.get('sorton', 'popularity')
recent = request.get('recent', False)
request.set('sorton',sorton)
request.set('recent',recent)

param_string = recent and 'weekly' or 'alltime'
headerfragment  = {'weekly': 'Last Week', 'alltime': 'Complete History'}[param_string]

cached_results = content.cache.resultsCacheLookup(searchhash,sorton,recent)

if cached_results is None:  # todo: cache and/or invalidate-based-on actual data range
    stats = context.portal_hitcount.getDailyAverages(recent)
    if stats:
        raw_results = context.getObjectResultsForIds(stats)
        results = sorton!='popularity' and content.sortSearchResults(list(raw_results),sorton,recent) or raw_results
        content.cache.resultsCacheInject(searchhash, (results, {}, sorton, recent))
    else:
        results = []
else:
    results=cached_results[0]

retvals = {}
retvals['searchhash'] = searchhash
retvals['results'] = results
retvals['recent'] = recent
retvals['headerfragment'] = headerfragment
retvals['param_string'] = param_string
return retvals
