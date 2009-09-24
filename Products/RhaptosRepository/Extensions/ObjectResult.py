import AccessControl

class ObjectResult:
    
    def __init__(self,objectId,version,weight=0,repository=None):
	"""shadow class to make sims look like search res"""
	if version == 'latest':
            ob=repository.catalog(objectId=objectId,version=version)
	    if ob:
                self = ob
        else:
	    self = repository.getRhaptosObject(objectId,version)

        self.matched={}
        self.fields={}
        self.weight=weight

AccessControl.allow_class(ObjectResult)
