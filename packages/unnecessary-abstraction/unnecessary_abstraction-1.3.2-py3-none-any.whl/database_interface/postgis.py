import atexit
from typing import Literal
from .postgresql import PostgreSQL
from .core import SpatialJoin, Join, OrderBy, Table, Where
import psycopg

GEOM_TYPES = ["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon", 
              "GeometryCollection", "Point Geography", "LineString Geography", "Polygon Geography",
              "MultiPoint Geography", "MultiLineString Geography", "MultiPolygon Geography", "Geography"]

class PostGIS(PostgreSQL):
    def __init__(self, db_name:str, user:str, password:str, namespace:str, host:str="localhost", port:int=5432, geometry_extract:Literal["WKT", "WKB"]="WKT"):
        super().__init__(db_name, user, password, namespace, host, port)
        self.__extract_mode = geometry_extract

        atexit.register(self.close)

    def map_type(self, col):
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
                "Point": f"geometry(Point{col.z}{col.m}, {col.spatial_ref})", 
                "LineString": f"geometry(LineString{col.z}{col.m}, {col.spatial_ref})", 
                "Polygon": f"geometry(Polygon{col.z}{col.m}, {col.spatial_ref})", 
                "MultiPoint": f"geometry(MultiPoint{col.z}{col.m}, {col.spatial_ref})", 
                "MultiLineString": f"geometry(MultiLineString{col.z}{col.m}, {col.spatial_ref})", 
                "MultiPolygon": f"geometry(MultiPolygon{col.z}{col.m}, {col.spatial_ref})", 
                "GeometryCollection": f"geometry(GeometryCollection{col.z}{col.m}, {col.spatial_ref})", 
                "Point Geography": f"geography(Point)", 
                "LineString Geography": f"geography(LineString)", 
                "Polygon Geography": f"geography(Polygon)", 
                "MultiPoint Geography": f"geography(MultiPoint)", 
                "MultiLineString Geography": f"geography(MultiLineString)", 
                "MultiPolygon Geography": f"geography(MultiPolygon)", 
                "Geography": "geography", 
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
    
    def select(self, cursor:psycopg.Cursor, table:str, cols:list=["*"], where:Where=None, 
               join:Join | SpatialJoin=None, order_by:OrderBy=None, limit:int=0, schema:Table=None) -> list[tuple]:
        schema = self.schema(cursor, table, cols)
        if self.__extract_mode == "WKT":
            cols = list(schema.col_name_list)
            for i, d_type in enumerate(schema.data_type_list):
                if d_type in GEOM_TYPES:
                    cols[i] = f"ST_AsText({cols[i]})"

        return super().select(cursor, table, cols, where, join, order_by, limit, schema)