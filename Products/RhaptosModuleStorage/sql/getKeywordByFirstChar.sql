<dtml-comment>
arguments: firstletter:string
max_rows: 0
</dtml-comment>

SELECT word FROM keywords WHERE upper(word) ~ upper('^<dtml-var firstletter>') ORDER BY upper(word)
