import sqlite3
from abc import ABC, abstractmethod

def get_db_connection(data_path):
    conn = sqlite3.connect(data_path)
    conn.row_factory = sqlite3.Row
    return conn

class Transportation(ABC):
    def __init__(self, departure_time: str, start: str, end: str, folder: str):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        self.data_path = r"../data/" + folder
        self.paths = [[]]

    @abstractmethod
    def create_path(self):
        pass

    @abstractmethod
    def create_time(self):
        pass

    @abstractmethod
    def create_cost(self):
        pass

    def create(self):
        self.create_path()
        self.create_time()
        self.create_cost()
        return self.paths