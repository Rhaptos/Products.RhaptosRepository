## Script (Python) "expanded_browse_language_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# organize results data for expanded language view
# hopefully to turn into a Zope 3 view.

request = context.REQUEST
content = context.portal_url.getPortalObject().content
searchhash = context.expanded_searchhash(request.form)
sorton = request.get('sorton', 'portal_type')
recent = request.get('recent', False)
request.set('sorton',sorton)
request.set('recent',recent)

cached_results = content.cache.resultsCacheLookup(searchhash,sorton,recent)

langLookup = content.langLookup()
getLangAndLocaleData = context.getLanguageData()
langData = getLangAndLocaleData['langData']
langs = request.langs
langCode = langs and langs[-1]
majorCode  = langCode and langCode.split('-')[0] or ''
nativeName = majorCode and langLookup[majorCode]['nativeName'] or ''
engName = majorCode and langLookup[majorCode]['englishName'] or ''
variantName = langCode and langLookup[langCode]['variantName'] or ''
siblingLocales = majorCode and langData[majorCode]['variantCodes'] or ''

if cached_results is None:
    raw_results = content.getContentByLanguage(lang=langs)
    results = sorton != 'title' and content.sortSearchResults(list(raw_results),sorton,recent) or raw_results
    content.cache.resultsCacheInject(searchhash, (results, {}, sorton, recent))
else:
    results = cached_results[0]

retvals = {}
retvals['searchhash'] = searchhash
retvals['results'] = results
retvals['langLookup'] = langLookup
retvals['langs'] = langs
retvals['langCode'] = langCode
retvals['siblingLocales'] = siblingLocales
retvals['nativeName'] = nativeName
retvals['engName'] = engName
retvals['variantName'] = variantName
return retvals
