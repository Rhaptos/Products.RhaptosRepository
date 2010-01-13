from zope.interface import implements
from zope.app.event.interfaces import IObjectEvent

class IModuleRatedEvent(IObjectEvent):
    """
    An event which fires whenever a module is rated.
    """
