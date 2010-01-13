## Script (Python) "truncate"
##title = truncate a string
##bind container = container
##bind context = context
##bind namespace=
##bind script = script
##bind subpath = traverse_subpath
##parameters = str, max, min = None, suffix = u'[\u2026]'
charset = context.portal_properties.site_properties.getProperty('default_charset', 'utf-8')
if min is None:
    min = int(0.8 * max)
ustr = unicode(str, charset)
if len(ustr) > max:
    words = ustr.split()
    chop = 0
    for index,word in enumerate(words):
        chop = chop+len(word) + 1
        if chop > max - len(suffix) - 1:
            break
    if index == 0:
        return suffix.encode(charset)
    newstr = u' '.join(words[:index])+ u' ' + suffix
    if len(newstr) < min:
        newstr = ustr[:(max-len(suffix))]+ suffix
    ustr=newstr
return ustr.encode(charset)
    
