<dtml-comment>
arguments: moduleid:string version:string=latest query:string open_wrap_tag:string=<b> close_wrap_tag:string=</b>
</dtml-comment>

SELECT headline(abstract,plainto_tsquery('<dtml-var query fmt=sql-quote>'), 'StartSel=<dtml-var open_wrap_tag fmt=sql-quote>, StopSel=<dtml-var close_wrap_tag fmt=sql-quote>, ShortWord=5, MinWords=50, MaxWords=60') as headline,
headline(abstract,plainto_tsquery('<dtml-var query fmt=sql-quote>'),'StartSel=<dtml-var open_wrap_tag fmt=sql-quote>, StopSel=<dtml-var close_wrap_tag fmt=sql-quote>, MinWords=600, MaxWords=700') as abstract
FROM abstracts natural join <dtml-if expr="version == 'latest'">latest_modules
WHERE
<dtml-else>modules WHERE
<dtml-sqltest version type="string">
AND
</dtml-if>
<dtml-sqltest moduleid type="string">
