<dtml-comment>
arguments: query
cache_time: 60
max_cache:  10
max_rows: 0
</dtml-comment>

<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
SELECT p.*
FROM persons p
where
 p.firstname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 p.surname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 p.fullname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or 
 p.personid ~* ('^'||req('<dtml-var q_item fmt=sql-quote>'::text)||'$')
 or
 p.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)||'.*@')
</dtml-in>

