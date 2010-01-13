<dtml-comment>
arguments: moduleid:string version:string
</dtml-comment>

SELECT 
  totalrating,
  votes

FROM
  moduleratings

WHERE
  module_ident = (
    SELECT 
      module_ident 
    FROM 
      modules 
    WHERE 
      moduleid=<dtml-sqlvar moduleid type="string">
      and version=<dtml-sqlvar version type="string">
  )
