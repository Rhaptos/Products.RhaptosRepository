<dtml-comment>
arguments: query weights required min_rating=""
class_file: RhaptosModuleStorage.DBModule.py
class_name: DBModuleSearch
cache_time: 60
max_cache:  100
max_rows: 0 
</dtml-comment>

select lm.name as title,lm.name as "Title", title_order(lm.name) as "sortTitle", lm.moduleid as "objectId",
  lm.version as version, revised, language, weight, keys as _keys, '' as matched, '' as fields, lm.portal_type,
  (mr.totalrating*1.0/greatest(mr.votes, 1)) as rating
from latest_modules lm natural left join moduleratings mr,
(
select module_ident, cast (sum(weight) as bigint) as weight, semilist(keys) as keys  from 
<dtml-with weights mapping>
<dtml-if expr="weights['parentAuthor'] or weights['language'] or weights['subject'] or weights['fulltext'] or weights['abstract'] or weights['keyword'] or weights['author'] or weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
(
<dtml-if parentAuthor>
select cm.module_ident, count(*)*<dtml-var parentAuthor> as weight, semilist(key) as keys
from (
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>

select module_ident, '<dtml-var q_item fmt=sql-quote>'::text ||'-::-parentAuthor' as key
from 
latest_modules 
where
 '<dtml-var q_item fmt=sql-quote>' = any (parentAuthors)
</dtml-in>
) cm

group by cm.module_ident

<dtml-if expr="weights['language'] or weights['subject'] or weights['fulltext'] or weights['abstract'] or weights['keyword'] or weights['author'] or weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if language>
select cm.module_ident, count(*)*<dtml-var language> as weight, semilist(key) as keys
from (
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>

select module_ident, '<dtml-var q_item fmt=sql-quote>'::text ||'-::-language' as key
from 
latest_modules 
where
 language ~ ('^'||req('<dtml-var q_item fmt=sql-quote>'::text))
</dtml-in>
) cm

group by cm.module_ident


<dtml-if expr="weights['subject'] or weights['fulltext'] or weights['abstract'] or weights['keyword'] or weights['author'] or weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if subject>
select cm.module_ident, count(*)*<dtml-var subject> as weight, semilist(key) as keys
from (
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>

select module_ident, '<dtml-var q_item fmt=sql-quote>'::text ||'-::-subject' as key
from 
latest_modules natural join moduletags natural join tags 
where
 tag ~* req('<dtml-var q_item fmt=sql-quote>'::text)
</dtml-in>
) cm

group by cm.module_ident


<dtml-if expr="weights['fulltext'] or weights['abstract'] or weights['keyword'] or weights['author'] or weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if fulltext>
select cm.module_ident, sum(rank)*<dtml-var fulltext> as weight, semilist(key) as keys
from (
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>

select cm.module_ident, '<dtml-var q_item fmt=sql-quote>'::text ||'-::-fulltext' as key, rank_cd('{1.0,1.0,1.0,1.0}',module_idx,plainto_tsquery(<dtml-sqlvar q_item type=string>),4)*2^length(to_tsvector(<dtml-sqlvar q_item type=string>)) as rank
from 
latest_modules cm, modulefti mf

where
 cm.module_ident = mf.module_ident 
 and 
 module_idx @@ plainto_tsquery(<dtml-sqlvar q_item type=string>)

</dtml-in>
) cm

group by cm.module_ident


<dtml-if expr="weights['abstract'] or weights['keyword'] or weights['author'] or weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if abstract>

select cm.module_ident, count(*)*<dtml-var abstract> as weight, semilist(key) as keys

from 
( 
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select cm.module_ident, '<dtml-var q_item fmt=sql-quote>'::text ||'-::-abstract' as key

from latest_modules cm, abstracts a

where
 cm.abstractid = a.abstractid
 and 
 a.abstract ~* req('<dtml-var q_item fmt=sql-quote>'::text)
</dtml-in>

) cm

group by cm.module_ident


<dtml-if expr="weights['keyword'] or weights['author'] or weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if keyword>
select cm.module_ident, count(*)*<dtml-var keyword> as weight, semilist(key) as keys

from 
( 
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select cm.module_ident, '<dtml-var q_item fmt=sql-quote>'::text ||'-::-keyword' as key

from latest_modules cm, modulekeywords mk, keywords k

where
 cm.module_ident = mk.module_ident 
 and 
 mk.keywordid = k.keywordid
 and 
 k.word ~* req('<dtml-var q_item fmt=sql-quote>'::text)
</dtml-in>

) cm

group by cm.module_ident

<dtml-if expr="weights['author'] or weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if author>
select module_ident, count(*)*<dtml-var author> as weight, semilist(key) as keys

from 
( 
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-author' as key
from latest_modules m, persons ap

where
 ap.personid = any (m.authors)
 and 
 (
 ap.firstname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.surname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.fullname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or 
 ap.personid ~* ('^'||req('<dtml-var q_item fmt=sql-quote>'::text)||'$')
 or
 ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)||'.*@')
 or
 (ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)) 
   and 
 '<dtml-var q_item fmt=sql-quote>'::text  ~ '@' )
 )
