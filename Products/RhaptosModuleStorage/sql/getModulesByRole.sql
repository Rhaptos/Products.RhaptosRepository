<dtml-comment>
arguments: user:string role:string
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
max_rows: 0
</dtml-comment>

SELECT moduleid AS "objectId", portal_type, title_order(name) as "sortTitle", name AS title, name as "Title", 'latest' AS version, created, revised, authors as _authors, language, p.fullname||'-::-<dtml-var role>' as _keys
FROM latest_modules 
<dtml-if expr="role in ('author', 'maintainer', 'licensor', 'parentAuthor')">
   ,persons p

   WHERE 

   <dtml-sqlvar user type="string"> = any (<dtml-var role>s)
<dtml-else>
   natural left join moduleoptionalroles natural left join roles, persons p

   WHERE 

   <dtml-sqlvar user type="string"> = any (personids)

   AND

   '<dtml-var role>s' = roleparam
</dtml-if>

AND p.personid = <dtml-sqlvar user type="string">

ORDER BY "sortTitle"
