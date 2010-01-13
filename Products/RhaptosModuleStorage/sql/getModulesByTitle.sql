<dtml-comment>
arguments: firstletter
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
max_rows: 0
</dtml-comment>

SELECT 
m.moduleid AS "objectId", m.portal_type, 'latest' as version, m.name as "Title", m.name as title, m.created, m.revised, 
abstract, m.stateid, m.doctype,l.url AS license, m.module_ident AS ident, m.submitter, 
p.moduleid AS parent_id, p.version AS parent_version,
m.authors as _authors, m.licensors as _licensors, 
m.maintainers as _maintainers, m.parentauthors as _parentauthors, m.language as language

FROM latest_modules m
NATURAL JOIN abstracts 
LEFT JOIN modules p on m.parent = p.module_ident
JOIN licenses l on l.licenseid = m.licenseid
WHERE upper(title_order(m.name)) ~ upper('^<dtml-var firstletter>') ORDER BY upper(title_order(m.name));
