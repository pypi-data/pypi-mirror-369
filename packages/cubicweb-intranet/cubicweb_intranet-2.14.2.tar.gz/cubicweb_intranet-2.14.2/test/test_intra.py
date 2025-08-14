"""intranet automatic tests"""

import os
import random
import unittest

from cubicweb import devtools
from cubicweb.devtools.fill import ValueGenerator
from cubicweb_web.devtools.testlib import (
    AutomaticWebTest,
    WebPostgresApptestConfiguration,
)


def setUpModule():
    """Ensure a PostgreSQL cluster is running and configured

    If PGHOST environment variable is defined, use existing PostgreSQL cluster
    running on PGHOST and PGPORT (default 5432).

    Or start a dedicated PostgreSQL cluster by using
    cubicweb.devtools.startpgcluster()
    """
    config = devtools.DEFAULT_PSQL_SOURCES["system"]
    if config["db-host"] != "REPLACEME":
        return
    if "PGHOST" in os.environ:
        config["db-host"] = os.environ["PGHOST"]
        config["db-port"] = os.environ.get("PGPORT", 5432)
        return
    devtools.startpgcluster(__file__)
    import atexit

    atexit.register(devtools.stoppgcluster, __file__)


class AutomaticWebTest(AutomaticWebTest):
    configcls = WebPostgresApptestConfiguration
    pass


def random_numbers(size):
    return "".join(random.choice("0123456789") for i in range(size))


class MyValueGenerator(ValueGenerator):
    def generate_Book_isbn10(self, entity, index):
        return random_numbers(10)

    def generate_Book_isbn13(self, entity, index):
        return random_numbers(13)


if __name__ == "__main__":
    unittest.main()
