<dtml-comment>
arguments: start:string end:string
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModuleOAI
max_rows: 0
</dtml-comment>

SELECT
  m.moduleid AS "objectId", m.moduleid AS id, m.portal_type, m.version, m.name,m.name as title,  m.name as "Title", m.created, m.revised, 
  abstract, 1 as weight, m.stateid, m.doctype,l.url AS license, m.module_ident AS ident, m.submitter, 
  p.moduleid AS parent_id, p.version AS parent_version,
  m.authors as authors, m.licensors as licensors, m.maintainers as maintainers,
  fullnames(m.authors) as authornames,
  m.parentauthors as "parentAuthors", m.language as language, 
  (select '{'||list(''''||roleparam||''':['''||array_to_string(personids,''',''')||''']')||'}' from roles natural join moduleoptionalroles where module_ident=m.module_ident group by module_ident) as roles, 
  (select list(word) from modulekeywords mk natural left join keywords where mk.module_ident=m.module_ident) as keywords,
  (select list(tag) from moduletags mt NATURAL LEFT JOIN tags where m.module_ident = mt.module_ident) as subject,
  '' as matched, '' as fields, '' as _keys
FROM latest_modules m NATURAL JOIN abstracts LEFT JOIN modules p on m.parent = p.module_ident, licenses l
WHERE
     date_trunc('seconds', m.revised) between  '<dtml-var expr="start.HTML4()">' and '<dtml-var expr="end.HTML4()">'
and 
 m.licenseid = l.licenseid
order by m.revised
