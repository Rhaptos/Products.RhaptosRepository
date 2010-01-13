<dtml-comment>
arguments: id:string version:string filename:string
</dtml-comment>

SELECT length(file) as size
FROM files natural join module_files natural join modules
WHERE
<dtml-sqltest id column="moduleid" type="string"> AND
<dtml-sqltest version column="version" type="string"> AND
<dtml-sqltest filename column="filename" type="string">