</dtml-in>

) cm

group by cm.module_ident

<dtml-if expr="weights['editor'] or weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>
<dtml-if editor>
select module_ident, count(*)*<dtml-var editor> as weight, semilist(key) as keys

from
(
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-editor' as key
from latest_modules m natural join moduleoptionalroles mor natural join roles r, persons ap 

where
 ap.personid = any (mor.personids)
 and lower(r.rolename) = 'editor'
 and 
 (
 ap.firstname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.surname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.fullname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or 
 ap.personid ~* ('^'||req('<dtml-var q_item fmt=sql-quote>'::text)||'$')
 or
 ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)||'.*@')
 or
 (ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)) 
   and 
 '<dtml-var q_item fmt=sql-quote>'::text  ~ '@' )
 )
</dtml-in>

) cm

group by cm.module_ident

<dtml-if expr="weights['translator'] or weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>
<dtml-if translator>
select module_ident, count(*)*<dtml-var translator> as weight, semilist(key) as keys

from
(
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-translator' as key
from latest_modules m natural join moduleoptionalroles mor natural join roles r, persons ap 

where
 ap.personid = any (mor.personids)
 and lower(r.rolename) = 'translator'
 and 
 (
 ap.firstname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.surname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.fullname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or 
 ap.personid ~* ('^'||req('<dtml-var q_item fmt=sql-quote>'::text)||'$')
 or
 ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)||'.*@')
 or
 (ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)) 
   and 
 '<dtml-var q_item fmt=sql-quote>'::text  ~ '@' )
 )
</dtml-in>

) cm

group by cm.module_ident

<dtml-if expr="weights['maintainer'] or weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>
<dtml-if maintainer>
select module_ident, count(*)*<dtml-var maintainer> as weight, semilist(key) as keys

from
(
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-maintainer' as key
from latest_modules m, persons ap 

where
 ap.personid = any (m.maintainers)
 and 
 (
 ap.firstname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.surname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.fullname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or 
 ap.personid ~* ('^'||req('<dtml-var q_item fmt=sql-quote>'::text)||'$')
 or
 ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)||'.*@')
 or
 (ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)) 
   and 
 '<dtml-var q_item fmt=sql-quote>'::text  ~ '@' )
 )
</dtml-in>

) cm

group by cm.module_ident

<dtml-if expr="weights['licensor'] or weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>
<dtml-if licensor>
select module_ident, count(*)*<dtml-var licensor> as weight, semilist(key) as keys

from
(
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-licensor' as key
from latest_modules m natural join moduleoptionalroles mor natural join roles r, persons ap 

where
 ap.personid = any (mor.personids)
 and lower(r.rolename) = 'licensor'
 and 
 (
 ap.firstname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.surname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or
 ap.fullname ~* req('<dtml-var q_item fmt=sql-quote>'::text)
 or 
 ap.personid ~* ('^'||req('<dtml-var q_item fmt=sql-quote>'::text)||'$')
 or
 ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)||'.*@')
 or
 (ap.email ~* (req('<dtml-var q_item fmt=sql-quote>'::text)) 
   and 
 '<dtml-var q_item fmt=sql-quote>'::text  ~ '@' )
 )
</dtml-in>

) cm

group by cm.module_ident

<dtml-if expr="weights['exact_title'] or weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if exact_title>
select module_ident, count(*)*<dtml-var exact_title> as weight, semilist(key) as keys

from 
( 
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-title' as key
from latest_modules
where 
     name ~* ('(^| )'||req('<dtml-var q_item fmt=sql-quote>'::text)||'( |$)'::text)
</dtml-in>

) cm

group by cm.module_ident

<dtml-if expr="weights['title'] or weights['objectid']">
union all
</dtml-if>
</dtml-if>

<dtml-if title>
select module_ident, count(*)*<dtml-var title> as weight, semilist(key) as keys

from 
( 
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-title' as key
from latest_modules
where 
     name ~* req('<dtml-var q_item fmt=sql-quote>'::text)
</dtml-in>

) cm

group by cm.module_ident

<dtml-if objectid>
union all
</dtml-if>
</dtml-if>
<dtml-if objectid>
select module_ident, count(*)*<dtml-var objectid> as weight, semilist(key) as keys

from 
( 
<dtml-in query prefix="q">
<dtml-unless sequence-start>union all </dtml-unless>
select module_ident, '<dtml-var q_item fmt=sql-quote>'::text||'-::-objectid' as key
from latest_modules
where 
     moduleid = '<dtml-var q_item fmt=sql-quote>'::text
</dtml-in>

) cm

group by cm.module_ident
</dtml-if>
) as matched group by module_ident) as weighted
</dtml-if>
</dtml-with>
where 
    weighted.module_ident = lm.module_ident
<dtml-if min_rating>
    and round(mr.totalrating/greatest(mr.votes, 1)) >= <dtml-sqlvar min_rating type="float">
</dtml-if>
order by weight desc 
;
