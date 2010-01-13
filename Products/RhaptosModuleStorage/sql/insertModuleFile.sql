<dtml-comment>
arguments: moduleid:string version:string fileid:string filename:string mimetype:string
</dtml-comment>

INSERT INTO module_files (module_ident, fileid, filename, mimetype)
  SELECT module_ident, <dtml-sqlvar fileid type="string">, 
         <dtml-sqlvar filename type="string">,
         <dtml-sqlvar mimetype type="string">
  FROM modules
  WHERE <dtml-sqltest moduleid type="string">
  AND <dtml-sqltest version type="string">
