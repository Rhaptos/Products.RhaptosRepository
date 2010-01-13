## Script (Python) "search_history_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=searchhash,searchurl,matched_terms,lenresults
##title=
##

from Products.PythonScripts.standard import url_quote, url_unquote

rawhash = searchhash

request = context.REQUEST
response = request.RESPONSE
cookies = request.cookies
search_hist = cookies.get('search_history', [])

if search_hist: search_hist = search_hist.split(':')

searchstring = context.format_search_string(matched_terms, searchurl)
searchhash = url_quote(searchhash)  # to forestall any separator conflicts
searchstring = url_quote(searchstring)
searchurl = url_quote(searchurl)
val = searchhash + "|" + searchurl + "|" + searchstring + "|" + str(lenresults)

# remove existing searches, so that we only have the one at the top
searchhashes = [s[0] for s in context.search_history_get()]
if rawhash in searchhashes:
    hashidx = searchhashes.index(rawhash)
    del search_hist[hashidx]

search_hist.insert(0,val)
search_hist = search_hist[:5]  # trim to display size so we don't carry around giant cookies

search_hist = ':'.join(search_hist)
response.setCookie('search_history', search_hist)
request.cookies['search_history'] = search_hist  # to include change in the current request
