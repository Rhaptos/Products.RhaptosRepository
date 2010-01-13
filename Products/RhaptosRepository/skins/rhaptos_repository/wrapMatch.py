## Script (Python) "wrapMatch.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=target_string='', matched_terms=[], open_wrap_tag='<b>', close_wrap_tag='</b>'
##title=
##
target_string = str(target_string)
target_string = target_string.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def wrap(target, term, start=0):
    st = target.lower().find(term.lower(),start)
    if st != -1:
        end = st + len(term)
        return [(st,end)] + wrap(target,term,end)
    else:
        return []

def wrapWithTag(target, intervals, offset):
    m = intervals.pop(0)
    m = (int(m[0]-offset),int(m[1]-offset))
    wrapped = target[:m[0]] + open_wrap_tag + target[m[0]:m[1]] + close_wrap_tag
    if intervals:
        return wrapped + wrapWithTag(target[m[1]:],intervals,offset+len(target[:m[0]]+target[m[0]:m[1]]))
    else:
        return wrapped + target[m[1]:]

matches = []
for term in matched_terms:
    matches.extend(wrap(target_string,term))

matches.sort()

mout=[]
if matches:
    x=matches[0]
    y=()
    for y in matches[1:]:
        if y[0]>x[1]:
            mout.append(x)
            x=y
        else:
            if x[1]<y[1]:
                x=(x[0],y[1])
            y=x

    if y:
        mout.append(y)
    else:
        mout.append(x)
        
if mout:
    return wrapWithTag(target_string,mout,0)
else:
    return target_string
