select note.archival_object_id, archival_object.component_id from note, archival_object where note.archival_object_id=archival_object.id and note.notes like '%prefercite%';