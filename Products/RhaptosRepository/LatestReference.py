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

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraverser
from zope.publisher.skinnable import setDefaultSkin
from zope.component import ComponentLookupError
import Products.Five.security
from zExceptions import NotFound


_marker = {}

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
    def __bobo_traverse__(self, REQUEST, name):
        parent = aq_parent(self)
        proxy = self.__of__(parent)
        val = getattr(proxy, name, _marker)
        if val is not _marker:
            return val
        else:
            # try for a Zope 3-type view. see code in Five/traversable.py
            target = self.getTarget()
            
            if not IBrowserRequest.providedBy(REQUEST):
                # Try to get the REQUEST by acquisition
                REQUEST = getattr(self, 'REQUEST', None)
                if not IBrowserRequest.providedBy(REQUEST):
                    REQUEST = FakeRequest()
                    setDefaultSkin(REQUEST)
            Products.Five.security.newInteraction()
            try:
                # note use of 'target' instead of 'self'...
                return ITraverser(target).traverse(path=[name], request=REQUEST).__of__(target)
            except (ComponentLookupError, LookupError,
                    AttributeError, KeyError, NotFound):
                pass
        
        raise AttributeError, "name"


InitializeClass(LatestReference)
