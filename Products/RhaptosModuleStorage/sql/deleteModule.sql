<dtml-comment>
arguments: id:string version:string
</dtml-comment>

DELETE FROM files WHERE fileid in
    (SELECT fileid FROM module_files WHERE module_ident IN
        (SELECT module_ident FROM modules WHERE 
            <dtml-sqltest id column="moduleid" type="string"> 
            <dtml-if version>
            AND
            <dtml-sqltest version column="version" type="string" optional>
            </dtml-if>
    ));
DELETE FROM module_files WHERE module_ident IN
    (SELECT module_ident FROM modules WHERE 
        <dtml-sqltest id column="moduleid" type="string"> 
        <dtml-if version>
        AND
        <dtml-sqltest version column="version" type="string" optional>
        </dtml-if>
    );
DELETE FROM moduletags WHERE module_ident IN
    (SELECT module_ident FROM modules WHERE 
        <dtml-sqltest id column="moduleid" type="string"> 
        <dtml-if version>
        AND
        <dtml-sqltest version column="version" type="string" optional>
        </dtml-if>
    );

DELETE from modules where 
<dtml-sqltest id column="moduleid" type="string"> 
<dtml-if version>
and
<dtml-sqltest version column="version" type="string" optional>
</dtml-if>
;

DELETE from abstracts where abstractid not in (select abstractid from modules)

