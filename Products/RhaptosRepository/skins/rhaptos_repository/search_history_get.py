## Script (Python) "search_history_get"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.PythonScripts.standard import url_unquote

REQUEST = context.REQUEST
cookies = REQUEST.cookies
search_hist = cookies.get('search_history', [])
#context.plone_log("search_hist")
#context.plone_log(same_type(search_hist,''))
#context.plone_log(search_hist)

if search_hist: search_hist = search_hist.split(':')

retlist = []
for elt in search_hist:
    searchrecord = elt.split('|')
    #context.plone_log("----------------------")
    #context.plone_log("searchrecord")
    #context.plone_log(searchrecord)

    searchhash = url_unquote(searchrecord[0])
    searchurl = url_unquote(searchrecord[1])
    searchstring = url_unquote(searchrecord[2])
    lenresults = int(searchrecord[3])
    searchrecord = (searchhash, searchurl, searchstring, lenresults)
    retlist.append(searchrecord)

return retlist
