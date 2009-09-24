"""
Reference to latest verson of an object stored in RhaptosRepository Product

Author: Brent Hendricks and Ross Reedstrom
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Globals import InitializeClass
from Acquisition import aq_parent

from Products.References import Reference, _dictify

def addLatestReference(self, id, title, path='', REQUEST=None):
    '''Add a reference to *path*. The target does not need to exist.'''
    ob = LatestReference(id)
    ob.edit(title, path)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

class LatestReference(Reference):
    """
    Reference to latest version of an object stored in the repository

    Based on Dieter Mauerer's References Product
    """

    meta_type = 'Latest Reference'

    def url(self):
        """
        Return the canonical URL used to access the object (including a trailing slash)
        """
        return self.absolute_url() + '/'

    # there are several things, we should not relay to the target,
    # because it can prevent managebility of ourself.
    # we may want more intelligent solutions than this one!
    ## changed to add url non-relay (so we can get the 'latest' URL)
    _dontRelayToTarget= (
        '__before_publishing_traverse__',
        '__bobo_traverse__',
        'absolute_url',         # NEW
        'url'                   # NEW
        )
    _dontRelayToTarget= _dictify(_dontRelayToTarget).has_key

    ## change to fix Zope 2.9 TALES path expression problem (see LatestReference.Zope29.README)
    def __bobo_traverse__(self, request, name):
        parent = aq_parent(self)
        proxy = self.__of__(parent)
        return getattr(proxy, name)


InitializeClass(LatestReference)
