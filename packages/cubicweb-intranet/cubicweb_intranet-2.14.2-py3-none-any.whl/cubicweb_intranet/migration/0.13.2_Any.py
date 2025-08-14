# add missing see_also relation definitions
see_also_schema = schema.rschema("see_also")

if "Versionedfile" in schema:
    for ttype in ("Card", "Blog", "File", "Image", "Link", "Versionedfile"):
        if not see_also_schema.has_rdef("Versionedfile", ttype):
            add_relation_definition("Versionedfile", "see_also", ttype)

for ttype in ("Card", "Blog", "File", "Image", "Link"):
    if not see_also_schema.has_rdef("Image", ttype):
        add_relation_definition("Image", "see_also", ttype)
