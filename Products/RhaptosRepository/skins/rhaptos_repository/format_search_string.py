## Script (Python) "format_search_string.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=matched_dict={}, words='', joinstring=' '
##title=
##
from Products.PythonScripts.standard import html_quote
matched_dict = matched_dict.copy()
portal_type = matched_dict.pop('SEARCH_LIMIT_ptype',None)
terms =  matched_dict.items()

for t,i in zip(terms, range(len(terms))):
    if t[1] == [('author', 'translator', 'maintainer', 'editor')]:
        terms[i] = (t[0],['person'])
	matched_dict[t[0]] = ['person']

terms.sort(lambda a,b: cmp(words.find(a[0]),words.find(b[0])))

mainstr = joinstring.join([ ' '.join(((m.find(' ') != -1) and ('"'+html_quote(m)+'"') or html_quote(m),(matched_dict[m] and '<span class="limit">(')+', '.join([' or '.join(not(same_type(f,'')) and f or [f]) for f in matched_dict[m]])+(matched_dict[m] and ')</span>'))).strip() for m in [t[0] for t in terms] ])

if portal_type:
    mainstr = mainstr + ' <span class="limit">(%ss only)</span>' %(portal_type[0])

return mainstr

