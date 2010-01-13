<dtml-comment>
arguments: authors
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
max_rows: 0
</dtml-comment>

SELECT moduleid AS "objectId", m.portal_type, name AS title, name as "Title", 'latest' as version, created, revised, authors AS _authors, language as _language
FROM latest_modules m
WHERE 
<dtml-in authors>
<dtml-unless sequence-start> OR </dtml-unless>
<dtml-sqlvar sequence-item type="string"> = any (authors)
</dtml-in>
ORDER BY m.name

