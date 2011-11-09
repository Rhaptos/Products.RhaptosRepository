## Script (Python) "stats_present"
##title = some hit stats have been loaded
##bind container = container
##bind context = context
##bind namespace=
##bind script = script
##bind subpath = traverse_subpath
##parameters = 
interval_start, interval_end  = context.portal_hitcount.getIncrementDateRange()
return not(interval_start == interval_end)
