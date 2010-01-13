RhaptosModuleStorage

  This Zope Product is part of the Rhaptos system
  (http://software.cnx.rice.edu)

  RhaptosModuleStorage is an alternative RhaptosRepository storage backend
  for use with Rhaptos modules.  Each module is split into its component
  files which are stored in CVS and the metadata is stored in a
  relational database using the included ModuleDBTool.  It also makes
  use of LinkMapTool to store module-level links.

  RhaptosModuleStorage does not currently store any content in the ZODB,
  but relies on a __bobo_traverse__ hook in RhaptosRepository to
  dynamically create objects.  In the future this will probably be
  altered so that at least the ModuleVersionFolder objects are stored
  in the ZODB.

  Requires FSImportTool, CVSTool, LinkMapTool, ExtZSQL, CNXMLDocument

Future plans

  - Refactor with RhaptosRepository for better extensible back-end
    storage system.

