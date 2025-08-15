import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha1
from typing import Any, Literal, Optional, Sequence


class QueryBase(ABC):
    """Base class for all queries."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        self.table_name = table_name

    @abstractmethod
    def make_query(self, *values: Any) -> str:
        """Return the query as a string."""


FROM_TO_TYPE = {
    "character varying": "varchar",
}

_ColumnType = Literal[
    "text",
    "boolean",
    "uuid",
    "jsonb",
    "varchar",
    "json",
    "timestamp with time zone",
]


@dataclass
class ColumnType:
    """Type of a column."""

    name: _ColumnType
    character_maximum_length: Optional[int] = None

    @property
    def query_name(self) -> str:
        """Return the query name of the column type."""
        if self.name == "varchar" and self.character_maximum_length is not None:
            return f"{self.name}({self.character_maximum_length})"
        return self.name

    @classmethod
    def from_string(cls, name: str) -> "ColumnType":
        """Return the column type from a string."""
        pattern = r"^(\w+)(?:\((\d+)(?:,(\d+))?\))?$"
        match = re.match(pattern, name)
        if match:
            return cls(name=match.group(1), character_maximum_length=match.group(2))
        return cls(name=name)


class Column(QueryBase):
    """Base class for all columns."""

    def __init__(
        self,
        name: str,
        type_: ColumnType,
        nullable: bool = False,
        default: Any = None,
        primary_key: bool = False,
    ) -> None:
        """Initialize the column."""
        self.name = name
        self.type = type_
        self.nullable = nullable
        self.default = default
        self.primary_key = primary_key
        self.comment = sha1(self.make_query().encode()).hexdigest()  # noqa: S324

    def make_query(self) -> str:
        """Return the column definition as a SQL string."""
        parts = [self.name, self.type]

        if not self.nullable:
            parts.append("NOT NULL")

        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")

        if self.primary_key:
            parts.append("PRIMARY KEY")

        return " ".join(parts)


class CreateTableQuery(QueryBase):
    """Query to create a table."""

    def __init__(self, table_name: str, columns: Sequence[Column]) -> None:
        """Initialize the query."""
        super().__init__(table_name)
        self.columns = columns

    def make_query(self) -> str:
        """Return the query as a string."""
        return (
            f"CREATE TABLE {self.table_name} "
            f"({', '.join(column.make_query() for column in self.columns)})"
        )


class IsTableExistsQuery(QueryBase):
    """Query to check if a table exists."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(self) -> str:
        """Return the query as a string."""
        return f"SELECT to_regclass('{self.table_name}') is not null"


class CommentColumnQuery(QueryBase):
    """Query to comment a column."""

    def __init__(self, table_name: str, column: Column) -> None:
        """Initialize the query."""
        super().__init__(table_name)
        self.column = column

    def make_query(self, comment: str) -> str:
        """Return the query as a string."""
        return f"COMMENT ON COLUMN {self.table_name}.{self.column.name} IS '{comment}'"


class GetColumnCommentQuery(QueryBase):
    """Query to get the comment of a column."""

    def __init__(self, table_name: str, column: Column) -> None:
        """Initialize the query."""
        super().__init__(table_name)
        self.column = column

    def make_query(self) -> str:
        """Return the query as a string."""
        return (
            f"SELECT col_description('{self.table_name}'::regclass, attnum) "  # noqa: S608
            f"FROM pg_attribute WHERE attrelid = '{self.table_name}'::regclass "
            f"AND attname = '{self.column.name}'"
        )


class CommentTableQuery(QueryBase):
    """Query to comment a table."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(self, comment: str) -> str:
        """Return the query as a string."""
        return f"COMMENT ON TABLE {self.table_name} IS '{comment}'"


class GetTableCommentQuery(QueryBase):
    """Query to get the comment of a table."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(self) -> str:
        """Return the query as a string."""
        return f"SELECT obj_description('{self.table_name}'::regclass) AS comment"


class GetTableColumnsDataQuery(QueryBase):
    """Query to get the data of a table."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(self, columns: Optional[Sequence[Column]] = None) -> str:
        """Return the query as a string."""
        return (
            "select c.column_name as name, data_type as type_, c.character_maximum_length as varchar_len,"  # noqa: E501, S608
            'c.is_nullable as nullable,c.column_default as "default",'
            "tc.constraint_type is not null and tc.constraint_type = 'PRIMARY KEY' as primary_key "  # noqa: E501
            'from information_schema."columns" as c '
            "left join information_schema.key_column_usage as kcu on "
            "c.column_name = kcu.column_name and c.table_name = kcu.table_name "
            "left join information_schema.table_constraints as tc on "
            "tc.table_name = c.table_name and c.table_schema = tc.table_schema "
            " and tc.constraint_name = kcu.constraint_name "
            f"where c.table_name = '{self.table_name}'"
            + (
                f" and c.column_name in ({', '.join(column.name for column in columns)})"
                if columns is not None
                else ""
            )
        )


class CreateIndexQuery(QueryBase):
    """Query to create an index."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(self, columns: Sequence[Column]) -> str:
        """Return the query as a string."""
        return "\n".join(
            "CREATE INDEX IF NOT EXISTS "
            f"{self.table_name}_{column.name}_idx "
            f"ON {self.table_name} USING HASH ({column.name});"
            for column in columns
        )


