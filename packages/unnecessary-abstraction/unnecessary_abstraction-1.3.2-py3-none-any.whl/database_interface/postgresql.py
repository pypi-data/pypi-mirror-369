from .database import Database
from .core import Table, Column, PGFunction
import psycopg
import atexit
from contextlib import contextmanager


class PostgreSQL(Database):
    def __init__(self, db_name:str, user:str, password:str, namespace:str, host:str="localhost", port:int=5432):
        self.__db_name:str = db_name
        self.__user:str = user
        self.__password:str = password
        self.__host:str = host
        self.__port:int = port
        self.__conn = psycopg.Connection.connect(self.connect_str)
        self.__binding = "%s"
        self.__namespace:str = namespace

        atexit.register(self.close)

    @property
    def db_name(self) -> str:
        return self.__db_name
    @property
    def user(self) -> str:
        return self.__user
    @property
    def password(self) -> str:
        return self.__password
    @property
    def host(self) -> str:
        return self.__host
    @property
    def port(self) -> int:
        return self.__port
    @property
    def connect_str(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
    @property
    def connection(self) -> psycopg.Connection:
        return self.__conn
    @property
    def binding(self) -> str:
        return self.__binding
    @property
    def table_list(self) -> tuple[str]:
        with self.cursor() as cur:
            cur.execute((f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.__namespace}'"))
            return tuple(table[0] for table in cur.fetchall())
        
    def schema(self, cursor:psycopg.Cursor, table:str, cols:list=["*"]) -> Table:
        GET_COL_SCHEMA = f"""
        SELECT column_name, data_type, ordinal_position, udt_name
        FROM information_schema.columns 
        WHERE table_schema='{self.__namespace}' AND table_name='{table}'
        """
        def get_geom(col_name:str): 
            sql = f"""
            SELECT postgis_typmod_type(atttypmod)
            FROM pg_attribute
            JOIN pg_class ON pg_class.oid = pg_attribute.attrelid
            JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
            WHERE pg_namespace.nspname='{self.__namespace}' 
            AND pg_class.relname='{table}' 
            AND pg_attribute.attname='{col_name}';
            """
            return cursor.execute(sql).fetchall()[0][0]
        
        res = cursor.execute(GET_COL_SCHEMA).fetchall()
        if not res:
            return None
        
        schema = []
        all_columns = (cols == ["*"])
        for col in res:
            col_filter = True if all_columns else col[0] in cols
            match (all_columns, col[3], col_filter):
                case (True, "geometry", _):
                    schema.append(Column(col[0], get_geom(col[0]), col[2]))
                case (True, _, _):
                    schema.append(Column(col[0], col[1], col[2]))
                case (False, "geometry", True):
                    schema.append(Column(col[0], get_geom(col[0]), col[2]))
                case (False, _, True):
                    schema.append(Column(col[0], col[1], col[2]))

        return Table(table, schema)

    def table(self, table:str) -> str:
        return f"{self.__namespace}.{table}"

    def map_type(self, col:Column) -> str:
        type = {"integer": "integer", 
                "smallint": "smallint", 
                "bigint": "bigint", 
                "real": "real", 
                "double precision": "double precision", 
                "decimal": f"decimal({col.precision},{col.scale})", 
                "numeric": f"numeric({col.precision},{col.scale})",  
                "smallserial": "smallserial", 
                "serial": "serial", 
                "bigserial": "bigserial", 
                "text": "text", 
                "timestamp": "timestamp", 
                "timestamp with time zone": "timestamp with time zone", 
                "timestamp without time zone": "timestamp without time zone", 
                "date": "date", 
                "time with time zone": "time with time zone", 
                "time": "time", 
                "interval": "interval", 
                "uuid": "uuid", 
                "json": "json", 
                "jsonb": "jsonb", 
                "boolean": "boolean", 
                "bytea": "bytea", 
                "oid": "oid", 
                "geometry": "geometry", 
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
                "FLOAT": "real", 
                "float": "real", 
                "DOUBLE": "double precision", 
                "double": "double precision", 
                "DOUBLE PRECISION": "double precision", 
                "INTEGER": "integer", 
                "NUMERIC": f"numeric({col.precision},{col.scale})", 
                "BLOB": "bytea", 
                "NUMERIC": f"numeric({col.precision},{col.scale})", 
                "BOOLEAN": "boolean", 
                "DATE": "date", 
                "TIME": "time", 
                "DATETIME": "timestamp", 
                "datetime": "timestamp", 
                "JSON": "json", 
                "JSOB": "jsob"}
        
        return type[col.data_type]

    def create_function(self, cursor:psycopg.Cursor, function:PGFunction):
        exists = True if cursor.execute(f"SELECT to_regproc('{function.name}')").fetchall()[0][0] else False
        if not exists and function.query:
            cursor.execute(function.build(self.__namespace))

    def create_table(self, cursor:psycopg.Cursor, schema:Table) -> None:
        query, params = self.create_table_sql(schema).build(self.binding)
        cursor.execute(query, params)
        for trigger in schema.triggers:
            cursor.execute(trigger.build(schema.name, self.__namespace))

    @contextmanager
    def listen(self, channels:list[str], timeout_after:int=30):
        listen_conn = psycopg.Connection.connect(self.connect_str, autocommit=True)
        for channel in channels:
            listen_conn.execute(f"LISTEN {channel}")
        try:
            yield listen_conn.notifies(timeout_after)
        except Exception as e:
            raise e
        finally:
            listen_conn.close()


def create_replication(publication_name:str, tables:list[str], pub_db:PostgreSQL, sub_db:PostgreSQL) -> None:
    pub_db.connection.set_autocommit(True)
    with pub_db.cursor() as cur:
        cur.execute(f"""CREATE PUBLICATION {publication_name} 
                    FOR TABLE {', '.join(tables)} 
                    WITH (publish = 'insert, update, delete, truncate');""")
    
    sub_db.connection.set_autocommit(True)
    with sub_db.cursor() as cur:
        cur.execute(f"""CREATE SUBSCRIPTION {publication_name}_sub 
                    CONNECTION 'host={pub_db.host} dbname={pub_db.db_name} user={pub_db.user} password={pub_db.password}'
                    PUBLICATION {publication_name};""")
        
    pub_db.connection.set_autocommit(False)
    sub_db.connection.set_autocommit(False)