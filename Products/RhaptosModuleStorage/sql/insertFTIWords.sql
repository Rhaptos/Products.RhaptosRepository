<dtml-comment>
arguments: moduleid:string version:string modulecontents:string
</dtml-comment>

INSERT INTO modulefti (module_ident,module_idx)
  SELECT module_ident, to_tsvector(<dtml-sqlvar modulecontents type="string">)
  FROM modules
  WHERE <dtml-sqltest moduleid type="string">
  AND <dtml-sqltest version type="string">