class InsertQuery(QueryBase):
    """Query to insert a row into a table."""

    def __init__(
        self,
        table_name: str,
    ) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(
        self,
        columns: Sequence[Column],
        returning: Optional[Sequence[Column]] = None,
    ) -> str:
        """Return the query as a string."""
        return (
            f"INSERT INTO {self.table_name} "  # noqa: S608
            f"({', '.join(column.name for column in columns)}) "
            f"VALUES ({', '.join(f'${i}' for i in range(1, len(columns) + 1))})"
            + (
                f" RETURNING {', '.join(column.name for column in returning)}"
                if returning is not None
                else ""
            )
        )


class InsertOrUpdateQuery(InsertQuery):
    """Query to insert or update a row into a table."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(
        self,
        columns: Sequence[Column],
        returning: Sequence[Column],
        on_conflict_columns: Sequence[Column],
        on_conflict_action: Literal["UPDATE", "NOTHING"] = "UPDATE",
        on_conflict_update_columns: Optional[Sequence[Column]] = None,
    ) -> str:
        """Return the query as a string."""
        insert_query = super().make_query(columns)
        returning_query = (
            f" RETURNING {', '.join(column.name for column in returning)}"
            if returning is not None
            else ""
        )
        if on_conflict_action == "UPDATE":
            if on_conflict_update_columns is None:
                raise ValueError(
                    "on_conflict_update_columns is required when "
                    "on_conflict_action is UPDATE",
                )

            set_query = ", ".join(
                f"{column.name} = EXCLUDED.{column.name}"
                for column in on_conflict_update_columns
            )
            conflict_query = ", ".join(column.name for column in on_conflict_columns)
            update_query = f"ON CONFLICT ({conflict_query}) DO UPDATE SET {set_query}"
            return f"{insert_query} {update_query} {returning_query}"

        return (
            f"{insert_query} ON CONFLICT ({', '.join(on_conflict_columns)}) DO NOTHING"
            + returning_query
        )


class DeleteQuery(QueryBase):
    """Query to delete a row from a table."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(self, column: Column) -> str:
        """Return the query as a string."""
        return f"DELETE FROM {self.table_name} WHERE {column.name} = $1"  # noqa: S608


class DeleteByDateQuery(QueryBase):
    """Query to delete a row from a table by date."""

    def __init__(self, table_name: str) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(self, column: Column) -> str:
        """Return the query as a string."""
        return f"DELETE FROM {self.table_name} WHERE {column.name} BETWEEN $1 AND $2"  # noqa: S608


class SelectQuery(QueryBase):
    """Query to select a row from a table."""

    def __init__(
        self,
        table_name: str,
    ) -> None:
        """Initialize the query."""
        super().__init__(table_name)

    def make_query(
        self,
        columns: Sequence[Column],
        where_columns: Optional[Sequence[Column]] = None,
    ) -> str:
        """Return the query as a string."""
        return (
            f"SELECT {', '.join(column.name for column in columns)} "  # noqa: S608
            f"FROM {self.table_name} "
            + (
                f"WHERE {' AND '.join(f'{column.name} = ${i}' for i, column in enumerate(where_columns, start=1))}"  # noqa: E501
                if where_columns is not None
                else ""
            )
        )


class CreatedAtColumn(Column):
    """Column for the created at timestamp."""

    def __init__(self) -> None:
        """Initialize the column."""
        super().__init__(
            "created_at",
            "TIMESTAMP WITH TIME ZONE",
            nullable=False,
            default="NOW()",
        )


class UpdatedAtColumn(Column):
    """Column for the updated at timestamp."""

    def __init__(self) -> None:
        """Initialize the column."""
        super().__init__(
            "updated_at",
            "TIMESTAMP WITH TIME ZONE",
            nullable=False,
            default="NOW()",
        )


class PrimaryKeyColumn(Column):
    """Column for the primary key."""

    def __init__(
        self,
        name: str = "id",
        type_: str = "UUID",
        default: Any = None,
    ) -> None:
        """Initialize the column."""
        super().__init__(name, type_, primary_key=True, default=default)
