## Script (Python) "getInstitutions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=begins="A", nonroman=None
##title=
##
# Result sets for the name and module/collection counts of institutions.
# Returns list of tuples like ('Institution name', collection_count)
from string import ascii_letters

catalog = context.content.catalog
if not begins:
    names = ['']
elif nonroman:
    names = [i for i in catalog.uniqueValuesFor('atomicInstitution') if i and i.strip()[0] not in ascii_letters]
else:  # begins is true
    match = (begins.upper(), begins.lower())
    names = [i for i in catalog.uniqueValuesFor('atomicInstitution') if i and i.strip()[0] in match]
    # another way, almost certainly slower...
    #names = [i for i in catalog.uniqueValuesFor('atomicInstitution')
    #           if i.strip().startswith(begins.upper()) or i.strip().startswith(begins.lower())]


insts = [(x, len(catalog(portal_type='Collection', atomicInstitution=x))) for x in names if x!='']
if not begins:
    all = catalog(atomicInstitution='',portal_type='Collection')
    unspec = [o for o in all if o.institution=='']
    insts.append(('',len(unspec)))

return insts
