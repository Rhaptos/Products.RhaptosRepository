## Script (Python) "browse_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,suppressHiddenFiles=1
##title=Control display of 3-pane browse page

# We assume that we will get a URL like so::
#  http://sullivan.cnx.rice.edu:8680/content/browse_content/author/T/Teddy%20sRoosevelt
# Since we are browse_content, that gives a traverse subpath::
#  author/T/Teddy%20sRoosevelt
# The parts are::
#  pane/param1/param2/param...
# We will look for two page templates, 'pane_%s' and 'pane_detail_%s', which in the example
# would be 'pane_author' and 'pane_detail_author'.
# Both of these are given in their namespace the list made up of the rest of the traverse subpath
# to do with as they will.

l = len(traverse_subpath)
elt2 = l >= 1 and traverse_subpath[0] or None
boxparams = l >= 2 and traverse_subpath[1:] or None

box2 = elt2 and getattr(context, 'pane_%s' % elt2) or None
box3 = elt2 and getattr(context, 'pane_detail_%s' % elt2) or None

return context.content_tab(box2=box2, box3=box3, boxparams=boxparams, panename=elt2)