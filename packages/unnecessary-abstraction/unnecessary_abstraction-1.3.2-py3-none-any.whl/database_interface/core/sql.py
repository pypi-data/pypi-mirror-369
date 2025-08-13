from typing import Literal, Callable
from datetime import datetime

class Composable:
    __slots__ = ("query", "params")
    def __init__(self):
        self.query:list = []
        self.params:list = []

    def and_(self, column):
        self.query.append(f" AND {column}")
        return self
    
    def or_(self, column):
        self.query.append(f" OR {column}")
        return self
    
    def not_(self, column):
        self.query.append(f" NOT {column}")
        return self
    
    def is_null(self):
        self.query.append(f" IS NULL")
        return self

    def not_null(self):
        self.query.append(f" IS NOT NULL")
        return self
    
    def between(self, value1, value2):
        self.query.append(f" BETWEEN ? AND ?")
        self.params.append(value1)
        self.params.append(value2)
        return self
    
    def is_(self, operator:Literal[">", "<", ">=", "<=", "=", "!="], value):
        if type(value) == datetime:
            value = value.isoformat()
            
        match operator:
            case "<":
                self.query.append(" < ?")
            case ">":
                self.query.append(" > ?")
            case "<=":
                self.query.append(" <= ?")
            case ">=":
                self.query.append(" >= ?")
            case "=":
                self.query.append(" = ?")
            case "!=":
                self.query.append(" != ?")
        self.params.append(value)
        return self

    def in_(self, values:list | tuple):
        placeholders = ', '.join('?' for _ in values)
        self.query.append(f" IN ({placeholders})")
        self.params.extend(values)
        return self

    def not_in(self, values:list | tuple):
        placeholders = ', '.join('?' for _ in values)
        self.query.append(f" NOT IN ({placeholders})")
        self.params += values
        return self

    def like(self, value:str):
        self.query.append(f" LIKE ?")
        self.params.append(value)
        return self

    def not_like(self, value:str):
        self.query.append(f" NOT LIKE ?")
        self.params.append(value)
        return self

class Where(Composable):
    def __init__(self, column:str):
        super().__init__()
        self.query.append(f"WHERE {column}")

class OrderBy(Composable):
    def __init__(self, col:str, op:Literal["ASC", "DESC"]):
        super().__init__()
        match op:
            case "ASC":
                self.query.append(f"ORDER BY {col}")
            case "DESC":
                self.query.append(f"ORDER BY {col} DESC")

JOIN_TYPE = Literal["INNER", "RIGHT", "LEFT", "OUTER"]
class Join(Composable):
    def __init__(self, right_table:str, type:JOIN_TYPE):
        super().__init__()
        self.query.append(f"{type} JOIN {right_table} ")
        self.right_table = right_table

    def on_columns(self, left_on, right_on):
        self.query.append(f"ON {left_on} = {right_on}")
        return self

class SpatialJoin(Composable):
    def __init__(self, right_table:str, type:JOIN_TYPE):
        super().__init__()
        self.query.append(f"{type} JOIN {right_table} ")
        self.right_table = right_table

    def ST_Contains(self, left_on, right_on):
        self.query.append(f"ON ST_Contains({right_on}, {left_on})")
        return self
    
    def ST_DWithin(self, left_on, right_on, distance):
        self.query.append(f"ON ST_DWithin({right_on}, {left_on}, {distance})")
        return self
    
    def ST_Intersects(self, left_on, right_on):
        self.query.append(f"ON ST_Intersects({right_on}, {left_on})")
        return self
    
