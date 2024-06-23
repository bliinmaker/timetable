"""Module for test runner."""


from types import MethodType
from typing import Any

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test.runner import DiscoverRunner


def prepare_db(self):
    """Create api_data schema."""
    self.connect()
    self.connection.cursor().execute('CREATE SCHEMA IF NOT EXISTS api_data;')


class PostgresSchemaRunner(DiscoverRunner):
    """Class for setuping database for tests."""

    def setup_databases(self, **kwargs: Any) -> list[tuple[BaseDatabaseWrapper, str, bool]]:
        """Set up databases.

        Returns:
            list[tuple[BaseDatabaseWrapper, str, bool]]: setup databases
        """
        for conn_name in connections:
            connection = connections[conn_name]
            connection.prepare_database = MethodType(prepare_db, connection)
        return super().setup_databases(**kwargs)
