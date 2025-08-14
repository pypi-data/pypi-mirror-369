"""schema customization for the intranet application

:organization: Logilab
:copyright: 2003-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb_blog.schema import BlogEntry
from cubicweb_card.schema import Card
from cubicweb_file.schema import File
from cubicweb_link.schema import Link
from yams.buildobjs import RelationDefinition
from yams.reader import context

PERMISSIONS = {
    "read": (
        "managers",
        "users",
        "guests",
    ),
    "add": (
        "managers",
        "users",
    ),
    "delete": (
        "managers",
        "owners",
    ),
    "update": (
        "managers",
        "users",
        "owners",
    ),
}

Card.__permissions__ = PERMISSIONS
BlogEntry.__permissions__ = PERMISSIONS
File.__permissions__ = PERMISSIONS
Link.__permissions__ = PERMISSIONS


class interested_in(RelationDefinition):
    subject = "CWUser"
    object = "Event"


BASETYPES: tuple[str, ...] = (
    "Card",
    "BlogEntry",
    "File",
    "Event",
    "Link",
    "Task",
    "Book",
)
if "VersionedFile" in context.defined:
    BASETYPES += ("VersionedFile",)
    from cubicweb_vcsfile.schema import VersionContent, VersionedFile

    VersionedFile.get_relation("name").fulltextindexed = True
    VersionContent.get_relation("data").fulltextindexed = True


class see_also(RelationDefinition):
    subject = BASETYPES
    object = BASETYPES


class comments(RelationDefinition):
    subject = "Comment"
    object = BASETYPES


class tags(RelationDefinition):
    subject = "Tag"
    object = BASETYPES
