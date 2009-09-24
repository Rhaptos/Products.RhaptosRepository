## Script (Python) "pane_detail_date_results"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=how='latest'
##title=
##
# Result sets for pane_detail_date are complex enough that we shouldn't do it in ZPT...
#  'how' is expected to be one of 'latest', 'new', 'revised', 'today', 'week', 'month', 'year', 'ever'

kw = {}
kw['number'] = 0
if (how == 'new'):
    kw['new'] = True
elif (how == 'revised'):
    kw['new'] = False

return context.getNewestObjects(**kw)
