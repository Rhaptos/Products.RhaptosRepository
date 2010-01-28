## Script (Python) "search_form_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from zLOG import LOG, INFO

REQUEST = context.REQUEST

words = REQUEST.get('words','')
#portal_types = REQUEST.get('portal_types', [])
rating = REQUEST.get('rating',0)
allterms = str(REQUEST.get('allterms', 'weakAND'))
weights = dict(REQUEST.get('weights',{}))
required = dict(REQUEST.get('required',{}))
sorton = str(REQUEST.get('sorton','weight'))
recent = REQUEST.get('recent',False)
inContext = REQUEST.get('inContext','')
showopts = REQUEST.get('showopts','')
term_limit = int(REQUEST.get('term_limit',12))
if REQUEST.form.has_key('advancedsearch'):
    showopts=1
started = DateTime().timeTime()

query=context.quoted_split(words)
ignored = ''

cooked,uncook = context.content.cookSearchTerms(query)
stopped = uncook.get('',[])
#generate in order unique list for user display of stopped terms

stopped_terms = {}
stopped_uniq = [t for t,i in zip(stopped,range(len(stopped))) if i == stopped.index(t)]
for t in stopped_uniq:
    stopped_terms[t] = ''

if len(cooked) > term_limit:
    qi = -1
    term_count = 0
    while term_count < term_limit:
        qi+=1
        if query[qi] not in stopped_terms:
            term_count+=1
    ignored = query[qi]
    query = query[:qi+1]

for field in ['title','keyword']:
    val = REQUEST.get(field, '')
    if val:
        try:
            f_val=shlex.split(val)   # note to future: shlex.split(None) is bad. see r20606
        except ValueError:
            try:
                f_val=shlex.split(val.replace("'","\\'"))
            except ValueError:
                f_val=shlex.split(val.replace("'","\\'")+'"')
        f_type = REQUEST.get(field+'_type','weakAND')
        required[field]=(f_val,f_type,False)
        showopts=1
        
val = REQUEST.get('author', '')
if val:
    try:
        f_val=shlex.split(val)   # note to future: shlex.split(None) is bad. see r20606
    except ValueError:
        try:
            f_val=shlex.split(val.replace("'","\\'"))
        except ValueError:
            f_val=shlex.split(val.replace("'","\\'")+'"')
    person_fields=[]
    for role in REQUEST.get('roles',['Authors','Translators','Maintainers','Editors']):
	person_fields.append(role.lower()[:-1])
    f_type = REQUEST.get('author_type','weakAND')
    required[tuple(person_fields)]=(f_val,f_type,False)
    showopts=1

for field in ['language']:
    val = REQUEST.get(field, '')
    if val:
        f_type = REQUEST.get(field+'_type','OR')
        if same_type(val,''):
            val = [val]
        # Note: this may not work for advanced search, we might need to
        # check the other input fields as well as the regular query
        if cooked:
            required[field]=(val,f_type,True)
        else:
            required[field]=(val,f_type,False)
        showopts=1

for field in ['subject','portal_types']:
    val = REQUEST.get(field, '')
    if val:
        f_type = REQUEST.get(field+'_type','OR')
        if same_type(val,''):
            val = [val]
        # Note: this may not work for advanced search, we might need to
        # check the other input fields as well as the regular query
        if cooked:
            required[field]=(val,f_type,True)
        else:
            required[field]=(val,f_type,False)

if weights.has_key('title'):
    weights.setdefault('exact_title',int(weights['title'])*10)

# Note: This may not work for advanced search, we may need to do
# this only for regular search.
if weights.has_key('author'):
    weights.setdefault('editor',int(weights['author']*0.4))
    weights.setdefault('translator',int(weights['author']*0.8))

DEBUG = REQUEST.get('DEBUG',0)
if DEBUG:
    REQUEST.set('DEBUG_query',(query,allterms))
    REQUEST.set('DEBUG_field_queries',required)
    REQUEST.set('DEBUG_weights',weights)

if showopts:
    REQUEST.set('showopts',1)

results, term_results,searchhash = context.content.searchRepository(query,query_type=allterms,
        weights=weights.copy(),field_queries=required,sorton=sorton,recent=recent,
        use_cache=(DEBUG!='NOCACHE'), min_rating=rating)

matched_terms = {}
skipped_terms = {}
term_res_copy = term_results.copy()
a_skipped, a_matched = term_res_copy.pop('any',(None,None))
for field,(skipped,matched)in term_res_copy.items():
    for m in matched:
        matched_terms.setdefault(m,[]).append(field)
    for s in skipped:
        if s not in stopped_terms:
            skipped_terms.setdefault(s,[]).append(field)

if a_matched or a_skipped:
    if weights:
        w_fields = weights.keys()
        # Hide any fields that we don't want displayed to users.  For now: exact_title
        if 'exact_title' in w_fields:
            w_fields.remove('exact_title')
        # Also, just for simple search: editor and translator.  This may need to be adjusted for advanced search
        if 'editor' in w_fields:
            w_fields.remove('editor')
        if 'translator' in w_fields:
            w_fields.remove('translator')
        for m in a_matched:
            matched_terms.setdefault(m,[]).extend(w_fields)
        for s in a_skipped:
            if s not in stopped_terms:
                 skipped_terms.setdefault(s,[]).extend(w_fields)
    else:
        for m in a_matched:
            if matched_terms.has_key(m):
                matched_terms[m].insert(0,'any')
            else:
                matched_terms[m] = ''
        for s in a_skipped:
            if s not in stopped_terms:
                if skipped_terms.has_key(s):
                    skipped_terms[s].insert(0,'any')
                else:
                    skipped_terms[s] = ''

pts = REQUEST.get('portal_types',[])
if len(pts) == 1:
    typ = pts[0]
    if len(matched_terms.keys()) > 0:
        matched_terms['SEARCH_LIMIT_ptype'] = [typ.lower()]
    else:
        skipped_terms['SEARCH_LIMIT_ptype'] = [typ.lower()]

virtualPath  = REQUEST.get('VIRTUAL_URL_PARTS',(None,None))[1]
virtualPath = virtualPath and '/%s' % virtualPath
regularPath = REQUEST.environ.get('PATH_INFO','/content/search')
template = virtualPath or regularPath

qs = REQUEST.environ.get('QUERY_STRING','')
searchurl = template + '?' + qs

if results and not inContext:
    context.search_history_set(searchhash, searchurl, matched_terms, len(results))

REQUEST.set('time', '%.3f' % (DateTime().timeTime()-started))
REQUEST.set('matched_terms',matched_terms)
REQUEST.set('skipped_terms',skipped_terms)
REQUEST.set('stopped_terms',stopped_terms)
REQUEST.set('term_results', term_results)
REQUEST.set('searchurl', searchurl)
REQUEST.set('was_search', 1)
REQUEST.set('searchhash', searchhash)
REQUEST.set('ignored_after', ignored)
REQUEST.set('term_limit', term_limit)
return results
