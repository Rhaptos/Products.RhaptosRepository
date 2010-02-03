## Script (Python) "getLanguageData"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

""" Assembles dynamic data for languages and locales, by language/locale code.
A "locale" in this context is any code that can appear in the language property
of a content object, whether it includes a regional variant or not -- en, en-us,
de-au, fi, etc.. A "language" is a top-level concept like English or Spanish.
The two-letter codes for languages are the same as for region-unspecified
locales, which can be a little confusing. That's why they're in separate
dictionaries.

Examples of resulting dictionaries:

localeData={'en-us': {'totalobjs': 1000, 'mods': 950, 'cols': 50}, 'de': ... }
langData={'en': {'variantCodes': ['en','en-us'], 'totalobjs': 1000, 'mods': 950, 'cols': 50}, 'de': ... }
"""

# Background data sets
langLookup=context.content.langLookup()
gROLC=context.content.getRhaptosObjectLanguageCounts(['Module','Collection'])
modcounts=dict(context.content.getRhaptosObjectLanguageCounts('Module'))
colcounts=dict(context.content.getRhaptosObjectLanguageCounts('Collection'))
localeCodesWithContent=[x[0] for x in gROLC]
modCountDict=dict([modcounts.has_key(la) and (la,modcounts[la]) or (la,0) for la in localeCodesWithContent])
colCountDict=dict([colcounts.has_key(la) and (la,colcounts[la]) or (la,0) for la in localeCodesWithContent])
totalCountDict=dict(gROLC)

localeData={}
for x in localeCodesWithContent:
  localeData[x]={'totalobjs': totalCountDict[x], 'mods': modCountDict[x], 'cols': colCountDict[x]}

langData={}
for x in localeCodesWithContent:
  if x is None: continue
  lc=langCode=x.split('-')[0]
  if not langData.has_key(lc):
    langData[lc]={'variantCodes': [], 'totalobjs': 0, 'mods': 0, 'cols': 0}
  langData[lc]['variantCodes'].append(x)
  langData[lc]['totalobjs']=langData[lc]['totalobjs']+totalCountDict[x]
  langData[lc]['mods']=langData[lc]['mods']+modCountDict[x]
  langData[lc]['cols']=langData[lc]['cols']+colCountDict[x]

# Sort by code, remove master code temporarily,
# then sort others by English name and replace master code
for x in langData.keys():
  codeList=langData[x]['variantCodes']
  codeList.sort()
  masterCode=codeList.pop(0)
  englishCountryNames=[(langLookup[c]['variantName'], c) for c in codeList]
  englishCountryNames.sort()
  codeList=[e[1] for e in englishCountryNames]
  codeList.append(masterCode)
  langData[x]['variantCodes']=codeList

return {'langData': langData, 'localeData': localeData}
