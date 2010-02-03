<dtml-comment>
arguments: modules
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
max_rows: 0
</dtml-comment>

<dtml-let versionedMods="[m for m in modules if m[1] != 'latest']" 
          latestMods="[m[0] for m in modules if m[1] == 'latest']" >
<dtml-if versionedMods>
SELECT
  m.moduleid AS "objectId", m.portal_type, m.version, m.version as "reqVersion", m.name, m.created as _created, m.revised as _revised, 
  abstract, m.stateid, m.doctype,l.url AS license, m.module_ident AS ident, m.submitter, 
  p.moduleid AS parent_id, p.version AS parent_version,
  m.authors as authors, m.licensors as licensors, m.maintainers as maintainers, COALESCE(m.parentauthors,ARRAY(select ''::text where false)) as "parentAuthors", m.language as language
FROM modules m
NATURAL JOIN abstracts 
LEFT JOIN modules p on m.parent = p.module_ident,
licenses l
WHERE
m.licenseid = l.licenseid AND (
<dtml-in versionedMods prefix="mod">
<dtml-unless mod_start>OR</dtml-unless> ( 
<dtml-sqltest mod_key column="m.moduleid" type="string" > AND
<dtml-sqltest mod_item column="m.version" type="string" > )
</dtml-in> )

<dtml-if latestMods>
UNION ALL
</dtml-if>
</dtml-if>

<dtml-if latestMods>
SELECT
  m.moduleid AS "objectId", m.portal_type, m.version, 'latest' as "reqVersion", m.name, m.created as _created, m.revised as _revised, 
  abstract, m.stateid, m.doctype,l.url AS license, m.module_ident AS ident, m.submitter, 
  p.moduleid AS parent_id, p.version AS parent_version,
  m.authors as authors, m.licensors as licensors, m.maintainers as maintainers, m.parentauthors as parentauthors
FROM latest_modules m
NATURAL JOIN abstracts 
LEFT JOIN modules p on m.parent = p.module_ident,
licenses l
WHERE
m.licenseid = l.licenseid AND (
<dtml-in latestMods prefix="mod">
<dtml-unless mod_start> OR </dtml-unless>  
<dtml-sqltest mod_item column="m.moduleid" type="string" >
</dtml-in> )
</dtml-if>
</dtml-let>
