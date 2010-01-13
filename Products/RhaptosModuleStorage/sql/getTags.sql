<dtml-comment>
arguments: tag:string scheme:string
</dtml-comment>

SELECT * 
FROM tags 
  <dtml-sqlgroup where>
    <dtml-sqltest tag type="string" optional>
    <dtml-and>
    <dtml-sqltest scheme type="string" optional>
  </dtml-sqlgroup>
