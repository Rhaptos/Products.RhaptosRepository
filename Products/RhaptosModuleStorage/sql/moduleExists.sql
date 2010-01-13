<dtml-comment>
arguments: id:string
</dtml-comment>

SELECT TRUE FROM modules WHERE <dtml-sqltest id column="moduleid" type="string"> LIMIT 1;