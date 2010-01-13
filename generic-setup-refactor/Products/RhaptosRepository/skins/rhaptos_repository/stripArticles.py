## Script (Python) "stripArticles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=t
##title=
##

ARTICLES = ['the', 'a', 'an']
for a in ARTICLES:
    compare = a + ' '
    if t.lower().startswith(compare) and t[len(compare):]:
        return t[len(compare):]
else:
    return t
