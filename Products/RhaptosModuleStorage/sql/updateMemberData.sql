<dtml-comment>
arguments: id honorific firstname othername surname fullname lineage email homepage comment
</dtml-comment>

UPDATE persons 
<dtml-sqlgroup set noparens>
  <dtml-sqltest honorific type="string" optional><dtml-comma>
  <dtml-sqltest firstname type="nb" optional><dtml-comma>
  <dtml-sqltest othername type="string" optional><dtml-comma>
  <dtml-sqltest surname type="nb" optional><dtml-comma>
  <dtml-sqltest fullname type="nb" optional><dtml-comma>
  <dtml-sqltest lineage type="string" optional><dtml-comma>
  <dtml-sqltest email type="nb" optional><dtml-comma>
  <dtml-sqltest homepage type="string" optional><dtml-comma>
  <dtml-sqltest comment type="string" optional>
</dtml-sqlgroup>
WHERE <dtml-sqltest id column="personid" type="string">;


