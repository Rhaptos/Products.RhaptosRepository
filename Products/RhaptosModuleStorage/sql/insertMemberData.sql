<dtml-comment>
arguments: id honorific="" firstname="" othername="" surname="" lineage="" fullname="" email="" homepage="" comment=""
</dtml-comment>

INSERT INTO persons (personid, honorific, firstname, othername, surname, lineage, fullname, email, homepage, comment)
VALUES (<dtml-sqlvar id type="string">, 
        <dtml-sqlvar honorific type="string">, 
        <dtml-sqlvar firstname type="string">,
        <dtml-sqlvar othername type="string">, 
        <dtml-sqlvar surname type="string">,
        <dtml-sqlvar lineage type="string">,
        <dtml-sqlvar fullname type="string">,
        <dtml-sqlvar email type="string">, 
        <dtml-sqlvar homepage type="string">,
        <dtml-sqlvar comment type="string">
);
