"""
OAI.py - Open Archives Initiative PMH Support

Author: Brent Hendricks and Ross Reedstrom
(C) 2004-2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

# FIXME: implement resumptionToken using batch
# Identifier should be of the form oai:cnx.rice.edu:id/version

import sys
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem

START_TIME = DateTime('2000-01-01T19:20:30Z')

# OAI Verbs and arguments from  http://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm
VERBS = {'GetRecord':{'required':['verb', 'identifier', 'metadataPrefix']},
         'Identify':{'required':['verb']},
         'ListIdentifiers':{'required':['verb', 'metadataPrefix'], 'optional':['from', 'until', 'set']},
         'ListMetadataFormats':{'required':['verb'], 'optional':['identifier']},
         'ListRecords':{'required':['verb','metadataPrefix'], 'optional':['from', 'until', 'set']},
         'SearchRecords':{'required':['verb','metadataPrefix','query'],'optional':['weights','sorton','b_start','b_size']},
         'ListSets':{'required':['verb'], 'optional':['resumptionToken']},
         }

METADATA_FORMATS = [
        {'prefix':'oai_dc',
         'schema':'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
         'namespace':'http://www.openarchives.org/OAI/2.0/oai_dc/'
         },
        {'prefix':'ims1_2_1',
         'schema':'http://www.imsglobal.org/xsd/imsmd_v1p2p4.xsd',
         'namespace':'http://www.imsglobal.org/xsd/imsmd_v1p2'
         },
        {'prefix':'cnx_dc',
         'schema':'/http://cnx.rice.edu/technology/cnx_dc/schema/xsd/1.0/cnx-dc-extension.xsd',
         'namespace':'http://cnx.rice.edu/cnx_dc/'
         }
        ]



# OAI error codes
class OAIError(Exception):
    code = None

class BadArgumentError(OAIError):
    code = "badArgument"

class IdDoesNotExistError(OAIError):
    code = "idDoesNotExist"

class NoMetadataFormatsError(OAIError):
    code = "noMetadataFormats"

class BadResumptionToken(OAIError):
    code = "badResumptionToken"

class NoRecordsMatch(OAIError):
    code = "noRecordsMatch"

class CannotDisseminateFormat(OAIError):
    code = "cannotDisseminateFormat"
    
class NoSetHierarchy(OAIError):
    code = "noSetHierarchy"
    
class OAIHandler(SimpleItem):
    """Class to handle OAI PMH requests"""

    def __init__(self, id):
        self.id = id

    def __call__(self, REQUEST={}):
        """Perform an OAI query"""
        verb = REQUEST.get('verb', None)
        if verb not in VERBS.keys():
            return self.oai_results(error='badVerb', message='Illegal verb: Legal verbs are: %s' % ', '.join(VERBS.keys()))

        args = REQUEST.form
        try:
            checkArguments(args, VERBS[verb].get('required',[]), VERBS[verb].get('optional',[]))
            handler = getattr(self, verb)
            results = handler(**args)
            if results:
                args.update(results)
            return self.oai_results(**args)
        except OAIError, e:
            return self.oai_results(error=sys.exc_type.code, message=e)

    index_html = __call__

    def Identify(self, **args):
        pass

    def ListMetadataFormats(self, **args):
        #FIXME we support all formats for all objects, to date.
        #identifier = args.get('identifier', None)
        #if identifier:
        #    obj = self._getObjectByIdentifier(identifier)
        return {'results':METADATA_FORMATS}

    def ListIdentifiers(self, **args):
        start, end = parseDates(args)
        r = {}
        r['results'] = self.searchRepositoryByDate(start, end)
        if not r['results']:
            raise NoRecordsMatch, "No records match specified criteria"
        return r
    
    def ListRecords(self, **args):
        start, end = parseDates(args)
        r = {}
        r['results'] = self.searchRepositoryByDate(start, end)
        if not r['results']:
            raise NoRecordsMatch, "No records match specified criteria"
        return r

    def SearchRecords(self, **args):
        r = {}
        verb = args.pop('verb')
        md = args.pop('metadataPrefix')
        weights = args.get('weights')
        if weights:
            args['weights'] = weights.copy()
        try:
            b_start = int(args.pop('b_start'))
        except KeyError:
            b_start = None
        try:
            b_size = int(args.pop('b_size'))
            if b_size == -1:
                end=None
            else:
                end = (b_start or 0) + b_size
        except KeyError:
            end = (b_start or 0) + 10
        r['results'] = [self.getRhaptosObject(o.objectId,o.version) for o in self.searchRepository(**args)[0][b_start:end]]
        if not r['results']:
            raise NoRecordsMatch, "No records match specified criteria"
        r['verb'] = verb
        r['metadataPrefix'] = md
        return r

    def ListSets(self, **args):
        #FIXME currently do not support sets
        raise NoSetHierarchy, "The repository does not support sets."


    def GetRecord(self, **args):
        identifier = args.get('identifier', None)
        r = {}
        r['results'] = [self._getObjectByIdentifier(identifier)]
        # FIXME: need to somehow return author information
        return r


    def _getObjectByIdentifier(self, identifier):
        # FIXME: check for valid identifier
        try:
            proto, host, objectId = identifier.split(':')
        except ValueError:
            raise IdDoesNotExistError, "Identifier %s does not exist" % identifier
        try:
            obj = self.getRhaptosObject(objectId, 'latest')
        except (AttributeError, KeyError):
            raise IdDoesNotExistError, "Identifier %s does not exist" % identifier
        return obj


def parseDates(args):
    """Parse the start and end dates out of the argument list, checking for date sanity and returning them as a tuple"""
    
    start = args.get('from', None)
    end = args.get('until', None)

    if start and end and len(start) != len(end):
        raise BadArgumentError, "From and until dates have different granularity (%s, %s)" % (start, end)

    # Now that we've compared granularity, we can put it defaults
    start = start or str(START_TIME)
    end = end or str(DateTime())
    
    try:
        start_date = DateTime(start)
    except (IndexError, DateTime.SyntaxError):
        raise BadArgumentError, "Illegal date argument: %s" % start

    try:
        end_date = DateTime(end)
    except (IndexError, DateTime.SyntaxError):
        raise BadArgumentError, "Illegal date argument: %s" % end

    return (start_date, end_date)


def checkArguments(mapping, required=[], optional=[]):
    args = mapping.keys()

    # FIXME: we don't handle resumptionToken very well
    if 'resumptionToken' in args:
        if len(args) > 2:
            raise BadArgumentError, "resumptionToken not allowed with other arguments"
        else:
            raise BadResumptionToken, "Bad resumption token"
    
    if 'metadataPrefix' in args:
       if mapping['metadataPrefix'] not in [mf['prefix'] for mf in METADATA_FORMATS]:
           raise CannotDisseminateFormat, "metadataPrefix %s not supported" % mapping['metadataPrefix']

    for r in required:
        try:
            args.remove(r)
        except ValueError:
            raise BadArgumentError, "Required argument %s missing" % r
    
    for r in optional:
        try:
            args.remove(r)
        except ValueError:
            pass

    if args:
        raise BadArgumentError, "Illegal arguments: %s" % args
        
