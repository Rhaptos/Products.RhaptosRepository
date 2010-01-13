<dtml-comment>
arguments: md5:string length:int 
</dtml-comment>

SELECT fileid,file FROM files WHERE 
<dtml-sqltest md5 column="md5" type="string"> 
;
