## Script (Python) "langCodesByContentCount"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=codes
##title=
##

try:
  codes=codes.split(',')
except AttributeError:
  pass

queryString='&'.join(['langs='+x for x in codes])

return queryString
