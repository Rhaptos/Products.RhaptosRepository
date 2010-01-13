from zope.app.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.interface import classImplements
from Products.CatalogMemberDataTool.PASMemberDataTool import MemberData

class IRateable(IAnnotations):
    """
    Object can rate other objects
    """

class IMemberData(Interface):
    """
    Our own Marker class for Member Data, since CMFCore version does not extend
    Interface properly
    """

classImplements(MemberData, IMemberData)
