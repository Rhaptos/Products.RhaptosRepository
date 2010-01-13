## Script (Python) "expanded_browse_titles_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# organize results data for expanded title view
# hopefully to turn into a Zope 3 view.

request = context.REQUEST
content = context.portal_url.getPortalObject().content
searchhash = context.expanded_searchhash(request.form)

letter = request.get('letter', 'A')
sqlletter = letter == 'Other' and '[^A-Z]' or letter
sorton = request.get('sorton', 'title')
recent = request.get('recent', False)
request.set('sorton', sorton)
request.set('recent', recent)
cached_results = content.cache.resultsCacheLookup(searchhash,sorton,recent)

if cached_results is None:
    raw_results = context.getTitleByFirstChar(firstletter=sqlletter)
    results = sorton != 'title' and content.sortSearchResults(list(raw_results),sorton,recent) or raw_results
    content.cache.resultsCacheInject(searchhash, (results, {}, sorton, recent))
else:
    results = cached_results[0]

retvals = {}
retvals['searchhash'] = searchhash
retvals['results'] = results
retvals['letter'] = letter
return retvals
