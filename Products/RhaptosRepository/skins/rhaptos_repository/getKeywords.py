## Script (Python) "getKeywords"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=firstletter, other=None
##title=
##
from string import ascii_letters
catalog = context.content.catalog

keywords=[]
if other:  # starts with something else
    keywords = [k for k in catalog.uniqueValuesFor('keywordscase') if k.lower()[0] not in ascii_letters]
    keywords.reverse()
elif firstletter:
    fll = firstletter.lower()
    keywords = [k for k in catalog.uniqueValuesFor('keywordscase') if k.lower().startswith(fll)]
    keywords.reverse()
    # Uniquefy based on case insensitive match, but preserve case if no collision, prefering uppercase (hence the reverse)
    keywords=filter(None,dict(map(None,[k.lower() for k in keywords],keywords)).values())
    keywords.sort(lambda x,y: cmp(x.lower(),y.lower()))

return keywords
