## Script (Python) "langCodesByEnglishSort"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=langData={}
##title=
##

langLookup=context.content.langLookup()

languageEnglishNames=[(langLookup[lc]['englishName'], lc) for lc in langData.keys() if langLookup.has_key(lc)]
languageEnglishNames.sort()

languagesByEnglishName=[x[1] for x in languageEnglishNames]

return languagesByEnglishName



