## Script (Python) "expanded_browse_subject_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# organize results data for expanded subject view
# hopefully to turn into a Zope 3 view.

request = context.REQUEST
content = context.portal_url.getPortalObject().content
portal_url = context.portal_url.getPortalPath()

basehash = context.expanded_searchhash(request.form)

bycontent_hash = "%s>by" % basehash
containers_hash = "%s>containers" % basehash
forks_hash = "%s>forks" % basehash
m_content_hash = "%s>m_content" % basehash
sorton = request.get('sorton', 'portal_type')
recent = request.get('recent', False)
request.set('sorton',sorton)
request.set('recent',recent)

cached_bycontent = content.cache.resultsCacheLookup(bycontent_hash,sorton,recent)
cached_containers = content.cache.resultsCacheLookup(containers_hash,sorton,recent)
cached_forks = content.cache.resultsCacheLookup(forks_hash,sorton,recent)
cached_m_content = content.cache.resultsCacheLookup(m_content_hash,sorton,recent)

author = request.get('author')
m = context.desecured.getMemberById(author)
first_letter = m.surname and m.surname[0] or m.shortname and m.shortname[0]
subset = request.get('subset', 'by')
base_letter = request.get('letter', first_letter)
sortkey = 'sortTitle'
reverse = None

# backwards-compat support for links to pages using the "old" expanded vocabulary, since expanded authors
# now (15 Oct 2007) uses the same vocabulary as the 3-pane. TODO: remove this after a while
subset = {'content':'by', 'forks':'derivedfrom', 'm_content':'maintains'}.get(subset, subset)

# TODO: we can't currently detect between a cache miss and a None hit; we should be checking against a
# default value. But: anyone doing this search really should have some hit, so we should be okay at the moment
if not (cached_bycontent or cached_containers or cached_forks or cached_m_content):
    all_results = context.getAuthorContent(author,sortkey,reverse)
    bycontent = all_results['content']
    containers = all_results['containers']
    forks = all_results['forks']
    m_content = all_results['m_content']
    
    content.cache.resultsCacheInject(bycontent_hash,  (bycontent, {}, sorton, recent))
    content.cache.resultsCacheInject(containers_hash, (containers, {}, sorton, recent))
    content.cache.resultsCacheInject(forks_hash,      (forks, {}, sorton, recent))
    content.cache.resultsCacheInject(m_content_hash,  (m_content, {}, sorton, recent))
else:
    bycontent = cached_bycontent[0]
    containers = cached_containers[0]
    forks = cached_forks[0]
    m_content = cached_m_content[0]

if subset == 'by':
    raw_results = bycontent
    searchhash = bycontent_hash
elif subset=='derivedfrom':
    raw_results = forks
    searchhash = forks_hash
elif subset=='maintains':
    raw_results = m_content
    searchhash = m_content_hash
elif subset=='containers':
    raw_results = containers
    searchhash = containers_hash
else:
    raw_results = bycontent
    searchhash = bycontent_hash

qs = request.environ.get('QUERY_STRING', '')
queries = '&'.join([p for p in qs.split('&') if not(p.startswith('subset=') or p.startswith('author='))])
returnhref = portal_url+'/content/browse_content/author/'+base_letter+'/'+author+'/'+subset

results = sorton != 'title' and content.sortSearchResults(list(raw_results),sorton,recent) or raw_results;

retvals = {}
retvals['searchhash'] = searchhash
retvals['results'] = results
retvals['queries'] = queries
retvals['subset'] = subset
retvals['author'] = author
retvals['m'] = m
retvals['bycontent'] = bycontent
retvals['containers'] = containers
retvals['forks'] = forks
retvals['m_content'] = m_content
retvals['returnhref'] = returnhref
return retvals
