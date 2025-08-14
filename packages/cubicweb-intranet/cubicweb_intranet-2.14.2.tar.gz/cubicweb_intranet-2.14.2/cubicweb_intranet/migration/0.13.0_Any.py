add_relation_definition("Card", "see_also", "File")
add_relation_definition("Blog", "see_also", "File")
add_relation_definition("File", "see_also", "File")
add_relation_definition("Card", "see_also", "Link")
add_relation_definition("Blog", "see_also", "Link")
add_relation_definition("File", "see_also", "Link")
add_relation_definition("Link", "see_also", "Link")

synchronize_permissions("Blog")
synchronize_permissions("Card")
synchronize_permissions("File")
synchronize_permissions("Link")


rql("SET X see_also Y WHERE X concerns Y")

drop_relation_type("concerns")
