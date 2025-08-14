synchronize_permissions("Blog")
synchronize_permissions("Card")
synchronize_permissions("File")
synchronize_permissions("Link")

add_relation_definition("Comment", "comments", "Card")
