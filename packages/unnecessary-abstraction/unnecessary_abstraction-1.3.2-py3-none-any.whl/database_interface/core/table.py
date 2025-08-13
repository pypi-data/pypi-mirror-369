from .column import Column
from .sql import Trigger
import csv
import json

class Table:
    __slots__ = ("__name", "__columns", "__triggers", "__composite_idx")
    def __init__(self, name:str, columns:list|tuple[Column]):
        self.__name:str = name
        self.__columns:list|tuple[Column] = columns
        self.__triggers:list[Trigger] = []

        self.__composite_idx:tuple[str, list[str]] = None
        
        self.order_columns()

    @property
    def name(self) -> str:
        return self.__name
    @property
    def columns(self) -> tuple[Column]:
        return self.__columns
    @property
    def column_dict(self) -> dict[str, Column]:
        return {col.name: col for col in self.__columns}
    @property
    def col_name_set(self) -> set[str]:
        return set(col.name for col in self.__columns)
    @property
    def col_name_list(self) -> tuple[str]:
        return tuple(col.name for col in self.__columns)
    @property
    def data_type_list(self) -> tuple[str]:
        return tuple(col.data_type for col in self.__columns)
    @property
    def positions_list(self) -> tuple[int]:
        return tuple(col.position for col in self.__columns)
    
    @property
    def triggers(self) -> list[Trigger]:
        return self.__triggers
    def trigger(self, trigger:Trigger):
        self.__triggers.append(trigger)
        return self

    @property
    def composite_idx(self) -> str:
        return self.__composite_idx
    def composite_index(self, idx_name:str, on_cols:list[str]):
        on_cols = ", ".join(on_cols)
        self.__composite_idx = (idx_name, on_cols)
        return self
    

    def order_columns(self) -> None:
        pos_list = sorted(self.positions_list)
        if pos_list == tuple(range(min(pos_list), max(pos_list)+1)) and pos_list[0] == 1:
            self.order_by_position_id()
        else:
            self.order_by_location()

    def order_by_location(self) -> None:
        for pos, column in enumerate(self.__columns):
            column.position = pos + 1

    def order_by_position_id(self) -> None:
        self.__columns = tuple(sorted(self.__columns, key=lambda x: x.position))

    def filter_columns(self, col_name_list:list) -> None:
        self.__columns = tuple(col for col in self.__columns if col in col_name_list)
        self.order_by_location()

    def to_csv(self, save_path:str=".") -> None:
        cols = [col.to_dict for col in self.__columns]
        headers = cols[0].keys()
        with open(f"{save_path}\\{self.__name}_schema.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
            writer.writerows(cols)
    
    def to_json(self, save_path:str=".") -> None:
        cols = [col.to_dict for col in self.__columns]
        with open(f"{save_path}\\{self.__name}_schema.json", "w") as f:
            json.dump(cols, f, indent=4)
    
    def __repr__(self) -> str:
        text = f"{'Column Name':<25} {'Data Type':<30} {'Position':<3}\n"
        text += f"-" * 68 + "\n"
        for col in self.columns:
            text += f"{col}\n"
        return text

    def generate_definitions(self, file_name:str, class_name:str):
        slotted_class = []
        named_tuple = []
        typed_dict = []

        slotted_class.append("from datetime import datetime, time, date, timedelta\n\n")
        slotted_class.append(f"class {class_name}:\n")
        slotted_class.append('    __slots__ = ("' + '", "'.join(self.col_name_list) + '")\n')
        for row in self.columns:
            slotted_class.append(f"    {row.name}:{self.map_type(row)}\n")
        
        slotted_class.append("\ndef __init__(self) -> None:\n")
        slotted_class.append("    pass\n")

        named_tuple.append("from datetime import datetime, time, date, timedelta\n")
        named_tuple.append("from typing import NamedTuple\n\n")
        named_tuple.append(f"class {class_name}Tuple(NamedTuple):\n")
        for row in self.columns:
            named_tuple.append(f"    {row.name}:{self.map_type(row)}\n")

        typed_dict.append("from datetime import datetime, time, date, timedelta\n")
        typed_dict.append("from typing import TypedDict\n\n")
        typed_dict.append(f"class {class_name}Dictionary(TypedDict):\n")
        for row in self.columns:
            typed_dict.append(f"    {row.name}:{self.map_type(row)}\n")

        with open(f"{file_name}.py", "w") as f:
            f.write("".join(slotted_class))
        with open(f"{file_name}_tuple.py", "w") as f:
            f.write("".join(named_tuple))
        with open(f"{file_name}_dictionary.py", "w") as f:
            f.write("".join(typed_dict))
            

    def map_type(self, col:Column) -> str:
        type = {"integer": "int", 
                "smallint": "int", 
                "bigint": "int", 
                "real": "float", 
                "double precision": "float", 
                "decimal": "float", 
                "numeric": "float",  
                "smallserial": "int", 
                "serial": "int", 
                "bigserial": "int", 
                "text": "str", 
                "timestamp": "datetime", 
                "timestamp with time zone": "datetime", 
                "timestamp without time zone": "datetime", 
                "date": "date", 
                "time with time zone": "datetime", 
                "time": "time", 
                "interval": "str", 
                "uuid": "str", 
                "json": "dict", 
                "jsonb": "dict", 
                "boolean": "bool", 
                "bytea": "bytes", 
                "oid": "int", 
                "geometry": "str", 
                "Point": "str", 
                "LineString": "str", 
                "Polygon": "str", 
                "MultiPoint": "str", 
                "MultiLineString": "str", 
                "MultiPolygon": "str", 
                "GeometryCollection": "str", 
                "Point Geography": "str", 
                "LineString Geography": "str", 
                "Polygon Geography": "str", 
                "MultiPoint Geography": "str", 
                "MultiLineString Geography": "str", 
                "MultiPolygon Geography": "str", 
                "Geography": "str", 
                "TEXT": "str", 
                "REAL": "float", 
                "FLOAT": "float", 
                "float": "float", 
                "DOUBLE": "float", 
                "double": "float", 
                "DOUBLE PRECISION": "float", 
                "INTEGER": "int", 
                "NUMERIC": "float", 
                "BLOB": "bytes", 
                "NUMERIC": "float", 
                "BOOLEAN": "bool", 
                "DATE": "date", 
                "TIME": "time", 
                "DATETIME": "datetime", 
                "datetime": "datetime", 
                "JSON": "dict", 
                "JSOB": "dict"}
        
        return type[col.data_type]