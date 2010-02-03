## Script (Python) "expanded_browse_date_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# organize results data for expanded date view
# hopefully to turn into a Zope 3 view.

request = context.REQUEST
content = context.portal_url.getPortalObject().content
searchhash = context.expanded_searchhash(request.form)
sorton = request.get('sorton', 'revised')
recent = request.get('recent', False)
request.set('sorton', sorton)
request.set('recent', recent)
cached_results = content.cache.resultsCacheLookup(searchhash,sorton,recent)

new_str = request.get('new', 'latest')
sorton = request.get('sorton', 'revised')
recent = request.get('recent', False)
headerdetail = {'latest': 'All Activity', 'new': 'New Content', 'revised': 'Content Revisions'}[new_str]

if cached_results is None:
    raw_results = context.pane_detail_date_results(new_str) #getNewestObjects(number=0, new=new_bool)
    results = sorton != 'revised' and content.sortSearchResults(list(raw_results),sorton) or raw_results
    content.cache.resultsCacheInject(searchhash, (results, {}, sorton, recent))
else:
    results = cached_results[0]

retvals = {}
retvals['searchhash'] = searchhash
retvals['results'] = results
retvals['headerdetail'] = headerdetail
retvals['new_str'] = new_str
return retvals
