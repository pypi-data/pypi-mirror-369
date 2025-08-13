from .column import Column
from .table import Table
from datetime import datetime, timedelta, time, date
import json
import csv
import pickle
import warnings
from decimal import Decimal
from uuid import UUID
from typing import Literal, Any
from collections import defaultdict
import re
import pathlib 

REGEX = r"^\s*(POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|GEOMETRY)(?:\s+(ZM|Z|M))?\s\(.*\)$"
PATTERN = re.compile(REGEX, re.IGNORECASE)

OP_MODE = Literal["in", "out"]
  
def rows_to_columnar(records:list | tuple[dict], return_tuples:bool=False) -> dict[list | tuple]:
    if return_tuples:
        return {col: tuple(row[col] for row in records) for col in records[0]}
    else:
        return {col: [row[col] for row in records] for col in records[0]}

def columnar_to_rows(records:dict[list | tuple], return_tuples:bool=False) -> list | tuple[dict]:
    if return_tuples:
        return tuple(dict(zip(records.keys(), row)) for row in zip(*records.values()))
    else:
        return [dict(zip(records.keys(), row)) for row in zip(*records.values())]

def is_ogc_geometry(val:str) -> tuple[bool, str]:
    str_match = re.match(PATTERN, val)

    if str_match:
        match str_match.group(1):
            case "POINT":
                return True, "point"
            case "LINESTRING":
                return True, "linestring"
            case "POLYGON":
                return True, "polygon"
            case "MULTIPOINT":
                return True, "multipoint"
            case "MULTILINESTRING":
                return True, "multilinestring"
            case "MULTIPOLYGON":
                return True, "multipolygon"
            
        match str_match.group(2):
            case "Z":
                pass
            case "M":
                pass
            case "ZM":
                pass
    else:
        return False, "text"

def is_datetime(val:str) -> bool:
    try:
        datetime.fromisoformat(val)
        return True
    except ValueError:
        return False
    
def is_string_jsonable(val:str) -> bool:
    try:
        json.loads(val)
        return True
    except (TypeError, OverflowError, json.decoder.JSONDecodeError):
        return False
def is_pyobj_jsonable(val) -> bool:
    try:
        json.dumps(val)
        return True
    except (TypeError, OverflowError, json.decoder.JSONDecodeError):
        return False

def precision(num:float) -> int:
    return len(str(num).split(".")[1])

def convert_numeric(numeric:float | Decimal, op:OP_MODE) -> float:
    match (numeric, op):
        case (Decimal(), "in" | "out"):
            return numeric.__float__()
        case (_, _):
            return numeric

def convert_date(date_time:str | datetime, op:OP_MODE) -> str | datetime:
    match (date_time, op):
        case (datetime(), "in"):
            return date_time.isoformat()
        case (str(), "out"):
            return datetime.fromisoformat(date_time)
        case (_, _):
            return date_time

def convert_json(json_val:dict | list | tuple | str, op:OP_MODE) -> str | dict | list | tuple:
    match (json_val, op):
        case (dict() | list() | tuple(), "in"):
            return json.dumps(json_val)
        case (str(), "out"):
            return json.loads(json_val)
        case (_, _):
            return json_val
        
def convert_bool(bool_val:bool | int, op:OP_MODE) -> bool:
    match (bool_val, bool_val, op):
        case (int(), 1, "out"):
            return True
        case (int(), 0, "out"):
            return False
        case (_, _, _):
            return bool_val

def convert_uuid(uuid_val:UUID | str, op:OP_MODE) -> str:
    match (uuid_val, op):
        case (UUID(), _):
            return uuid_val.__str__()
        case (_, _):
            return uuid_val

def convert_types(schema:Table, rows:list[tuple], op:OP_MODE) -> list[tuple]:
    func_map = {"datetime": convert_date, 
                "json": convert_json, 
                "jsonb": convert_json, 
                "numeric": convert_numeric, 
                "boolean": convert_bool, 
                "uuid": convert_uuid}
    
    mod_map = {pos: d_type for pos, d_type in enumerate(schema.data_type_list) if d_type in func_map.keys()}
    if not mod_map:
        return rows
    else:
        return [tuple(func_map[mod_map[pos]](val, op) if pos in mod_map else val 
                      for pos, val in enumerate(row)) 
                      for row in rows]



