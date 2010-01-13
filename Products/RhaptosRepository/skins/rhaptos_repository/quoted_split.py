##Script (Python) "quoted_split"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=words=''
##title=
##

terms=[]
while words:
    q = words.find('"')
    if q != -1:
        q2 = words.find('"',q+1) 
        q2 = (q2 != -1) and q2 or None
        preq=words[:q]
        terms.extend(preq.split())
        terms.append(words[q+1:q2])
        if q2:
            words = words[q2+1:]
        else:
            words = ''
    else:
        terms.extend(words.split())
        words = ''

return filter(None,terms)
