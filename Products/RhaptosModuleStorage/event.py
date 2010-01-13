from zope.interface import implements
from interfaces.event import IModuleRatedEvent

class ModuleRatedEvent(object):

    implements(IModuleRatedEvent)

    def __init__(self, ob):
        self.object = ob
