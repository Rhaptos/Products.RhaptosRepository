<dtml-comment>
arguments: roleparam:string rolename:string roledisplayname:string roleattribution:string rolecomment:string
</dtml-comment>

INSERT INTO roles 
  (roleparam, rolename, roledisplayname, roleattribution, rolecomment) 
VALUES 
(<dtml-sqlvar roleparam type="string">
<dtml-sqlvar rolename type="string">
<dtml-sqlvar roledisplayname type="string">
<dtml-sqlvar roleattribution type="string">
<dtml-sqlvar rolecomment type="string">)
