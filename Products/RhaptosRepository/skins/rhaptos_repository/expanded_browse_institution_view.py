## Script (Python) "expanded_browse_institution_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# organize results data for expanded institution view
# hopefully to turn into a Zope 3 view.

request = context.REQUEST
content = context.portal_url.getPortalObject().content
searchhash = context.expanded_searchhash(request.form)
sorton = request.get('sorton', 'title')
recent = request.get('recent', False)
request.set('sorton',sorton)
request.set('recent',recent)

cached_results = content.cache.resultsCacheLookup(searchhash,sorton,recent)

inst = request.get('inst')
lookFor = inst != '-' and inst or ''
base_letter = request.get('letter', inst and inst[0] or 'Unspecified')

if cached_results is None:
    all_results = content.catalog(atomicInstitution=lookFor.decode('utf-8'),sort_on='sortTitle',portal_type='Collection')
    raw_results = (lookFor=='' and [o for o in all_results if o.institution=='']) or all_results
    results = sorton!='title' and content.sortSearchResults(list(raw_results),sorton,recent) or raw_results
    content.cache.resultsCacheInject(searchhash, (results, {}, sorton, recent))
else:
    results = cached_results[0]

retvals = {}
retvals['searchhash'] = searchhash
retvals['results'] = results
retvals['inst'] = inst
retvals['base_letter'] = base_letter
return retvals
