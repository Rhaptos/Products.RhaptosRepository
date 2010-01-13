<dtml-comment>
arguments: word:string
</dtml-comment>

INSERT INTO keywords 
  (word) 
VALUES 
  (<dtml-sqlvar word type="string">)

