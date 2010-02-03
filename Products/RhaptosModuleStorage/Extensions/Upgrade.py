from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
import string
import psycopg2.psycopg1 as psycopg

def upgrade(self,major,minor=None,sub=None):
    """Upgrade the installed tool"""
    out = StringIO()

    # get the tool
    rep = getToolByName(self, 'portal_moduledb')
    db=getattr(self,rep.db)

    if (major < 1) and (minor < 15):
            try:
                db.manage_test(query="""
                 ALTER TABLE modulefti DROP CONSTRAINT "$1";
                 ALTER TABLE modulefti ADD CONSTRAINT fk_modules FOREIGN KEY 
                 (module_ident) REFERENCES modules(module_ident) ON DELETE CASCADE;
                 """)
            except psycopg.ProgrammingError, err:
                print "WARNING: seem to be upgrading an already upgraded db:\n%s" % err

            out.write("Upgrading Module Database for 0.15\n")

    if (major < 1) and (minor < 16):
            try:
                db.manage_test(query="""
                CREATE OR REPLACE FUNCTION fullname (text)
                RETURNS TEXT
                IMMUTABLE STRICT
                LANGUAGE PLPGSQL
                AS '
                DECLARE 
                  name text;
                BEGIN
                    SELECT firstname||\\' \\'||surname 
                    FROM persons WHERE personid = $1 INTO name;
                RETURN name;
                END;
                ';

                CREATE OR REPLACE FUNCTION fullnames (ANYARRAY)
                RETURNS TEXT
                IMMUTABLE STRICT
                LANGUAGE PLPGSQL
                AS '
                DECLARE 
                  name text;
                  names text;
                  id text;
                BEGIN
                  FOR i IN array_lower($1,1) .. array_upper($1,1)
                  LOOP
                    IF  i = 1
                    THEN
                      names = fullname($1[i]);
                    ELSE
                      names := names ||\\', \\' ||  fullname($1[i]);
                    END IF;
                  END LOOP;
                RETURN names;
                END;
                ';
                 """)
            except psycopg.ProgrammingError, err:
                print "WARNING: Problem upgrading db:\n%s" % err

            out.write("Upgrading Module Database for 0.16\n")

    if (major < 1) and (minor < 25):
            try:
                db.manage_test(query="""
		 ALTER TABLE modules ADD COLUMN portal_type text;
		 ALTER TABLE latest_modules ADD COLUMN portal_type text;
		 
                 CREATE OR REPLACE FUNCTION update_latest() RETURNS trigger AS '
                 BEGIN
                   IF TG_OP = ''INSERT'' THEN
                       DELETE FROM latest_modules WHERE moduleid = NEW.moduleid;
                       INSERT into latest_modules ( module_ident,portal_type,moduleid, version, name, 
                   		created, revised, abstractid, stateid, doctype, licenseid, 
                   		submitter,submitlog, parent, language,
                 		authors, maintainers, licensors, parentauthors) 
                   	VALUES ( NEW.module_ident,NEW.portal_type,NEW.moduleid, NEW.version, NEW.name,
                   	 NEW.created, NEW.revised, NEW.abstractid, NEW.stateid, NEW.doctype, NEW.licenseid, 
                   	 NEW.submitter, NEW.submitlog, NEW.parent, NEW.language,
                 	 NEW.authors, NEW.maintainers, NEW.licensors, NEW.parentauthors );
                   END IF;
                 
                   IF TG_OP = ''UPDATE'' THEN
                       UPDATE latest_modules SET
                         moduleid=NEW.moduleid,
                         portal_type=NEW.portal_type,
                         version=NEW.version,
                         name=NEW.name,
                         created=NEW.created,
                         revised=NEW.revised,
                         abstractid=NEW.abstractid,
                         stateid=NEW.stateid,
                         doctype=NEW.doctype,
                         licenseid=NEW.licenseid,
                 	submitter=NEW.submitter,
                 	submitlog=NEW.submitlog,
                         parent=NEW.parent,
                 	language=NEW.language,
                 	authors=NEW.authors,
                 	maintainers=NEW.maintainers,
                 	licensors=NEW.licensors,
                 	parentauthors=NEW.parentauthors 
                         WHERE module_ident=NEW.module_ident;
                   END IF;
                 
                 RETURN NEW;
                 END;
                 
                 ' LANGUAGE 'plpgsql';
		 
                 DROP VIEW all_modules;
                 CREATE VIEW all_modules as 
                 	SELECT module_ident,portal_type,moduleid, version, name, 
                 			created, revised, abstractid, stateid, doctype, licenseid, 
                 			submitter, submitlog, parent, language,
                 			authors, maintainers, licensors, parentauthors
                 	FROM modules
                 	UNION ALL
                 	SELECT module_ident,portal_type,moduleid, 'latest', name, 
                 			created, revised, abstractid, stateid, doctype, licenseid, 
                 			submitter, submitlog, parent, language,
                 			authors, maintainers, licensors, parentauthors
                 	FROM latest_modules;
                 
                 DROP VIEW current_modules; 
                 CREATE VIEW current_modules AS 
                        SELECT * FROM modules m 
                 	      WHERE module_ident = 
                 		    (SELECT max(module_ident) FROM modules 
                 			    WHERE m.moduleid = moduleid );
                 
		 UPDATE modules SET portal_type = 'Module';

                 """)
            except psycopg.ProgrammingError, err:
                print "WARNING: Problem upgrading db:\n%s" % err
            out.write("Upgrading Module Database for 0.25\n")

    if (major < 1) and (minor < 30):
            try:
                db.manage_test(query="""
                CREATE TABLE roles (
                    roleid serial PRIMARY KEY,
                    roleparam text,
                    rolename text,
                    roledisplayname text,
                    roleattribution text,
                    rolecomment text
                    );
                
                CREATE TABLE moduleoptionalroles (
                    module_ident integer,
                    roleid integer,
                    personids text[]
                    );
                    
                INSERT INTO roles (roleid, roleparam, rolename, roledisplayname, roleattribution, rolecomment) VALUES (2, 'licensors', 'Licensor', 'Copyright Holders', 'Copyright by:', 'Legal rights holder of the work.');
                INSERT INTO roles (roleid, roleparam, rolename, roledisplayname, roleattribution, rolecomment) VALUES (3, 'maintainers', 'Maintainer', 'Maintainers', 'Maintained by:', 'Has technical permission to republish the work.');
                INSERT INTO roles (roleid, roleparam, rolename, roledisplayname, roleattribution, rolecomment) VALUES (1, 'authors', 'Author', 'Authors', 'Written by:', 'Intellectual author of the work');
                INSERT INTO roles (roleid, roleparam, rolename, roledisplayname, roleattribution, rolecomment) VALUES (4, 'translators', 'Translator', 'Translators', 'Translation by:', 'Provided language translation.');
                INSERT INTO roles (roleid, roleparam, rolename, roledisplayname, roleattribution, rolecomment) VALUES (5, 'editors', 'Editor', 'Editors', 'Edited by:', 'Provided editorial oversight.');
                                                                                
                 """)
            except psycopg.ProgrammingError, err:
                print "WARNING:  Problem upgrading db:\n%s" % err
            out.write("Upgrading Module Database for 0.30\n")
    
    if (major < 1) and (minor < 31):
            try:
                db.manage_test(query="""

CREATE TABLE "modulefti" (
	"module_ident" integer UNIQUE,
	"module_idx" tsvector,
	FOREIGN KEY (module_ident) REFERENCES modules ON DELETE CASCADE
);

ALTER TABLE persons ADD COLUMN fullname text;

CREATE OR REPLACE FUNCTION fullname (text)
RETURNS TEXT
IMMUTABLE STRICT
LANGUAGE SQL
AS 'SELECT fullname FROM persons WHERE personid = $1;';

CREATE TABLE tags (
    tagid serial PRIMARY KEY,
    tag text,
    scheme text
);

CREATE TABLE moduletags (
    module_ident integer,
    tagid integer,
    FOREIGN KEY (module_ident) REFERENCES modules(module_ident) DEFERRABLE,
    FOREIGN KEY (tagid) REFERENCES tags(tagid) DEFERRABLE
);
                 """)
            except psycopg.ProgrammingError, err:
                print "WARNING: Problem upgrading db:\n%s" % err
            out.write("Upgrading Module Database for 0.31\n")

    return out.getvalue()



