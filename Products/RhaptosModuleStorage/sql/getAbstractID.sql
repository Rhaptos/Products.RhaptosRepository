<dtml-comment>
arguments: abstract:string
</dtml-comment>

SELECT abstractid AS id
FROM abstracts 
WHERE <dtml-sqltest abstract type="string">
