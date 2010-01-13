<dtml-comment>
arguments: id:string version:string
</dtml-comment>

SELECT filename
FROM module_files natural join modules
WHERE
<dtml-sqltest id column="moduleid" type="string"> AND
<dtml-sqltest version column="version" type="string">