class Utils:

    @staticmethod
    def evaluate_schema(table_name:str, records:list[dict] | dict[list]) -> Table:
        if isinstance(records, (list, tuple)):
            records:dict[list] = rows_to_columnar(records, True)
        
        schema = []
        for pos, (col_name, col_data) in enumerate(records.items(), 1):
            col_type = tuple(Utils.infer_type(x)for x in col_data if x != None)
            types = set(col_type)
            if not types:
                col_type = ["text"]
            elif len(types) == 2 and "integer" in types and "decimal" in types:
                col_type = ["decimal"]
            elif len(types) > 1:
                warnings.warn(f"schema evaluation picked up types {types} in col {col_name}. Forcing to text due to the ambiguity.")
                col_type = ["text"]
            
            schema.append(Column(col_name, col_type[0], pos))
            
        return Table(table_name, schema)

    @staticmethod
    def rename_duplicate_columns(fieldname_list:list[str]) -> list[str]:
        d = defaultdict(list)
        [d[name].append(seq) for seq, name in enumerate(fieldname_list)]
        for col, count in d.items():
            if len(count) > 1:
                for seq, index in enumerate(count[1:]):
                    fieldname_list[index] = f"{fieldname_list[index]}_{seq+2}"
        return fieldname_list
    
    @staticmethod
    def csv_to_records(csv_path:str) -> list[dict]:
        csv_path:pathlib.Path = pathlib.Path(csv_path)
        with open(csv_path, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                reader.fieldnames = Utils.rename_duplicate_columns(reader.fieldnames)
            records = [row for row in reader]
        
        for row in records:
            for key, val in row.items():
                if val == '':
                    row[key] = None
        return records
    
    @staticmethod
    def records_to_csv(csv_name:str, table_records:list[dict], csv_path:str=".") -> None:
        headers = table_records[0].keys()
        with open(f"{csv_path}\\{csv_name}.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
            writer.writerows(table_records)

    @staticmethod
    def json_to_records(json_path:str) -> list[dict]:
        json_path:pathlib.Path = pathlib.Path(json_path)
        with open(json_path, "r") as f:
            data = json.load(f)
        
        if type(data) == list or type(data) == tuple:
            invalid = tuple(False for row in data if type(row) != dict)
            if invalid:
                raise Exception("TEMP")
        elif type(data) == dict:
            invalid = tuple(False for col in data.values() if not type(col) == list or type(col) == tuple)
            if invalid:
                raise Exception("TEMP")
            data = columnar_to_rows(data)
            
        return data

    @staticmethod
    def records_to_json(json_name:str, table_records:list[dict], json_path:str=".") -> None:
        for row in table_records:
            for key, val in row.items():
                match val:
                    case datetime():
                        row[key] = val.isoformat()
                    case set():
                        row[key] = list(val)
                    case _:
                        pass

        with open(f"{json_path}\\{json_name}.json", "w") as f:
            json.dump(table_records, f, indent=2)

    @staticmethod
    def row_tuples_to_json(json_name:str, table_rows:list[tuple], json_path:str=".") -> None:
        rebuilt_rows = []
        for row in table_rows:
            new_row = []
            for val in row:
                match val:
                    case datetime():
                        new_row.append(val.isoformat())
                    case set():
                        new_row.append(list(val))
                    case _:
                        new_row.append(val)
            rebuilt_rows.append(new_row)
            
        with open(f"{json_path}\\{json_name}.json", "w") as f:
            json.dump(rebuilt_rows, f, indent=2)

    @staticmethod
    def pickle(file_name:str, py_obj:Any, save_path:str=".") -> None:
        with open(f"{save_path}\\{file_name}", "wb") as f:
            pickle.dump(py_obj, f)
    
    @staticmethod
    def unpickle(file_path:str) -> Any:
        file_path:pathlib.Path = pathlib.Path(file_path)
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        return data

    @staticmethod
    def csv_to_json(csv_path:str, json_save_path:str=".") -> None:
        table_name = pathlib.Path(csv_path).stem
        records = Utils.csv_to_records(csv_path)
        Utils.records_to_json(table_name, records, json_save_path)

    @staticmethod
    def json_to_csv(json_path:str, csv_save_path:str=".") -> None:
        table_name = pathlib.Path(json_path).stem
        records = Utils.json_to_records(json_path)
        Utils.records_to_csv(table_name, records, csv_save_path)

    @staticmethod
    def infer_string_type(val:str):
        split = val.split(".")
        if len(split) == 2 and split[0].isdigit() and split[1].isdigit():
            return "decimal"
        elif val.isdigit():
            return "integer"
        elif "-" == val[0] and len(val) > 1:
            if len(split) == 2 and split[0].isdigit() and split[1].isdigit():
                return "decimal"
            elif val[1:].isdigit():
                return "integer"
            else:
                return "text"
        elif is_datetime(val):
            if datetime.fromisoformat(val).tzinfo:
                return "timestamp with time zone"
            else:
                return "timestamp"
        elif (res := is_ogc_geometry(val))[0]:
            return res[1]
        elif is_string_jsonable(val):
            return "json"
        else:
            return "text"

    @staticmethod
    def infer_type(val):
        match val:
            case bool():
                return "boolean"
            case int():
                return "integer"
            case float():
                return "decimal"
            case bytes() | bytearray():
                return "bytea"
            case UUID():
                return "uuid"
            case datetime():
                if val.tzinfo:
                    return "timestamp with time zone"
                else:
                    return "timestamp"
            case time():
                return "time"
            case date():
                return "date"
            case timedelta():
                pass
            case dict() | list() | tuple():
                if is_pyobj_jsonable(val):
                    return "json"
                else:
                    raise Exception("Temp exception")
            case str():
                return Utils.infer_string_type(val)
