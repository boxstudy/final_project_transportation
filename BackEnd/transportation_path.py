import sqlite3
from abc import ABC, abstractmethod

from express_train import ExpressTrain
from high_spead_rail import HighSpadeRail


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



class TransportationPath:
    def __init__(self):
        self.priority = [""]

    def get(self, start_date: str, from_place: str, to_place: str):
        # path = [
        #         # path 1
        #         [{"type": "train", "transportation_name": "Train 201", "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:00", "arrival_time": "2025/02/01-10:30", "cost": 100},
        #          {"type": "bus",   "transportation_name": "Bus 203",   "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:30", "arrival_time": "2025/02/01-11:00", "cost": 100}],
        #
        #         # path 2
        #         []
        # ]
        paths = [[]]

        # Implement the logic to get the transportation path to the train station.

        # Implement the logic to get the transportation path between two train station to the closest location to the target.
        train = ExpressTrain(departure_time=start_date, start=from_place, end=to_place)
        train_paths = train.create()
        paths = train_paths

        # Implement the logic to get the transportation path from the train station to the closest location to the target.

        return paths