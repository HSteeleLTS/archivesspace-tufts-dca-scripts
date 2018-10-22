 mysql -u libadmin -p -h libarcsdb-prod-01.uit.tufts.edu libaspace -e "select id from archival_object where id in (select archival_object_id from note where notes like '%prefercite%' and notes like '%false%')" > ~/archival_objects_prefercite_unpublished.txt

