<dtml-comment>
arguments: lang
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
max_rows: 0
</dtml-comment>

SELECT 
m.moduleid AS "objectId", 'latest' as version, m.portal_type, m.name as "Title", m.name as title, m.created, m.revised, 
abstract, m.stateid, m.doctype,l.url AS license, m.module_ident AS ident, m.submitter, 
p.moduleid AS parent_id, p.version AS parent_version,
m.authors as _authors, m.licensors as _licensors, 
m.maintainers as _maintainers, m.parentauthors as _parentauthors, m.language as language

FROM latest_modules m
NATURAL JOIN abstracts 
LEFT JOIN modules p on m.parent = p.module_ident
JOIN licenses l on l.licenseid = m.licenseid
WHERE m.language = '<dtml-var lang fmt=sql-quote>';
