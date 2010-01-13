# Script (Python) "expanded_browse_titles_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# organize results data for expanded keywords view
# hopefully to turn into a Zope 3 view.

request = context.REQUEST
content = context.portal_url.getPortalObject().content
searchhash = context.expanded_searchhash(request.form)
sorton = request.get('sorton', 'portal_type')
recent = request.get('recent', False)
request.set('sorton',sorton)
request.set('recent',recent)

cached_results = content.cache.resultsCacheLookup(searchhash,sorton,recent)

keyword = request.get('keyword')
first_letter = keyword[0]
base_letter = request.get('letter', first_letter)
sorton = request.get('sorton', 'portal_type')
recent = request.get('recent', False)

if cached_results is None:
    raw_results = context.getContentByKeyword(keyword)
    results = sorton != 'title' and context.content.sortSearchResults(list(raw_results),sorton,recent) or raw_results;
    content.cache.resultsCacheInject(searchhash, (results, {}, sorton, recent))
else:
    results = cached_results[0]

retvals = {}
retvals['searchhash'] = searchhash
retvals['results'] = results
retvals['keyword'] = keyword
retvals['base_letter'] = base_letter
return retvals
