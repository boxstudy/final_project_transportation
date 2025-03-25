import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

def get_db_connection(data_path):
    conn = sqlite3.connect(data_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_spend_path_minutes(path):
    departure_time = datetime.strptime(path[0]["departure_time"], '%Y-%m-%d %H:%M')
    arrive_time = datetime.strptime(path[-1]["arrival_time"], '%Y-%m-%d %H:%M')
    spend_time = arrive_time - departure_time
    return spend_time.total_seconds() / 60

class Transportation(ABC):
    def __init__(self, departure_time: str, start: str, end: str, folder: str):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        self.data_path = r"../data/" + folder
        self.paths = []

    @abstractmethod
    def __create_path(self):
        pass

    @abstractmethod
    def __create_time(self):
        pass

    @abstractmethod
    def __create_cost(self):
        pass

    def create(self):
        try:
            self.__create_path()
            self.__create_time()
            self.__create_cost()
        except Exception as e:
            self.paths = []
            print(e)
            # raise e
        return self.paths