import pickle, lzma, base64
from .core import Table, Where

class CrossDomainGimmick:
    def __init__(self, payload:dict={}):
        self.payload = payload

    @classmethod
    def from_gibberish(cls, byte_str:str):
        decoded = base64.b64decode(byte_str.encode('ascii'))
        decompressed = lzma.decompress(decoded)
        unpickled = pickle.loads(decompressed)
        return cls(unpickled)
    
    def build(self) -> str:
        pickled = pickle.dumps(self.payload, protocol=pickle.HIGHEST_PROTOCOL)
        compress = lzma.compress(pickled, preset=9 | lzma.PRESET_EXTREME)
        return base64.b64encode(compress).decode('ascii')
    
    def insert(self, table:str, rows:list[tuple], cols:list=["*"], on_conflict_col:str="", where:Where=None, schema:Table=None) -> None:
        if "insert" not in self.payload.keys():
            self.payload["insert"] = []
        self.payload["insert"].append({"table": table, 
                                         "rows": rows, 
                                         "cols": cols, 
                                         "on_conflict_col": on_conflict_col, 
                                         "where": where, 
                                         "schema": schema})
        return self
        
    def update(self, table:str, rows:list[tuple], cols:list=["*"], on_column:str="", where:Where=None, schema:Table=None) -> None:
        if "update" not in self.payload.keys():
            self.payload["update"] = []
        self.payload["update"].append({"table": table, 
                                         "rows": rows, 
                                         "cols": cols, 
                                         "on_column": on_column, 
                                         "where": where, 
                                         "schema": schema})
        return self
        
    def delete(self, table:str, where:Where) -> None:
        if "delete" not in self.payload.keys():
            self.payload["delete"] = []
        self.payload["delete"].append({"table": table, 
                                         "where": where})
        return self

    def insert_records(self, table:str, records:list[dict], on_conflict_col:str="", where:Where=None, schema:Table=None) -> None:
        if "insert_records" not in self.payload.keys():
            self.payload["insert_records"] = []
        self.payload["insert_records"].append({"table": table, 
                                                 "records": records, 
                                                 "on_conflict_col": on_conflict_col, 
                                                 "where": where, 
                                                 "schema": schema})
        return self

    def update_with_records(self, table:str, records:list[dict], on_column:str="", where:Where=None, schema:Table=None) -> None:
        if "update_with_records" not in self.payload.keys():
            self.payload["update_with_records"] = []
        self.payload["update_with_records"].append({"table": table, 
                                                      "records": records, 
                                                      "on_column": on_column, 
                                                      "where": where, 
                                                      "schema": schema})
        return self
    
    def create_table(self, schema:Table) -> None:
        if "create_table" not in self.payload.keys():
            self.payload["create_table"] = []
        self.payload["create_table"].append({"schema": schema})
        return self
        
    def create_table_with_records(self, table:str, records:list[dict]) -> None:
        if "create_table_with_records" not in self.payload.keys():
            self.payload["create_table_with_records"] = []
        self.payload["create_table_with_records"].append({"table": table, 
                                                            "records": records})
        return self