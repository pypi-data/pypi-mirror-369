from typing import Protocol, TypeAlias, Literal
import pathlib
from contextlib import contextmanager
import sqlite3
import psycopg
import warnings
from .core import Utils, Table, Column, Where, Join, OrderBy, SQL, convert_types
from .cross_domain_gimmick import CrossDomainGimmick

DBCursor:TypeAlias = sqlite3.Cursor | psycopg.Cursor
FILE_TYPE = Literal["csv", "json", "pickle"]
FILE_FUNCTION = {"json_in": Utils.json_to_records, 
                 "json_out": Utils.records_to_json, 
                 "csv_in": Utils.csv_to_records, 
                 "csv_out": Utils.records_to_csv}

class Database(Protocol):
    def close(self) -> None:
        self.connection.close()

    @contextmanager
    def cursor(self):
        cur = self.connection.cursor()
        try:
            yield cur
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cur.close()

    @property
    def connection(self) -> sqlite3.Connection | psycopg.Connection:
        ...
    @property
    def binding(self) -> str:
        ...
    @property
    def table_list(self) -> list[str]:
        ...
    def schema(self, cursor:DBCursor, table:str, cols:list=["*"]) -> Table | None:
        ...
    def table(self, table:str) -> str:
        ...
    def map_type(self, col:Column) -> str:
        ...

    def select(self, cursor:DBCursor, table:str, cols:list=["*"], where:Where=None, 
               join:Join=None, order_by:OrderBy=None, limit:int=0, schema:Table=None) -> list[tuple]:
        query, params = (SQL(f"SELECT {', '.join(cols)} FROM {self.table(table)}")
                         .optional_add(where)
                         .optional_add(join)
                         .optional_add(order_by)
                         .limit(limit)
                         .build(self.binding))
        rows = cursor.execute(query, params).fetchall()
        schema = schema if schema else self.schema(cursor, table, cols)
        return convert_types(schema, rows, "out")

    def insert(self, cursor:DBCursor, table:str, rows:list[tuple], cols:list=["*"], on_conflict_col:str="", where:Where=None, schema:Table=None) -> None:
        if not rows:
            warnings.warn(f"Attempted insert on table {table} with empty records. insert/insert_records/insert_file exited early.")
            return
        
        schema = schema if schema else self.schema(cursor, table, cols)
        rows = convert_types(schema, rows, "in")
        col_filter = "" if cols == ["*"] else f" ({', '.join(cols)})"
        sql = (SQL(f"INSERT INTO {self.table(table)}{col_filter}")
               .values(rows)
               .optional_add(where))
        if on_conflict_col:
            col_filter = schema.col_name_list if cols == ["*"] else cols
            sql = sql.update_on_conflict(col_filter, on_conflict_col)
        query, params = sql.build(self.binding)
        cursor.executemany(query, params)

    def update(self, cursor:DBCursor, table:str, rows:list[tuple], cols:list=["*"], on_column:str="", where:Where=None, schema:Table=None) -> None:
        if not rows:
            warnings.warn(f"Attempted update on table {table} with empty records. update/update_with_records/update_with_file exited early.")
            return
        
        schema = schema if schema else self.schema(cursor, table, cols)
        rows = convert_types(schema, rows, "in")
        cols = cols if cols == ["*"] else schema.col_name_list
        query, params = (SQL(f"UPDATE {self.table(table)} ")
                         .set_to_values(cols, rows, on_column)
                         .optional_add(where)
                         .build(self.binding))
        cursor.executemany(query, params)

    def delete(self, cursor:DBCursor, table:str, where:Where=None) -> None:
        query, params = (SQL(f"DELETE FROM {self.table(table)}")
                         .optional_add(where)
                         .build(self.binding))
        cursor.execute(query, params)

    def create_table(self, cursor:DBCursor, schema:Table) -> None:
        ...
    
    def create_table_with_records(self, cursor:DBCursor, table:str, records:list[dict], schema:Table=None) -> None:
        schema = schema if schema else Utils.evaluate_schema(table, records)
        self.create_table(cursor, schema)
        self.insert_records(cursor, table, records)
    
    def create_table_with_file(self, cursor:DBCursor, file_type:FILE_TYPE, file_path:str, table:str="", schema:Table=None) -> None:
        records = FILE_FUNCTION[f"{file_type}_in"](file_path)
        table = table if table else pathlib.Path(file_path).stem
        self.create_table_with_records(cursor, table, records, schema)

    def create_table_sql(self, schema:Table) -> SQL:
        sql = SQL(f"CREATE TABLE IF NOT EXISTS {self.table(schema.name)} (")
        for col in schema.columns:
            sql.append(f"{col.name} {self.map_type(col)}")
            if col.primary_key:
                sql.append(f" PRIMARY KEY")
            else:
                if col.unique:
                    sql.append(f" UNIQUE")
                if not col.nullable:
                    sql.append(f" NOT NULL")
            if col.default:
                sql.append(f" DEFAULT {col.default}")
            if col.check:
                sql.append(f" CHECK {col.check.query}", col.check.params)
            if col.foreign_keys:
                for fk in col.foreign_keys:
                    sql.append(f" REFERENCES {self.table(fk[0])} ({fk[1]})")
            sql.query.append(", ")
        
        sql.query[-1] = sql.query[-1][:-2] + ");"
        return sql

    def select_records(self, cursor:DBCursor, table:str, cols:list=["*"], where:Where=None, 
                       join:Join=None, order_by:OrderBy=None, limit:int=0, schema:Table=None) -> list[tuple]:
        schema = schema if schema else self.schema(cursor, table, cols)
        rows = self.select(cursor, table, cols, where, join, order_by, limit, schema)
        records = [{col.name: row[col.position - 1] for col in schema.columns} for row in rows]
        return records

    def insert_records(self, cursor:DBCursor, table:str, records:list[dict], on_conflict_col:str="", where:Where=None, schema:Table=None) -> None:
        cols = list(records[0].keys())
        table_rows = tuple(tuple(val for val in row.values()) for row in records)
        self.insert(cursor, table, table_rows, cols, on_conflict_col, where, schema)

    def update_with_records(self, cursor:DBCursor, table:str, records:list[dict], on_column:str="", where:Where=None, schema:Table=None) -> None:
        cols = list(records[0].keys())
        table_rows = tuple(tuple(val for val in row.values()) for row in records)
        self.update(cursor, table, table_rows, cols, on_column, where, schema)

    def select_file(self, cursor:DBCursor, table:str, file_type:FILE_TYPE, file_name:str="", save_path:str=".", cols:list=["*"], 
                    where:Where=None, join:Join=None, order_by:OrderBy=None, limit:int=0, schema:Table=None) -> None:
        records = self.select_records(cursor, table, cols, where, join, order_by, limit, schema)
        file_name = file_name if file_name else table
        FILE_FUNCTION[f"{file_type}_out"](file_name, records, save_path)

    def insert_file(self, cursor:DBCursor, table:str, file_type:FILE_TYPE, file_path:str, on_conflict_col:str="", where:Where=None, schema:Table=None) -> None:
        records = FILE_FUNCTION[f"{file_type}_in"](file_path)
        self.insert_records(cursor, table, records, on_conflict_col, where, schema)

    def update_with_file(self, cursor:DBCursor, table:str, file_type:FILE_TYPE, file_path:str, on_column:str="", where:Where=None, schema:Table=None) -> None:
        records = FILE_FUNCTION[f"{file_type}_in"](file_path)
        self.update_with_records(cursor, table, records, on_column, where, schema)

    def reflect_actions(self, byte_str:str):
        gimmick = CrossDomainGimmick.from_gibberish(byte_str)
        with self.cursor() as cur:
            for crud, action in gimmick.payload.items():
                match crud:
                    case "insert":
                        for i in action:
                            self.insert(cur, i["table"], i["rows"], i["cols"], i["on_conflict_col"], i["where"], i["schema"])
                    case "update":
                        for i in action:
                            self.update(cur, i["table"], i["rows"], i["cols"], i["on_column"], i["where"], i["schema"])
                    case "delete":
                        for i in action:
                            self.delete(cur, i["table"], i["where"])
                    case "insert_records":
                        for i in action:
                            self.insert_records(cur, i["table"], i["records"], i["on_conflict_col"], i["where"], i["schema"])
                    case "update_with_records":
                        for i in action:
                            self.update_with_records(cur, i["table"], i["records"], i["on_column"], i["where"], i["schema"])
                    case "create_table":
                        for i in action:
                            self.create_table(cur, i["schema"])
                    case "create_table_with_records":
                        for i in action:
                            self.create_table_with_records(cur, i["table"], i["records"])
                    case _:
                        pass