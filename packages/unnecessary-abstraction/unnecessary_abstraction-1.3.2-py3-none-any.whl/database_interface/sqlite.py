import atexit
import sqlite3

from .database import Database
from .core import Table, Column

class SQLite(Database):
    def __init__(self, path:str=":memory:", foreign_keys:bool=False):
        self.__binding:str = "?"
        self.__conn = sqlite3.Connection(path)
        if foreign_keys:
            with self.cursor() as cur:
                cur.execute("PRAGMA foreign_keys = ON")
        
        atexit.register(self.close)

    @property
    def connection(self) -> sqlite3.Connection:
        return self.__conn
    @property
    def binding(self) -> str:
        return self.__binding
    @property
    def table_list(self) -> tuple[str]:
        with self.cursor() as cur:
            cur.execute("SELECT name FROM sqlite_master")
        return tuple(table[0] for table in cur.fetchall())

    def schema(self, cursor:sqlite3.Cursor, table:str, cols:list=["*"]) -> Table:
        res = cursor.execute(f"PRAGMA table_info({self.table(table)})").fetchall()
        if not res:
            return None

        if cols == ["*"]:
            return Table(table, tuple(Column(res_col[1], res_col[2], res_col[0]) for res_col in res))
        else:
            return Table(table, [Column(res_col[1], res_col[2], pos) 
                                 for pos, col in enumerate(cols, 1) 
                                 for res_col in res if res_col[1] == col])
        
    def table(self, table:str) -> str:
        return table
    
    def map_type(self, col:Column) -> str:
        type = {"integer": "integer", 
                "smallint": "integer", 
                "bigint": "integer", 
                "real": "real", 
                "double precision": "double precision", 
                "decimal": f"decimal({col.precision},{col.scale})", 
                "numeric": "numeric",  
                "smallserial": "integer", 
                "serial": "integer", 
                "bigserial": "integer", 
                "text": "text", 
                "timestamp": "datetime", 
                "timestamp with time zone": "datetime", 
                "timestamp without time zone": "datetime", 
                "date": "date", 
                "time with time zone": "time", 
                "time": "time", 
                "interval": "text", 
                "uuid": "text", 
                "json": "json", 
                "jsonb": "jsonb", 
                "boolean": "boolean", 
                "bytea": "blob", 
                "oid": "integer", 
                "geometry": "text", 
                "Point": "text", 
                "LineString": "text", 
                "Polygon": "text", 
                "MultiPoint": "text", 
                "MultiLineString": "text", 
                "MultiPolygon": "text", 
                "GeometryCollection": "text", 
                "Point Geography": "text", 
                "LineString Geography": "text", 
                "Polygon Geography": "text", 
                "MultiPoint Geography": "text", 
                "MultiLineString Geography": "text", 
                "MultiPolygon Geography": "text", 
                "Geography": "text", 
                "TEXT": "text", 
                "REAL": "real", 
                "FLOAT": "float", 
                "float": "float", 
                "DOUBLE": "double", 
                "double": "double", 
                "DOUBLE PRECISION": "double precision", 
                "INTEGER": "integer", 
                "NUMERIC": "numeric", 
                "BLOB": "blob", 
                "NUMERIC": "numeric", 
                "BOOLEAN": "boolean", 
                "DATE": "date", 
                "TIME": "time", 
                "DATETIME": "datetime", 
                "datetime": "datetime", 
                "JSON": "json", 
                "JSOB": "jsob"}
        
        return type[col.data_type]

    def create_table(self, cursor:sqlite3.Cursor, schema:Table) -> None:
        query, params = self.create_table_sql(schema).build(self.binding)
        cursor.execute(query, params)