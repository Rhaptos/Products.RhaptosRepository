<dtml-comment>
arguments: lang
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
max_rows: 0
</dtml-comment>

SELECT 
m.moduleid AS "objectId", 'latest' as version, m.portal_type, m.name as "Title", m.name as title, m.created as _created, m.revised as _revised, 
abstract, m.stateid, m.doctype,l.url AS license, m.module_ident AS ident, m.submitter, 
p.moduleid AS parent_id, p.version AS parent_version,
m.authors as authors, m.licensors as licensors, 
m.maintainers as maintainers, COALESCE(m.parentauthors,ARRAY(select ''::text where false)) as "parentAuthors", m.language as language

FROM latest_modules m
NATURAL JOIN abstracts 
LEFT JOIN modules p on m.parent = p.module_ident
JOIN licenses l on l.licenseid = m.licenseid
WHERE m.language = '<dtml-var lang fmt=sql-quote>';
