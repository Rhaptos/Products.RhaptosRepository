<dtml-comment>
arguments: num:int
max_rows: 0
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModule
</dtml-comment>

select m.moduleid as "objectId" , m.portal_type, m.name as "Title", m.name as title, 'latest' as "version", (select count(*) from modules where moduleid=m.moduleid) as versioncount, m.created, m.revised, m.submitter, m.submitlog, a.abstract, 1 as weight, m.authors as _authors,  fullnames(m.authors) as _authornames, l.url as license
from 
latest_modules m, abstracts a, licenses l
where
 m.abstractid = a.abstractid 
 and m.licenseid=l.licenseid
order by revised desc
<dtml-if num>limit <dtml-sqlvar num type="int"></dtml-if>
