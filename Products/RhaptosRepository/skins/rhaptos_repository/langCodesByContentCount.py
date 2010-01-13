## Script (Python) "langCodesByContentCount"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=langData
##title=
##

languageTotals=[(langData[lc]['totalobjs'], lc) for lc in langData.keys()]
languageTotals.sort()
languageTotals.reverse()

return [x[1] for x in languageTotals]

