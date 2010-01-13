## Script (Python) "getContentByLanguage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lang
##title=
##

if same_type(lang,''):
  lang=lang.split(',')

return context.catalog(language=lang,sort_on='sortTitle')
