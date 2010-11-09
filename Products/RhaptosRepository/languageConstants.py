# coding=utf-8
## Script (Python) "languageConstants"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

"""Monkeypatch to provide a single dictionary for language lookup."""

import re
lp=localeParens=re.compile('(^[^\(]*) \((.*)\)')

from Products.PloneLanguageTool import availablelanguages
al=availablelanguages

# monkey patch to fix broken brazilian entry
combined = al.combined
combined['pt-br'] = {'english':'Português (Brasil)', 'flag' : 'flag-br.gif'}
al.combined = combined
del combined

allCountries=al.getCountries()
allLocales=al.getCombinedLanguageNames()
allLanguages=al.getNativeLanguageNames()
allEnglishNames={}
for lc, ldict in al.getLanguages().items():
    allEnglishNames[lc] = ldict.get('english')

# Strip the region name out of the "combined" locale dictionary.
allLocaleNames=dict([(c, lp.match(allLocales[c]).groups()[1]) for c in allLocales.keys()])

# Include a couple of refinements relative to the standard Plone country list.
allCountries['YU']='Yugoslavia (former)'
al.countries=allCountries

# Combine variant name, native name, and English name into one dictionary for all codes
def languageConstants():
  langDict={}
  for x in allLocales.keys()+allLanguages.keys():
    langCode=x.split('-')[0]
    try:
      variantName=allLocaleNames[x]
    except KeyError:
      variantName=''
    langDict[x]={'langCode': langCode, 'nativeName': allLanguages[langCode], 'englishName': allEnglishNames[langCode], 'variantName': variantName}
  return langDict

# Monkeypatch results of languageConstants as a dictionary onto PloneLanguageTool
al.languageConstants=languageConstants()
