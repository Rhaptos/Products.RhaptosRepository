<dtml-comment>
arguments: ident:int
max_rows: 0
</dtml-comment>

SELECT word
FROM keywords
NATURAL JOIN modulekeywords
WHERE <dtml-sqltest ident column="module_ident" type="int"> ORDER BY upper(word)