def addRatings(self):
    db = self.devrep
    db.manage_test(query="""
CREATE TABLE moduleratings(
    module_ident integer,
    totalrating integer,
    votes integer,
    FOREIGN KEY (module_ident) REFERENCES modules(module_ident) ON DELETE CASCADE
);
		        """)

    db.manage_test(query="""
CREATE OR REPLACE FUNCTION register_rating(integer, integer) RETURNS boolean AS '
DECLARE
    id ALIAS FOR $1;
    rating ALIAS FOR $2;
BEGIN
    UPDATE moduleratings SET totalrating=totalrating+rating,votes=votes+1 WHERE module_ident=id;
    IF NOT FOUND THEN
        INSERT INTO moduleratings (module_ident,totalrating,votes) VALUES (id, rating, 1);
    END IF;
    RETURN FOUND;
END
' LANGUAGE plpgsql;
		        """)


def addReRatings(self):
    db = self.devrep
    db.manage_test(query="""
CREATE OR REPLACE FUNCTION deregister_rating(integer, integer) RETURNS boolean AS '
DECLARE
    id ALIAS FOR $1;
    rating ALIAS FOR $2;
BEGIN
    UPDATE moduleratings SET totalrating=totalrating-rating,votes=votes-1 WHERE module_ident=id;
    RETURN FOUND;
END
' LANGUAGE plpgsql;
		        """)


