<dtml-comment>
arguments: file:string
</dtml-comment>

INSERT INTO files 
  (file) 
VALUES 
  (<dtml-var file>::bytea)
RETURNING fileid

