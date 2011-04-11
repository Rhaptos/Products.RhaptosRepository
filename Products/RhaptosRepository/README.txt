RhaptosRepository
=================

This Zope Product is part of the Rhaptos system
(http://software.cnx.rice.edu)

Products.RhaptosRepository implements a version-controlled archive for portal
objects. It stores each version as well as a 'latest' reference
that always points to the most recent revisions of an object.

The repository assigns each object a unique identifier. Objects in
the repository may be viewed in place via a web browser using URLs
of the form: http://<portal_url>/content/<object_id>/<version>/

Products.RhaptosRepository supports the Open Archive Initiative's protocol
for metadata harvesting via requests to 
http://<portal_url>/content/OAI For more details see:
http://www.openarchives.org/OAI/openarchivesprotocol.html

It also supports A9's opensearch protocol
(http://opensearch.a9.com/) for aggregating search results. These
queries are of the form: 
http://<portal_url>/content/opensearch?words=<search terms>

Products.RhaptosRepository's default storage uses the ZODB, but other
backends are possible (For example, see Products.RhaptosModuleStorage which
stores data in CVS and a relational database). Each object
identifier receives a VersionFolder that contains the all the
versions of the object, as well as the special 'latest' object that
points to the most recent revision.

Future plans
------------

- Better extensible back-end storage system with portal_type
  registraion for declaring which storage to use instead of
  triggering off object ID starting characters.

- A method for registering objects before initial publication in
  order to reserve an objectId.  This will allow links to be put in
  place before the object is published so multiple items that refer
  to each other can be published at the same time.

- Integrate versioning with DCWorkflow
