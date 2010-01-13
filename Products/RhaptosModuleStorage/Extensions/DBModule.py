from ComputedAttribute import ComputedAttribute

class DBModule:

    icon = 'module_icon.gif'
    # Compatibility with CMF objects
    getIcon = icon

    meta_type = 'Rhaptos Module Version'


    # Compatibility with Archetypes catalog results
    Title = ComputedAttribute(lambda self: self.title)
    
    # Convert DB arrays into python tuples, dicts, etc.
    authors = ComputedAttribute(lambda self: tuple(self._authors[1:-1].split(',')), 1)
    maintainers = ComputedAttribute(lambda self: tuple(self._maintainers[1:-1].split(',')), 1)
    licensors = ComputedAttribute(lambda self: tuple(self._licensors[1:-1].split(',')), 1)
    parentAuthors = ComputedAttribute(lambda self: self._parentauthors and tuple(self._parentauthors[1:-1].split(',')) or [], 1)
    authornames = ComputedAttribute(lambda self: list(self._authornames.split(',')),1)
    keywords = ComputedAttribute(lambda self: list(self._keywords.split(',')),1)
    getHistoryCount = ComputedAttribute(lambda self: self.versioncount)
    matched = ComputedAttribute(lambda self: self._keydict(0),0)
    fields = ComputedAttribute(lambda self: self._keydict(1),0)
    subject = ComputedAttribute(lambda self: self._subject and tuple(self._subject.split(',')) or (),1)
    
    roles = ComputedAttribute(lambda self: self.getRolesDict(),1)
    def getRolesDict(self):
        """Return the optional roles for this object"""
        if self._roles:
            return eval(self._roles)
        else:
            return {}
    
    def url(self):
        return '/'.join([self.content.absolute_url(),self.objectId,self.version])

    def _keydict(self,index):
        if self._keys and type(self._keys) == type(''):
            d={}
            d2={}
            for k in self._keys.split(';--;'):
                t,v = k.split('-::-')
                d.setdefault(t,[]).append(v)
                d2.setdefault(v,[]).append(t)
            for k,v in d2.items():
                d2[k]={}.fromkeys(d2[k]).keys()
            self._keys=(d,d2)
        return self._keys[index]

class DBModuleSearch:

    icon = 'module_icon.gif'
    # Compatibility with CMF objects
    getIcon = icon

    meta_type = 'Rhaptos Module Version'


    def __init__(self,record=None, **args):
        """
        Class for wrapping search result records.  Usable as a pluggable brain (no arguments) or as a
        standalone (and therefore pickleable) class: pass in a record instance as the argument.
        """
        if record:
            if hasattr(record,'__record_schema__'):
                fields = record.__record_schema__
            else:
                fields = [v for v in dir(record) if hasattr(record,v) and not v.startswith('__')]
            for f in fields:
                setattr(self,f,record[f])
	    for f,v in args.items():
		if not(hasattr(self,f)):
		    setattr(self,f,v)

        else:
            # Convert DB arrays into python tuples, dicts, etc.
            d={}
            d2={}
            for k in self._keys.split(';--;'):
                t,v = k.split('-::-')
                d.setdefault(t,[]).append(v)
                d2.setdefault(v,[]).append(t)
            for k,v in d2.items():
                d2[k]={}.fromkeys(d2[k]).keys()
            self.matched = d.copy()
            self.fields = d2.copy()
            self._keys = (self.matched,self.fields)
            
    def url(self):
        return '/'.join([self.content.absolute_url(),self.objectId,self.version])


class DBModuleOAI:

    icon = 'module_icon.gif'

    # Compatibility with CMF objects
    getIcon = icon
    meta_type = 'Rhaptos Module Version'


    def __init__(self):
        
        # Convert DB arrays into python tuples, dicts, etc.
            self.authors =  tuple(self.authors[1:-1].split(','))
            self.maintainers = tuple(self.maintainers[1:-1].split(','))
            self.licensors = tuple(self.licensors[1:-1].split(','))
            self.parentAuthors = self.parentAuthors and tuple(self.parentAuthors[1:-1].split(',')) or []
            self.authornames = list(self.authornames.split(', '))
            self.keywords = list(self.keywords.split(', '))
            self.matched = self._keydict(0)
            self.fields = self._keydict(1)
            self.subject = self.subject and tuple(self.subject.split(', ')) or ()
            self.roles = self.roles and eval(self.roles) or {}

    def url(self):
        return '/'.join([self.content.absolute_url(),self.objectId,self.version])

    def _keydict(self,index):
        if self._keys and type(self._keys) == type(''):
            d={}
            d2={}
            for k in self._keys.split(';--;'):
                t,v = k.split('-::-')
                d.setdefault(t,[]).append(v)
                d2.setdefault(v,[]).append(t)
            for k,v in d2.items():
                d2[k]={}.fromkeys(d2[k]).keys()
            self._keys=(d,d2)
            return self._keys[index]
        else:
            return {}

