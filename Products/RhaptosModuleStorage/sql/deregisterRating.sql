<dtml-comment>
arguments: moduleid:string version:string rating:int
</dtml-comment>

SELECT deregister_rating (
    (SELECT 
       module_ident 
     FROM 
       modules 
     WHERE 
       moduleid=<dtml-sqlvar moduleid type="string">
       and version=<dtml-sqlvar version type="string">
    ), 
    <dtml-sqlvar rating type="int">
)
