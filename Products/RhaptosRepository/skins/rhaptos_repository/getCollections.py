## Script (Python) "getCollections"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=begins="A", nonroman=None
##title=
##
# Result brains for course names that start with upper/lower 'begins' or are non-ASCII.
# 'nonroman' only will work if 'begins' is false, since we want to support possible other index letters
# Not particularly efficient, since we have to pull the whole list to check if it begins with one letter,
# but that would require a smarter index, or maybe AdvancedQuery.
# see also getInstitutions

from string import ascii_letters

courses = context.content.catalog(portal_type='Collection',sort_on='sortTitle')
if begins:
    match = begins.lower()
    courses = [brain for brain in courses if brain and brain.Title.strip().lower().startswith(match)]
elif nonroman:
    courses = [brain for brain in courses if brain and brain.Title.strip()[0] not in ascii_letters]

return courses
