<dtml-comment>
arguments: moduleid:string version:string tag:string
</dtml-comment>

INSERT INTO moduletags (module_ident,tagid)
  SELECT module_ident, tagid
  FROM modules, tags
  WHERE <dtml-sqltest moduleid type="string">
  AND <dtml-sqltest version type="string">
  AND <dtml-sqltest tag type="string">