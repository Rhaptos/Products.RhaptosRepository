<dtml-comment>
arguments: text:string query:string open_wrap_tag:string=<b> close_wrap_tag:string=</b>
</dtml-comment>

SELECT headline('<dtml-var text fmt=sql-quote>',plainto_tsquery('<dtml-var query fmt=sql-quote>'),'StartSel=<dtml-var open_wrap_tag>, StopSel=<dtml-var close_wrap_tag>, ShortWord=5, MinWords=50, MaxWords=60') as headline,
headline('<dtml-var text fmt=sql-quote>',plainto_tsquery('<dtml-var query fmt=sql-quote>'),'StartSel=<dtml-var open_wrap_tag>, StopSel=<dtml-var close_wrap_tag>, MinWords=600, MaxWords=700') as fulltext
