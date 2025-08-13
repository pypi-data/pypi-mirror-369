from typing import Literal, Any
from .sql import SQL

SQLITE = Literal["text", "real", "integer", "blob", "numeric", "boolean", "date", "datetime", "json"]

POSTGRES = Literal["integer", "smallint", "bigint", "real", "double precision", "decimal", "numeric", 
                   "smallserial", "serial", "bigserial", "text", "timestamp", "timestamp with time zone", 
                   "timestamp without time zone", "date", "time with time zone", "time", "interval", 
                   "uuid", "json", "jsonb", "boolean", "bytea", "oid", "geometry"]

POSTGIS = Literal["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon", 
                  "GeometryCollection", "Point Geography", "LineString Geography", "Polygon Geography",
                  "MultiPoint Geography", "MultiLineString Geography", "MultiPolygon Geography", "Geography"]

class Column:
    __slots__ = ("name", "data_type", "position", 
                 "__primary_key", "__nullable", "__unique", 
                 "__default", "__foreign_keys", "__check", 
                 "__precision", "__scale", "__spatial_ref", "__M", "__Z", 
                 "__idx", "__unique_idx", "__partial_idx", "__spatial_idx")
    
    def __init__(self, name:str, data_type:SQLITE|POSTGRES|POSTGIS, position:int=1):
        
        self.name:str = name
        self.data_type:SQLITE|POSTGRES|POSTGIS = data_type
        if '(' in self.data_type:
            split = self.data_type.split("(")[1]
            split = split[:-1].split(",")
            self.set_precision(int(split[0]))
            self.set_scale(int(split[1]))
            self.data_type = self.data_type[:7]
        self.position:int = position

        self.__primary_key:bool = False
        self.__nullable:bool = True
        self.__unique:bool = False
        self.__foreign_keys:list[tuple] = []
        self.__check:SQL = None
        self.__default:Any = None
        self.__precision:int = 10
        self.__scale:int = 5
        self.__spatial_ref:int = 4326
        self.__M:str = ""
        self.__Z:str = ""

        self.__idx:str = None
        self.__unique_idx:str = None
        self.__partial_idx:tuple[str, str] = None
        self.__spatial_idx:str = None
        

    @property
    def primary_key(self) -> bool:
        return self.__primary_key
    def is_primary_key(self):
        self.__primary_key = True
        return self
    
    @property
    def nullable(self) -> bool:
        return self.__nullable
    def no_nulls(self):
        self.__nullable = False
        return self
    
    @property
    def unique(self) -> bool:
        return self.__unique
    def unique_values(self):
        self.__unique = True
        return self

    @property
    def foreign_keys(self) -> list[tuple]:
        return self.__foreign_keys
    def foreign_key(self, ref_table:str, ref_col:str):
        self.__foreign_keys.append((ref_table, ref_col)) # Check if pg namespaces will mess this up
        return self
    
    @property
    def check(self):
        return self.__check
    def check_constraint(self, check:SQL):
        self.__check = check
        return self
    
    @property
    def default(self) -> Any:
        return self.__default
    def default_value(self, default:Any):
        match default:
            case str():
                self.__default = f"'{default}'"
            case _:
                self.__default = default
        return self
    
    @property
    def spatial_ref(self) -> int:
        return self.__spatial_ref
    def set_spatial_ref(self, wkid:int):
        self.__spatial_ref = wkid
        return self
    
    @property
    def precision(self) -> int:
        return self.__precision
    def set_precision(self, ndigits:int):
        self.__precision = ndigits
        return self
    
    @property
    def scale(self) -> int:
        return self.__scale
    def set_scale(self, ndigits:int):
        self.__scale = ndigits
        return self

    @property
    def m(self) -> str:
        return self.__M
    def has_m(self):
        self.__M = "M"
        return self
    
    @property
    def z(self) -> str:
        return self.__Z
    def has_z(self):
        self.__Z = "Z"
        return self
    
    @property
    def idx(self) -> bool:
        return self.__idx
    def index(self, idx_name:str):
        self.__idx = idx_name
        return self

    @property
    def unique_idx(self) -> bool:
        return self.__unique_idx
    def unique_index(self, idx_name:str):
        self.__unique_idx = idx_name
        return self
    
    @property
    def partial_idx(self) -> str:
        return self.__partial_idx
    def partial_index(self, idx_name:str, where):
        self.__partial_idx = (idx_name, where)
        return self
    
    @property
    def spatial_idx(self) -> bool:
        return self.__spatial_idx
    def spatial_index(self, idx_name:str):
        self.__spatial_idx = idx_name
        return self
    
    @property
    def to_dict(self) -> dict:
        return {"name": self.name, "data_type": self.data_type, "position": self.position}
    
    def __repr__(self) -> str:
        return f"{self.name:<25} {self.data_type:<30} {self.position:<3}"