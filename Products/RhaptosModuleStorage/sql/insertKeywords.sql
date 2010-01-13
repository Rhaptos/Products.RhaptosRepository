<dtml-comment>
arguments: moduleid:string version:string keywordid:int
</dtml-comment>

INSERT INTO modulekeywords 
  SELECT module_ident, <dtml-sqlvar keywordid type="int">
  FROM modules
  WHERE <dtml-sqltest moduleid type="string">
  AND <dtml-sqltest version type="string">