def storageDispatchUpgrade(self):
    # Register ModuleVersion storage
    from Products.RhaptosModuleStorage.ModuleVersionFolder import ModuleVersionStorage
    from Products.RhaptosModuleStorage.ModuleVersionFolder import ModuleVersionStub

    repos = getToolByName(self, 'content')
    repos.registerStorage(ModuleVersionStorage('module_version_storage'))
    repos.setStorageForType('Module', 'module_version_storage')

    db = self.devrep()
    q = db.query('SELECT moduleid FROM latest_modules')
    modules = [tup[0] for tup in q[1]]
    for objectId in modules:  
        stub = ModuleVersionStub(objectId, 'module_version_storage')
        repos._setObject(objectId, stub, set_owner=0)


def drop_tsearch(self):
    db = self.devrep
    db.manage_test(query="DROP TABLE modulefti")

def setFullnames(self):
    db = self.devrep
    people = self.portal_membership.listMembers()
    for p in people:
        db.manage_test(query="UPDATE persons SET fullname = '%s' where personid= '%s'" % (p.fullname.replace("'","''"),p.id))
      
def setSubjectsOnCheckedoutObjects(self):
    """Set all objects that are checked out copies to the subject that is on the published object"""
    
    portal = getToolByName(self, 'portal_url').getPortalObject()
    
    for wg in portal.GroupWorkspaces.objectValues() + portal.Members.objectValues(['Plone Folder']):
        for o in wg.objectValues(['Collection','Module Editor']):
            obj = o.getPublishedObject()
            if obj:
                try:
                    o.subject = obj.latest.subject
                except:
                    pass

def addREQuoteFunc(self):
    db = self.devrep
    db.manage_test(query="CREATE OR REPLACE FUNCTION req(text) RETURNS text AS $$ select regexp_replace($1,E'([.()?[\\\\]\\\\{}*+|])',E'\\\\\\\\\\\\1','g') $$ language sql immutable;")

def addSemiList(self):
    db = self.devrep
    db.manage_test(query="""
CREATE OR REPLACE FUNCTION "semicomma_cat" (text,text) RETURNS text AS 'select case WHEN $2 is NULL or $2 = '''' THEN $1 WHEN $1 is NULL or $1 = '''' THEN $2 ELSE $1 || '';--;'' || $2 END' LANGUAGE 'sql';""")

    q = db().query("SELECT 1  FROM pg_proc where proname = 'semilist'")
    if q[1]:
        db.manage_test(query="DROP AGGREGATE semilist (text);")
    db.manage_test(query="CREATE AGGREGATE semilist ( BASETYPE = text, SFUNC = semicomma_cat, STYPE = text, INITCOND = '' );")

def reindexFTI(self):
    repos = getToolByName(self, 'content')
    moddb = getToolByName(self, 'portal_moduledb')
    db = self.devrep()
    db.query("DELETE from modulefti")
    q = db.query('SELECT module_ident,moduleid,version FROM latest_modules')
    for mident,modid,ver in q[1]:
        try:
            words = repos[modid][ver].SearchableText() 
        except KeyError:
            print 'no such module: %s/%s' % (modid,ver)
            continue
        moddb.sqlInsertFTIWords(moduleid=modid,
                                version=ver,
                                modulecontents=repos[modid][ver].SearchableText())

def addFiles(self):
    db = self.devrep
    db.manage_test(query="""
CREATE TABLE files (
    fileid serial PRIMARY KEY,
    md5 text,
    file bytea
);

CREATE INDEX files_md5_idx on files (md5);

CREATE FUNCTION update_md5() RETURNS "trigger"
    AS $$
BEGIN
  NEW.md5 = md5(NEW.file);
  RETURN NEW;
END;
$$
    LANGUAGE plpgsql;

CREATE TRIGGER update_file_md5
    BEFORE INSERT OR UPDATE ON files
    FOR EACH ROW
    EXECUTE PROCEDURE update_md5();

CREATE TABLE module_files (
    module_ident integer references modules, 
    fileid integer references files,
    filename text
);

CREATE UNIQUE INDEX module_files_idx ON module_files (module_ident, filename);

GRANT SELECT ON files TO backups ;
GRANT SELECT ON files_fileid_seq TO backups ;
GRANT SELECT ON module_files TO backups ;
    """)

def fixCatalogedModuleTitles(self):
    """Fixup modules with bad cataloged title"""
    cat = self.content.catalog
    for m in self.content.objectValues('Module Version Folder'):
        mv = m.latest
        cat_title = mv.Title()
        mod_title = mv.title
        if cat_title != mod_title:
            print "Fixing module %s: %s -> %s" % (mv.objectId,cat_title,mod_title)
            mv._cataloging = True
            cat.catalog_object(mv)
            del mv._cataloging

def addMimetypes(self):
    rep = getToolByName(self, 'portal_moduledb')
    db=getattr(self,rep.db)

    mreg = getToolByName(self, 'mimetypes_registry')
    lext = mreg.lookupExtension
    db.manage_test(query="""ALTER TABLE module_files ADD COLUMN mimetype text;""")
    d=db()
    mfs=d.query("select distinct filename from module_files")
    for mf in mfs[1]:
        fname = mf[0]
        d.query("update module_files set mimetype = %s where filename = %s ", query_data=(str(lext(fname)),fname))
