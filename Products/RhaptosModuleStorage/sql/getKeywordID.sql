<dtml-comment>
arguments: word:string
</dtml-comment>

SELECT keywordid AS id
FROM keywords 
WHERE <dtml-sqltest word type="string">