<dtml-comment>
arguments: word:string
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
max_rows: 0
</dtml-comment>

SELECT m.moduleid as "objectId", m.portal_type, m.name as "Title", m.name as title, 'latest' as version, created as _created, revised as _revised, authors as authors,  k.word, m.language as language
FROM latest_modules m, modulekeywords mkw, keywords k
WHERE
  m.module_ident = mkw.module_ident
AND
  mkw.keywordid = k.keywordid
AND (
<dtml-in word>
<dtml-unless sequence-start> OR </dtml-unless>
   lower(k.word)  = lower('<dtml-var sequence-item fmt=sql-quote>')
</dtml-in> )
ORDER BY m.name, k.word
