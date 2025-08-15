from typing import Sequence

from taskiq_postgresql.abc.driver import QueryDriver
from taskiq_postgresql.abc.query import Column


class Migration:
    """Base class for all migrations."""

    def __init__(self, driver: QueryDriver, columns: Sequence[Column]) -> None:
        """Initialize the migration."""
        self.driver = driver
        self.columns = {column.name: column for column in columns}

    async def up(self) -> None:
        """Run the migration."""
        if not self.driver.exists_table(self.table_name):
            return await self.driver.create_table()

        table_columns: dict[str, Column] = {
            column.name: column for column in await self.driver.get_table_columns_data()
        }

        return None

    def down(self) -> None:
        """Run the migration."""