class SQL(Composable):
    def __init__(self, sql:str="", params:list=[]):
        super().__init__()
        self.query.append(sql)
        self.params += params

    @classmethod
    def from_file(cls, path:str):
        with open(path, "r") as f:
            sql = f.read()
        return cls(sql)

    def optional_add(self, sql:Where|Join|SpatialJoin):
        if sql:
            self.query.append(" ")
            self.query += sql.query
            self.params += sql.params
        return self
    
    def append(self, sql:str, params:list=[]):
        self.query.append(sql)
        self.params += params
    
    def values(self, to_values:list[list | tuple]):
        if not to_values:
            raise Exception("TEMP EXCEPTION")
        
        self.query.append(f" VALUES (")
        for _ in range(len(to_values[0])):
            self.query.append("?, ")

        self.query[-1] = self.query[-1][:-2] + ")"
        self.params += to_values

        return self
    
    def set_to_values(self, cols:list[str], values:list | tuple, on_column:str=""):
        self.query += [" SET ", " = ?, ".join(cols), " = ?"]
        if on_column:
            pos = cols.index(on_column)
            self.query.append(f" WHERE {on_column} = ?")
            values = [row + (row[pos],) for row in values]
        self.params += values
        return self
    
    def update_on_conflict(self, cols:list[str], conflict_col:str):
        if conflict_col:
            self.query.append(f" ON CONFLICT ({conflict_col}) DO UPDATE SET ")
            self.query += [f"{col} = EXCLUDED.{col}, " for col in cols if col != conflict_col]
            self.query[-1] = self.query[-1][:-2]
        return self
    
    def where(self, column):
        self.query.append(f" WHERE {column}")
        return self
    
    def limit(self, amount:int=0):
        if amount:
            self.query.append(f" LIMIT {amount}")
        return self

    def build(self, token:Literal["?", "%s"]):
        return ''.join(self.query).replace("?", token), tuple(self.params)


TRIGGER_OP = Literal["INSERT", "UPDATE", "DELETE", "TRUNCATE", 
                     "INSERT OR UPDATE", 
                     "INSERT OR DELETE", 
                     "INSERT OR TRUNCATE", 
                     "UPDATE OR DELETE", 
                     "UPDATE OR TRUNCATE", 
                     "DELETE OR TRUNCATE", 
                     "INSERT OR UPDATE OR DELETE", 
                     "UPDATE OR DELETE OR TRUNCATE", 
                     "INSERT OR UPDATE OR TRUNCATE", 
                     "INSERT OR DELETE OR TRUNCATE", 
                     "INSERT OR UPDATE OR DELETE OR TRUNCATE"]

class PGFunction:
    def __init__(self, function_name:str):
        self.name = function_name
        self.query:list = []

    def build(self, pg_namespace:str):
        return ''.join(self.query).replace(":NAMESPACE:", f"{pg_namespace}.")
    
    def trigger(self, language:Literal["sql", "plpgsql", "python"], sql:SQL):
        self.query.append(f"CREATE OR REPLACE FUNCTION :NAMESPACE:{self.name}()\nRETURNS TRIGGER\nLANGUAGE {language}\n")
        self.query.append("AS $$")
        self.query += sql.query
        self.query.append("$$;")
        return self

class Trigger:
    def __init__(self, name:str):
        self.name:str = name
        self.query:list = []
        self.query.append(f"CREATE TRIGGER {name}\n")

    def build(self, table:str, pg_namespace:str):
        return ''.join(self.query).replace(":TABLE:", table).replace(":NAMESPACE:", f"{pg_namespace}.")

    def after(self, op:TRIGGER_OP, update_of:list[str]=["*"]):
        if not update_of == ["*"]:
            self.query.append(f"AFTER {op} OF {', '.join(update_of)} ON :NAMESPACE::TABLE:\n")
        else:
            self.query.append(f"AFTER {op} ON :NAMESPACE::TABLE:\n")
        return self
    
    def before(self, op:TRIGGER_OP, update_of:list[str]=["*"]):
        if not update_of == ["*"]:
            self.query.append(f"BEFORE {op} OF {', '.join(update_of)} ON :NAMESPACE::TABLE:\n")
        else:
            self.query.append(f"BEFORE {op} ON :NAMESPACE::TABLE:\n")
        return self

    def instead_of(self, op:TRIGGER_OP, update_of:list[str]=["*"]):
        if not update_of == ["*"]:
            self.query.append(f"INSTEAD OF {op} OF {', '.join(update_of)} ON :NAMESPACE::TABLE:\n")
        else:
            self.query.append(f"INSTEAD OF {op} ON :NAMESPACE::TABLE:\n")
        return self

    def for_each(self, op:Literal["ROW", "STATEMENT"]):
        self.query.append(f"FOR EACH {op}")
        return self
    
    def when(self, sql:SQL):
        self.query.append("WHEN (")
        self.query += sql.query
        self.query.append(")")
        return self

    def execute(self, function:PGFunction):
        self.query.append(f" EXECUTE FUNCTION :NAMESPACE:{function.name}();")
        return self