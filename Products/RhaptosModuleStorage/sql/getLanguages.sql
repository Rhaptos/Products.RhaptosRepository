<dtml-comment>
arguments: portal_types
</dtml-comment>

SELECT  language, count(*)
FROM latest_modules
<dtml-if portal_types>
WHERE
(
<dtml-in portal_types prefix="mod">
<dtml-unless mod_start>OR</dtml-unless> (
<dtml-sqltest mod_item column="portal_type" type="string"> )
</dtml-in> )
</dtml-if>
group by language order by count
