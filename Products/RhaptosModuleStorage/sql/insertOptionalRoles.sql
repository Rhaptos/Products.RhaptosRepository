<dtml-comment>
arguments: moduleid:string version:string rolename:int persons
</dtml-comment>

INSERT INTO moduleoptionalroles (module_ident, roleid, personids)
  SELECT module_ident, roleid, ARRAY <dtml-var expr="_.list([p.encode('utf-8') for p in persons])">
  FROM modules, roles
  WHERE <dtml-sqltest moduleid type="string">
  AND <dtml-sqltest version type="string">
  AND <dtml-sqltest rolename type="string">
