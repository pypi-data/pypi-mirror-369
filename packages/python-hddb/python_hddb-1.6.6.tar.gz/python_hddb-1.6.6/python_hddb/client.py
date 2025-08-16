import io
import json
import os
from functools import wraps
from typing import Any, Dict, List, Optional

import duckdb
import pandas as pd
from loguru import logger
from datetime import datetime
from .exceptions import ConnectionError, QueryError, TableExistsError
from .helpers import generate_field_metadata
from .models import FetchParams, FieldsParams
from .query_utils import (
    build_select_sql,
    build_where_sql,
    build_group_sql,
    build_order_sql,
    build_count_sql,
)


def attach_motherduck(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not os.environ.get("motherduck_token"):
            raise ValueError("Motherduck token has not been set")
        self.execute("ATTACH 'md:'")
        return func(self, *args, **kwargs)

    return wrapper


class HdDB:
    def __init__(self, motherduck_token="", read_only=False):
        try:
            if motherduck_token:
                os.environ["motherduck_token"] = motherduck_token
            self.conn = duckdb.connect(":memory:", read_only=read_only)
        except duckdb.Error as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def set_motherduck_token(self, motherduck_token: str):
        os.environ["motherduck_token"] = motherduck_token

    def execute(
        self, query: str, parameters: Optional[List[Any]] = None
    ) -> duckdb.DuckDBPyConnection:
        return self.conn.execute(query, parameters)

    def create_database(
        self, org: str, db: str, dataframes: List[pd.DataFrame], names: List[str]
    ):
        """
        Create in-memory database and create tables from a list of dataframes.

        :param dataframes: List of pandas DataFrames to create tables from
        :param names: List of names for the tables to be created
        :raises ValueError: If the number of dataframes doesn't match the number of table names
        :raises QueryError: If there's an error executing a query
        """
        if len(dataframes) != len(names):
            raise ValueError(
                "The number of dataframes must match the number of table names"
            )

        try:
            all_metadata = []
            for df, table_name in zip(dataframes, names):
                metadata = generate_field_metadata(df)

                # Create a mapping of original column names to new IDs
                columns = {field["label"]: field["id"] for field in metadata}

                # Rename the columns and convert to string, handling null values
                df_renamed = (
                    df.rename(columns=columns)
                    .astype(str)
                    .replace({"nan": "", "NaN": "", "None": ""})
                )

                self.conn.register("df_renamed", df_renamed)

                # Create the table with VARCHAR columns
                column_definitions = ", ".join(
                    f'"{col}" VARCHAR' for col in df_renamed.columns
                )

                create_table_query = f"CREATE TABLE {table_name} ({column_definitions})"
                self.execute(create_table_query)
                # Insert all data at once using the DataFrame directly
                self.execute(f"INSERT INTO {table_name} SELECT * FROM df_renamed")

                for field in metadata:
                    field["table"] = table_name
                all_metadata.extend(metadata)

            self.create_hd_tables()
            self.create_hd_database(org, db, len(dataframes))
            self.create_hd_fields(all_metadata)
            self.create_hd_views()
        except duckdb.Error as e:
            raise QueryError(f"Error executing query: {e}")

    def create_hd_database(self, org: str, db: str, tables: int):
        try:
            self.execute("BEGIN TRANSACTION;")

            create_query = "CREATE TABLE hd_database (id VARCHAR, username VARCHAR, slug VARCHAR, db_created_at TIMESTAMP DEFAULT current_timestamp, db_updated_at TIMESTAMP DEFAULT current_timestamp, db_n_tables INTEGER);"
            self.execute(create_query)

            insert_query = "INSERT INTO hd_database (id, username, slug, db_n_tables) VALUES (?, ?, ?, ?);"
            self.execute(insert_query, [f"{org}__{db}", org, db, tables])

            self.execute("COMMIT;")
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            raise QueryError(f"Error executing query: {e}")

    # TODO: map duckdb data types to datasketch types
    def create_hd_fields(self, metadata: List[Dict[str, str]]):
        try:
            # Create a temporary table with the metadata
            self.execute(
                "CREATE TEMP TABLE temp_metadata (fld___id VARCHAR, id VARCHAR, label VARCHAR, tbl VARCHAR)"
            )
            for field in metadata:
                self.execute(
                    "INSERT INTO temp_metadata VALUES (?, ?, ?, ?)",
                    (field["fld___id"], field["id"], field["label"], field["table"]),
                )

            # Join the temporary table with information_schema.columns
            self.execute(
                """
                CREATE TABLE hd_fields AS 
                SELECT 
                    tm.fld___id, 
                    tm.id, 
                    tm.label, 
                    ic.table_name AS tbl, 
                    'Txt' AS type
                FROM 
                    temp_metadata tm
                JOIN 
                    information_schema.columns ic 
                ON 
                    tm.tbl = ic.table_name AND tm.id = ic.column_name
            """
            )

            # Drop the temporary table
            self.execute("DROP TABLE temp_metadata")
        except duckdb.Error as e:
            logger.error(f"Error creating hd_fields: {e}")
            raise QueryError(f"Error creating hd_fields: {e}")

    def create_hd_tables(self):
        try:
            self.execute(
                "CREATE TABLE hd_tables AS SELECT table_name AS id, table_name AS label, estimated_size AS nrow, column_count AS ncol from duckdb_tables();"
            )
        except duckdb.Error as e:
            logger.error(f"Error creating hd_tables: {e}")
            raise QueryError(f"Error creating hd_tables: {e}")

    @attach_motherduck
    def upload_to_motherduck(self, org: str, db: str):
        """
        Upload the current database to Motherduck
        """
        try:
            self.execute(
                f'CREATE OR REPLACE DATABASE "{org}__{db}" from CURRENT_DATABASE();',
            )
        except duckdb.Error as e:
            logger.error(f"Error uploading database to MotherDuck: {e}")
            raise ConnectionError(f"Error uploading database to MotherDuck: {e}")

    @attach_motherduck
    def drop_database(self, org: str, db: str):
        """
        Delete a database stored in Motherduck

        :param org: Organization name
        :param db: Database name
        :raises ConnectionError: If there's an error deleting the database from Motherduck
        """
        try:
            self.execute(f'DROP DATABASE "{org}__{db}";')
            logger.info(f"Database {org}__{db} successfully deleted from Motherduck")
        except duckdb.Error as e:
            logger.error(f"Error deleting database from MotherDuck: {e}")
            raise QueryError(f"Error deleting database from MotherDuck: {e}")

    @attach_motherduck
    def get_data(self, org: str, db: str, tbl: str) -> dict:
        """
        Retrieve data and field information from a specified table in Motherduck

        :param org: Organization name
        :param db: Database name
        :param tbl: Table name
        :return: Dictionary containing 'data' and 'fields' properties as JSON objects
        :raises ConnectionError: If there's an error retrieving data from Motherduck
        """
        try:
            # Fetch data from the specified table
            data_query = f'SELECT * FROM "{org}__{db}"."{tbl}"'
            data = self.execute(data_query).fetch_df()

            # Fetch field information
            fields_query = f'SELECT * FROM "{org}__{db}".hd_fields WHERE tbl = ?'
            fields = self.execute(fields_query, [tbl]).fetch_df()

            # Convert all columns to string type first, then handle null values
            data = data.astype(str)
            data_json = json.loads(
                data.replace({"nan": "", "NaN": "", "None": ""}).to_json(
                    orient="records"
                )
            )
            fields_json = fields.to_dict(orient="records")

            return {"data": data_json, "fields": fields_json}
        except duckdb.Error as e:
            logger.error(f"Error retrieving data from MotherDuck: {e}")
            raise QueryError(f"Error retrieving data from MotherDuck: {e}")

    @attach_motherduck
    def get_data_chunk(self, org: str, db: str, tbl: str, params: FetchParams) -> dict:
        """
        Get a chunk of data with advanced sorting, filtering and grouping capabilities.

        Args:
            org (str): Organization name
            db (str): Database name
            tbl (str): Table name
            params (FetchParams): Query parameters including:
                - start_row (int): Starting row for pagination
                - end_row (int): Ending row for pagination
                - sort (str): Sorting condition
                - filter_model (Dict[str, FilterModel]): Filter conditions
                - row_group_cols (List[RowGroupCol]): Columns to group by
                - group_keys (List[str]): Selected group values

        Returns:
            dict: Contains:
                - data: List of records
                - count: Total number of records
        """
        try:
            end_row = params.end_row or 0
            start_row = params.start_row or 0
            page_size = end_row - start_row

            select_sql = build_select_sql(params)
            from_sql = f'FROM "{org}__{db}"."{tbl}"'
            where_sql = build_where_sql(params)
            group_sql = build_group_sql(params)
            order_sql = build_order_sql(params)
            limit_sql = f"LIMIT {page_size} OFFSET {start_row}"

            query = f"{select_sql} {from_sql} {where_sql} {group_sql} {order_sql} {limit_sql}"
            data = self.execute(query).fetchdf()

            count_query = build_count_sql(params, from_sql, where_sql)
            count = self.execute(count_query).fetchone()[0]

            return {"data": json.loads(data.to_json(orient="records")), "count": count}

        except duckdb.Error as e:
            logger.error(f"Error retrieving data from MotherDuck: {e}")
            raise QueryError(f"Error retrieving data from MotherDuck: {e}")

    @attach_motherduck
    def get_record_by_id(self, org: str, db: str, tbl: str, id: str) -> dict:
        """
        Retrieve a record by its ID from a specified table in Motherduck

        :param org: Organization name
        :param db: Database name
        :param tbl: Table name
        :param id: Record ID
        :return: Dictionary containing the record data and fields, or null values if no data found
        """
        try:
            # Obtener el registro como DataFrame
            result_df = self.execute(
                f'SELECT * FROM "{org}__{db}"."{tbl}" WHERE rcd___id = ?', [id]
            ).fetch_df()

            if not result_df.empty:
                # Convertir la primera fila del DataFrame a un diccionario
                record_dict = result_df.iloc[0].to_dict()
                # Obtener los campos
                fields_query = f'SELECT * FROM "{org}__{db}".hd_fields WHERE tbl = ?'
                fields = self.execute(fields_query, [tbl]).fetchdf()
                fields_json = fields.to_dict(orient="records")

                return {"data": record_dict, "fields": fields_json}
            else:
                return {"data": None, "fields": None}
        except duckdb.Error as e:
            logger.error(f"Error retrieving record from MotherDuck: {e}")
            raise QueryError(f"Error retrieving record from MotherDuck: {e}")

    @attach_motherduck
    def drop_table(self, org: str, db: str, tbl: str):
        """
        Deletes a specific table from the database in Motherduck

        :param org: Organization name
        :param db: Database name
        :param tbl: Table name
        :raises ConnectionError: Si hay un error al eliminar la tabla de Motherduck
        """
        try:
            self.execute("BEGIN TRANSACTION;")
            try:
                self.execute(f'DROP TABLE IF EXISTS "{org}__{db}"."{tbl}";')

                self.execute(f'DELETE FROM "{org}__{db}".hd_tables WHERE id = ?', [tbl])
                self.execute(
                    f'DELETE FROM "{org}__{db}".hd_fields WHERE tbl = ?', [tbl]
                )

                self.execute("COMMIT;")
            except Exception as e:
                self.execute("ROLLBACK;")
                raise e

            logger.info(
                f"Table {tbl} successfully deleted from database {org}__{db} in Motherduck and its record in hd_data has been removed"
            )
        except duckdb.Error as e:
            logger.error(f"Error deleting table from MotherDuck: {e}")
            raise QueryError(f"Error deleting table from MotherDuck: {e}")

    @attach_motherduck
    def add_table(self, org: str, db: str, tbl: str, df: pd.DataFrame):
        """
        Adds a new table to an existing database in MotherDuck and registers it in hd_tables and hd_fields.

        :param org: Organization name
        :param db: Database name
        :param tbl: Name of the new table
        :param df: Pandas DataFrame containing the data to be added
        :raises ConnectionError: If there's an error adding the table to MotherDuck
        """
        try:
            # Generate metadata for the new table
            metadata = generate_field_metadata(df)

            # Create a mapping of original column names to new IDs and rename columns
            df_renamed = (
                df.rename(columns={field["label"]: field["id"] for field in metadata})
                .astype(str)
                .replace({"nan": "", "NaN": "", "None": ""})
            )

            # register table for duckdb
            self.conn.register("df_renamed", df_renamed)

            # Begin transaction
            self.execute("BEGIN TRANSACTION;")

            # Create the new table with all columns as VARCHAR
            column_definitions = ", ".join(
                [f'"{col}" VARCHAR' for col in df_renamed.columns]
            )

            create_table_query = (
                f'CREATE TABLE "{org}__{db}"."{tbl}" ({column_definitions})'
            )

            self.execute(create_table_query)

            insert_query = f'INSERT INTO "{org}__{db}"."{tbl}" SELECT * FROM df_renamed'

            self.execute(insert_query)

            # Insert into hd_tables
            self.execute(
                f'INSERT INTO "{org}__{db}".hd_tables (id, label, nrow, ncol) VALUES (?, ?, ?, ?)',
                [tbl, tbl, len(df), len(df.columns)],
            )

            self.execute(
                "CREATE TEMP TABLE temp_metadata (fld___id VARCHAR, id VARCHAR, label VARCHAR, tbl VARCHAR)"
            )

            for field in metadata:
                self.execute(
                    "INSERT INTO temp_metadata VALUES (?, ?, ?, ?)",
                    (field["fld___id"], field["id"], field["label"], tbl),
                )

            # Insertar en hd_fields usando una consulta JOIN, pero siempre usando 'Txt' como tipo
            self.execute(
                f"""
            INSERT INTO "{org}__{db}".hd_fields (fld___id, id, label, tbl, type)
            SELECT
                tm.fld___id,
                tm.id,
                tm.label,
                '{tbl}' AS tbl,
                'Txt' AS type
            FROM
                temp_metadata tm
            """
            )

            # Eliminar la tabla temporal
            self.execute("DROP TABLE temp_metadata")

            # Commit transaction
            self.execute("COMMIT;")

        except (duckdb.CatalogException, duckdb.Error) as e:
            self.execute("ROLLBACK;")
            if isinstance(e, duckdb.CatalogException):
                logger.error(f"Table with name {tbl} already exists: {e}")
                raise TableExistsError(f"Table with name {tbl} already exists: {e}")
            else:
                logger.error(f"Error adding table to MotherDuck: {e}")
                raise QueryError(f"Error adding table to MotherDuck: {e}")
        except Exception as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error adding table to MotherDuck: {e}")
            raise QueryError(f"Error adding table to MotherDuck: {e}")

    @attach_motherduck
    def download_data(
        self, org: str, db: str, tbl: str, format: str = "csv", fields: List[str] = None
    ) -> io.BytesIO:
        """
        Download data from a specified table in CSV or JSON format, using original column names.

        Args:
            org (str): The organization name.
            db (str): The database name.
            tbl (str): The table name.
            format (str, optional): The output format ('csv' or 'json'). Defaults to 'csv'.
            fields (List[str], optional): The fields to include in the export. Defaults to None.

        Returns:
            io.BytesIO: A BytesIO object containing the exported data.

        Raises:
            ValueError: If an invalid format is specified.
            duckdb.Error: If there's an error executing the query or writing the file.
        """
        if format not in ["csv", "json"]:
            raise ValueError("Format must be either 'csv' or 'json'")

        try:
            # Construct the full table name
            full_table_name = f'"{org}__{db}".{tbl}'

            # Get the original column names from hd_fields
            original_names_query = f"""
            SELECT id, label
            FROM "{org}__{db}".hd_fields
            WHERE tbl = '{tbl}'
            """
            original_names = self.execute(original_names_query).fetchdf()

            # Filter original_names if fields is provided
            if fields is not None:
                original_names = original_names[original_names["id"].isin(fields)]

            # Construct the SELECT statement with original column names, excluding rcd___id from the header
            select_stmt = ", ".join(
                [
                    f'"{row.id}" AS "{row.label}"'
                    for _, row in original_names.iterrows()
                    if row.id != "rcd___id"
                ]
            )

            # Prepare the query
            query = f"SELECT {select_stmt} FROM {full_table_name}"

            # Execute query and return as BytesIO
            result = self.execute(query).fetchdf()

            buffer = io.BytesIO()
            if format == "csv":
                result.to_csv(buffer, index=False)
            else:  # json
                result.to_json(buffer, orient="records")
            buffer.seek(0)
            logger.info(f"Data from table {tbl} successfully exported to memory")
            return buffer

        except duckdb.Error as e:
            logger.error(f"Error downloading / exporting data from table {tbl}: {e}")
            raise

    @attach_motherduck
    def update_table_data(
        self, org: str, db: str, tbl: str, field: str, value: str, rcd___id: str
    ) -> bool:
        """
        Update a specific field in a table for a given record.

        :param org: Organization name
        :param db: Database name
        :param table: Table name
        :param field: Field to update
        :param value: New value for the field
        :param rcd___id: Record ID to update
        :return: True if update was successful
        :raises ConnectionError: If there's an error updating data in MotherDuck
        """
        try:
            query = f'UPDATE "{org}__{db}"."{tbl}" SET "{field}" = ? WHERE rcd___id = ?'
            self.execute(query, [value, rcd___id])
            return True
        except duckdb.Error as e:
            logger.error(f"Error updating data in MotherDuck: {e}")
            raise QueryError(f"Error updating data in MotherDuck: {e}")

    def close(self):
        try:
            self.conn.close()
            logger.info("Database connection closed")
        except duckdb.Error as e:
            logger.error(f"Error closing connection: {e}")

    @attach_motherduck
    def delete_table_data(self, org: str, db: str, tbl: str, rcd___id: str) -> bool:
        """
        Delete a specific row from a table.

        :param org: Organization name
        :param db: Database name
        :param tbl: Table name
        :param rcd___id: Record ID to delete
        :return: True if deletion was successful
        :raises ConnectionError: If there's an error deleting data in MotherDuck
        """
        try:
            self.execute("BEGIN TRANSACTION;")
            query = f'DELETE FROM "{org}__{db}"."{tbl}" WHERE rcd___id = ?'
            self.execute(query, [rcd___id])
            query = f'UPDATE "{org}__{db}".hd_tables SET nrow = nrow - 1 WHERE id = ?'
            self.execute(query, [tbl])
            self.execute("COMMIT;")
            logger.info(
                f"Row with rcd___id {rcd___id} successfully deleted from table {tbl}"
            )
            return True
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error deleting data in MotherDuck: {e}")
            raise QueryError(f"Error deleting data in MotherDuck: {e}")

    @attach_motherduck
    def add_row(self, org: str, db: str, tbl: str, row: dict):
        try:
            columns = ", ".join(f'"{k}"' for k in row.keys())
            placeholders = ", ".join(["?" for _ in row])

            self.execute("BEGIN TRANSACTION;")
            query = (
                f'INSERT INTO "{org}__{db}"."{tbl}" ({columns}) VALUES ({placeholders})'
            )
            self.execute(query, list(row.values()))
            self.execute(
                f'UPDATE "{org}__{db}".hd_tables SET nrow = nrow + 1 WHERE id = ?',
                [tbl],
            )
            self.execute("COMMIT;")
            return True
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error adding row to table {tbl}: {e}")
            raise QueryError(f"Error adding row to table {tbl}: {e}")

    @attach_motherduck
    def add_column(self, org: str, db: str, tbl: str, column: dict):
        try:
            self.execute("BEGIN TRANSACTION;")
            self.execute(
                f'ALTER TABLE "{org}__{db}"."{tbl}" ADD COLUMN "{column["slug"]}" VARCHAR'
            )
            self.execute(
                f'UPDATE "{org}__{db}".hd_tables SET ncol = ncol + 1 WHERE id = ?',
                [tbl],
            )
            self.execute(
                f'INSERT INTO "{org}__{db}".hd_fields (fld___id, id, label, tbl, type) VALUES (?, ?, ?, ?, ?)',
                [
                    column["fld___id"],
                    column["slug"],
                    column["headerName"],
                    tbl,
                    column["type"],
                ],
            )
            self.execute("COMMIT;")
            return True
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error adding column to table {tbl}: {e}")
            raise QueryError(f"Error adding column to table {tbl}: {e}")

    @attach_motherduck
    def delete_column(self, org: str, db: str, tbl: str, column: dict):
        try:
            column_name = column["slug"]
            column_id = column["fld___id"]
            self.execute("BEGIN TRANSACTION;")
            self.execute(
                f'ALTER TABLE "{org}__{db}"."{tbl}" DROP COLUMN "{column_name}"'
            )
            self.execute(
                f'UPDATE "{org}__{db}".hd_tables SET ncol = ncol - 1 WHERE id = ?',
                [tbl],
            )
            self.execute(
                f'DELETE FROM "{org}__{db}".hd_fields WHERE fld___id = ? AND tbl = ?',
                [column_id, tbl],
            )
            self.execute("COMMIT;")
            return True
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error deleting column from table {tbl}: {e}")
            raise QueryError(f"Error deleting column from table {tbl}: {e}")

    @attach_motherduck
    def upload_bulk_data(
        self, org: str, db: str, tbl: str, data: pd.DataFrame, is_json: bool = False
    ):
        try:
            # Fetch the column names and their order from the actual table
            table_columns = self.execute(f'DESCRIBE "{org}__{db}"."{tbl}"').fetchall()
            table_column_names = [col[0] for col in table_columns]

            if not is_json:
                # Fetch the column labels and ids from hd_fields
                hd_fields = self.execute(
                    f'SELECT id, label FROM "{org}__{db}".hd_fields WHERE tbl = ?',
                    [tbl],
                ).fetchall()
                hd_fields_dict = {field[1]: field[0] for field in hd_fields}
                hd_fields_reverse_dict = {field[0]: field[1] for field in hd_fields}

                # Create a mapping from data column names to table column names
                column_mapping = {}
                for data_col in data.columns:
                    if data_col in hd_fields_dict:
                        column_mapping[data_col] = hd_fields_dict[data_col]
                    else:
                        column_mapping[data_col] = (
                            data_col  # Keep unmapped columns as is
                        )

                # Check if all required columns are present in the data and identify extra columns
                missing_columns = set(table_column_names) - set(column_mapping.values())
                extra_columns = set(column_mapping.values()) - set(table_column_names)

                if missing_columns or extra_columns:
                    error_message = []
                    if missing_columns:
                        missing_labels = [
                            hd_fields_reverse_dict.get(col, col)
                            for col in missing_columns
                        ]
                        error_message.append(
                            f"Missing columns in data: {', '.join(missing_labels)}"
                        )
                    if extra_columns:
                        extra_labels = [
                            hd_fields_reverse_dict.get(col, col)
                            for col in extra_columns
                        ]
                        error_message.append(
                            f"Extra columns in data: {', '.join(extra_labels)}"
                        )
                    raise ValueError(". ".join(error_message))

                # Reorder and rename the columns in the DataFrame to match the table structure
                data_reordered = data.rename(columns=column_mapping)[table_column_names]
            else:
                # Verify that all columns in the data exist in the table
                missing_columns = set(table_column_names) - set(data.columns)
                extra_columns = set(data.columns) - set(table_column_names)
                if missing_columns or extra_columns:
                    error_message = []
                    if missing_columns:
                        error_message.append(
                            f"Missing columns in data: {', '.join(missing_columns)}"
                        )
                    if extra_columns:
                        error_message.append(
                            f"Extra columns in data: {', '.join(extra_columns)}"
                        )
                    raise ValueError(". ".join(error_message))
                data_reordered = data[table_column_names]

            self.execute("BEGIN TRANSACTION;")

            # Register the DataFrame as a table in DuckDB
            self.conn.register("data_reordered", data_reordered)

            # Insert data into the table
            self.execute(
                f'INSERT INTO "{org}__{db}"."{tbl}" SELECT * FROM data_reordered'
            )

            # Get the number of rows inserted
            rows_inserted = len(data)

            # Update the number of rows in hd_tables
            self.execute(
                f"""
                UPDATE "{org}__{db}".hd_tables 
                SET nrow = nrow + ? 
                WHERE id = ?
            """,
                [rows_inserted, tbl],
            )

            self.execute("COMMIT;")
            return True
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error uploading bulk data to table {tbl}: {e}")
            raise QueryError(f"Error uploading bulk data to table {tbl}: {e}")
        except ValueError as e:
            logger.error(str(e))
            raise QueryError(str(e))

    @attach_motherduck
    def update_hd_fields(self, org: str, db: str, fld___id: str, label: str, type: str):
        try:
            query = f'UPDATE "{org}__{db}".hd_fields SET label = ?, type = ? WHERE fld___id = ?'
            self.execute(query, [label, type, fld___id])
        except duckdb.Error as e:
            logger.error(f"Error updating hd_fields: {e}")
            raise QueryError(f"Error updating hd_fields: {e}")

    @attach_motherduck
    def update_row(self, org: str, db: str, tbl: str, id: str, data: dict):
        try:
            # 1️⃣ Consultar los tipos de las columnas
            type_query = f"""
                SELECT label, type
                FROM "{org}__{db}".hd_views
                WHERE tbl = '{tbl}'
            """
            column_types = {row[0]: row[1] for row in self.execute(type_query)}

            # 2️⃣ Procesar valores con base en el tipo
            processed_values = []
            for key, value in data.items():
                col_type = column_types.get(key)

                if col_type in ("Dtm", "Date") and isinstance(value, int):
                    value = datetime.utcfromtimestamp(value)
                    if col_type == "Date":
                        value = value.strftime("%Y-%m-%d")
                    elif col_type == "Dtm":
                        value = value.strftime("%Y-%m-%d %H:%M:%S")

                processed_values.append(value)

            # 3️⃣ Armar y ejecutar el query
            update_query = f'UPDATE "{org}__{db}".{tbl} SET '
            update_query += ", ".join([f"{key} = ?" for key in data.keys()])
            update_query += " WHERE rcd___id = ?"

            self.execute(update_query, processed_values + [id])
        except duckdb.Error as e:
            logger.error(f"Error updating row in table {tbl}: {e}")
            raise QueryError(f"Error updating row in table {tbl}: {e}")

    @attach_motherduck
    def get_fields(
        self,
        org: str,
        db: str,
        tbl: Optional[str] = None,
        params: Optional[FieldsParams] = None,
    ) -> list:
        """
        Retrieve fields from the hd_fields table for a given table.
        :param org: Organization name
        :param db: Database name
        :param tbl: Table name
        :return: List of fields from hd_fields table
        :raises QueryError: If there's an error fetching fields from MotherDuck
        """
        try:
            query = f'SELECT fld___id, id, label, type FROM "{org}__{db}".hd_fields'
            if tbl is not None:
                query += " WHERE tbl = ?"
            result = self.execute(query, [tbl] if tbl is not None else None).fetchdf()
            data = json.loads(result.to_json(orient="records"))

            if params and params.with_categories:
                for row in data:
                    column_type, column_id = row.get("type"), row.get("id")
                    if column_type == "Cat":
                        # Escapar el nombre de la columna con comillas dobles
                        query = (
                            f'SELECT DISTINCT("{column_id}") FROM "{org}__{db}"."{tbl}"'
                        )
                        try:
                            categories = self.execute(query).fetchall()
                            row["categories"] = [
                                c[0] for c in categories if c[0] is not None
                            ]
                        except duckdb.Error as cat_error:
                            logger.warning(
                                f"Error fetching categories for column '{column_id}': {cat_error}"
                            )
                            row["categories"] = []

            return {"data": data}
        except duckdb.Error as e:
            logger.error(f"Error fetching fields from hd_fields: {e}")
            raise QueryError(f"Error fetching fields from hd_fields: {e}")

    @attach_motherduck
    def get_metadata(self, org: str, db: str, tbl: str):
        try:
            query = f'SELECT * FROM "{org}__{db}".hd_tables WHERE id = ?'
            result = self.execute(query, [tbl]).fetchdf()

            data = result.to_dict(orient="records")
            if not data:
                raise QueryError(f"Table '{tbl}' not found in database '{org}__{db}'")

            # Obtener los valores con fallback a valores por defecto
            row_data = data[0]
            metadata = {
                "nrow": float(row_data.get("tb_n_rows", row_data.get("nrow", 0))),
                "ncol": float(row_data.get("tb_n_columns", row_data.get("ncol", 0))),
                "tbl_name": row_data.get("id", tbl),
                "label": row_data.get("label", tbl),
                "description": row_data.get("description"),
                "created_at": row_data.get("tb_created_at"),
                "updated_at": row_data.get("tb_updated_at"),
                "magnitude": float(row_data.get("tb_magnitude", 0)),
            }
            return metadata

        except duckdb.Error as e:
            logger.error(f"Error fetching metadata from hd_tables: {e}")
            raise QueryError(f"Error fetching metadata from hd_tables: {e}")

    @attach_motherduck
    def get_hd_fields(self, org: str, db: str, tbl: str):
        """
        Retrieve fields from the hd_fields table for a given table.

        :param org: Organization name
        :param db: Database name
        :param tbl: Table name
        :return: List of fields from hd_fields table
        :raises QueryError: If there's an error fetching fields from MotherDuck
        """
        try:
            query = f'SELECT * FROM "{org}__{db}".hd_fields WHERE tbl = ?'
            result = self.execute(query, [tbl]).fetchdf()
            return result.to_dict(orient="records")
        except duckdb.Error as e:
            raise QueryError(f"Error fetching hd_fields: {e}")

    @attach_motherduck
    def update_records(
        self, org: str, db: str, tbl: str, updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update multiple records in a table in a single transaction.

        Args:
            org (str): Organization name
            db (str): Database name
            tbl (str): Table name
            updates (List[Dict[str, Any]]): List of dictionaries containing updates.
                Each dictionary must have:
                - 'rcd___id': The record ID to update
                - Any other key-value pairs representing the columns to update

        Returns:
            bool: True if updates were successful

        Raises:
            QueryError: If there's an error updating the records
            ValueError: If updates list is empty or missing required fields
        """
        if not updates:
            raise ValueError("Updates list cannot be empty")

        try:
            self.execute("BEGIN TRANSACTION;")

            for update in updates:
                if "rcd___id" not in update:
                    raise ValueError("Each update must contain 'rcd___id'")

                record_id = update["rcd___id"]
                # Remove rcd___id from the update data
                update_data = {k: v for k, v in update.items() if k != "rcd___id"}

                if not update_data:
                    continue  # Skip if no fields to update

                # Construct the UPDATE query
                set_clause = ", ".join([f'"{k}" = ?' for k in update_data.keys()])
                query = (
                    f'UPDATE "{org}__{db}"."{tbl}" SET {set_clause} WHERE rcd___id = ?'
                )

                # Execute the UPDATE query with all values plus the record_id
                self.execute(query, list(update_data.values()) + [record_id])

            self.execute("COMMIT;")
            logger.info(f"Successfully updated {len(updates)} records in table {tbl}")
            return True

        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error updating records in table {tbl}: {e}")
            raise QueryError(f"Error updating records in table {tbl}: {e}")

    @attach_motherduck
    def clear_column_values(
        self, org: str, db: str, tbl: str, column: str, value: str
    ) -> bool:
        """
        Clear values in a specific column that match a given value.

        Args:
            org (str): Organization name
            db (str): Database name
            tbl (str): Table name
            column (str): Column label to clear values from
            value (str): Value to match and clear

        Returns:
            bool: True if operation was successful

        Raises:
            QueryError: If there's an error executing the query
        """
        try:
            # Verify if the column exists by querying hd_fields
            check_query = f"""
                SELECT id 
                FROM "{org}__{db}".hd_fields 
                WHERE tbl = ? AND id = ?
            """
            result = self.execute(check_query, [tbl, column]).fetchone()

            if not result:
                raise QueryError(f"Column '{column}' not found in table '{tbl}'")

            column_id = result[0]

            # Begin transaction
            self.execute("BEGIN TRANSACTION;")

            # Update the values to empty string where they match
            update_query = f"""
                UPDATE "{org}__{db}"."{tbl}" 
                SET "{column_id}" = ''
                WHERE "{column_id}" = ?
            """
            self.execute(update_query, [value])

            self.execute("COMMIT;")
            logger.info(
                f"Successfully cleared values matching '{value}' in column '{column}' of table '{tbl}'"
            )
            return True

        except (duckdb.Error, Exception) as e:
            self.execute("ROLLBACK;")
            logger.error(f"Error clearing values in column: {e}")
            raise QueryError(f"Error clearing values in column: {e}")

    @attach_motherduck
    def get_tables(self, org: str, db: str):
        try:
            query = f'SELECT id FROM "{org}__{db}".hd_tables'
            result = self.execute(query).fetchall()
            return [row[0] for row in result]
        except (duckdb.Error, Exception) as e:
            logger.error(f"Error fetching tables: {e}")
            raise QueryError(f"Error fetching tables: {e}")

    def create_hd_views(self):
        try:
            self.execute("BEGIN TRANSACTION;")

            # Crear la tabla en el esquema actual
            create_query = "CREATE TABLE hd_views (id VARCHAR, user_table VARCHAR, type VARCHAR, config JSON);"
            self.execute(create_query)

            self.execute("COMMIT;")

            return True
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            raise QueryError(f"Error executing query: {e}")

    @attach_motherduck
    def insert_hd_views(
        self, org: str, db: str, id: str, tbl: str, type: str, config: dict
    ):
        try:
            # Verificar si existe la tabla hd_views
            check_query = f"""
                SELECT table_catalog, table_name 
                FROM information_schema.tables 
                WHERE table_name = 'hd_views' 
                AND table_catalog = '{org}__{db}'
            """
            result = self.execute(check_query).fetchone()

            # Si no existe la tabla, crearla
            if not result:
                self.execute("BEGIN TRANSACTION;")
                create_query = f'CREATE TABLE "{org}__{db}".hd_views (id VARCHAR, user_table VARCHAR, type VARCHAR, config JSON);'
                self.execute(create_query)
                self.execute("COMMIT;")

            # Insertar el registro
            insert_query = f'INSERT INTO "{org}__{db}".hd_views (id, user_table, type, config) VALUES (?, ?, ?, ?);'
            self.execute(insert_query, [id, tbl, type, config])
        except duckdb.Error as e:
            raise QueryError(f"Error executing query: {e}")

    @attach_motherduck
    def update_hd_views(self, org: str, db: str, id: str, config: dict):
        try:
            update_query = f'UPDATE "{org}__{db}".hd_views SET config = ? WHERE id = ?'
            self.execute(update_query, [config, id])
        except duckdb.Error as e:
            raise QueryError(f"Error executing query: {e}")

    @attach_motherduck
    def delete_hd_views(self, org: str, db: str, id: str):
        try:
            delete_query = f'DELETE FROM "{org}__{db}".hd_views WHERE id = ?'
            self.execute(delete_query, [id])
        except duckdb.Error as e:
            raise QueryError(f"Error executing query: {e}")

    @attach_motherduck
    def get_hd_views(self, org: str, db: str, id: str):
        try:
            query = f'SELECT * FROM "{org}__{db}".hd_views WHERE id = ?'
            result = self.execute(query, [id]).fetchdf()
            return result.to_dict(orient="records")[0]
        except duckdb.Error as e:
            raise QueryError(f"Error executing query: {e}")

    @attach_motherduck
    def create_geo_table(self, org: str, db: str, tbl: str, df: pd.DataFrame):
        try:
            self.execute("BEGIN TRANSACTION;")

            self.execute("INSTALL spatial;")
            self.execute("LOAD spatial;")

            self.conn.register("df", df)

            # Crear la tabla en el esquema actual
            create_query = f'CREATE TABLE "{org}__{db}"."{tbl}" (id VARCHAR, properties JSON, geometry GEOMETRY);'

            insert_query = f'INSERT INTO "{org}__{db}"."{tbl}" SELECT id, properties, ST_GeomFromWKB(geometry) FROM df;'

            self.execute(create_query)
            self.execute(insert_query)

            self.execute("COMMIT;")

            return True
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            raise QueryError(f"Error executing query: {e}")

    @attach_motherduck
    def get_geo_table_by_shape(self, org: str, db: str, tbl: str, shape: tuple):
        try:
            self.execute("BEGIN TRANSACTION;")

            self.execute("INSTALL spatial;")
            self.execute("LOAD spatial;")

            query = f'SELECT id, properties, ST_AsWKB(geometry) as geometry FROM "{org}__{db}"."{tbl}" WHERE ST_Within(geometry, ST_MakeEnvelope({shape[0]}, {shape[1]}, {shape[2]}, {shape[3]}))'
            result = self.execute(query).fetchdf()

            self.execute("COMMIT;")

            return result
        except duckdb.Error as e:
            self.execute("ROLLBACK;")
            raise QueryError(f"Error executing query: {e}")
