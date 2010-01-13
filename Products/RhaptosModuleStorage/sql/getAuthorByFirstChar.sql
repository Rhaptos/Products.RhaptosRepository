<dtml-comment>
arguments: firstletter:string
max_rows: 0
</dtml-comment>

SELECT * FROM persons WHERE upper(surname) ~ upper('^<dtml-var firstletter>') ORDER BY upper(surname)
