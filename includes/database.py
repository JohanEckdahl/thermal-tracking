import sqlite3
import pandas as pd

class Database():
    
    def __init__(self, db_name): self.connection = self.connect(db_name)
    
    def read(self, sql): pass
    
    def connect(self,db_name): pass
    
    def insert(self, table_name, dataframe): print("yaa, inserted, get some!")
        
    def disconnect(self): pass
        
    def __del__(self): self.disconnect()
        

class SQLiteDB(Database):
    
    def connect(self,db_name): return sqlite3.connect(db_name)
    
    def read(self, sql): return pd.read_sql_query(sql, self.connection, index_col="id")
    
    def insert(self, table_name, dataframe):
        print(dataframe)
        dataframe.to_sql(table_name, self.connection, if_exists="append", index = False)
        
    def disconnect(self): self.connection.close()

