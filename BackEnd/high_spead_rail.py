from click.types import BoolParamType

from transportation_path import get_db_connection
from transportation_path import data_path


class HighSpadeRail:
    def __init__(self, departure_time, start, end, discount, reserved):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        self.data_paths = data_path + "/High_Speed_Rail"
        self.paths = [[]]

        self.discount = discount
        self.reserved_table = "reserved" if reserved is True else "non-reserved"

        self.ZuoYing_NanGang = {"to": "往北.db", "from": "往南.db"}

    def check_route_availability(self, db_file, start_station, end_station):

        conn = get_db_connection(self.data_paths + db_file)
        cursor = conn.cursor()

        cursor.execute(f"""
                        SELECT 車站 FROM train 
                        WHERE 車站 IN ('{start_station}', '{end_station}') 
                        ORDER BY rowid;""")
        records = cursor.fetchone()
        return records[0] == start_station

    def create_path(self):
        file = self.ZuoYing_NanGang["to"]
        if not self.check_route_availability(file, self.__start, self.__end):
            file = self.ZuoYing_NanGang["from"]
        self.paths = [[{"type": "HighSpeedRail", "file": file, "departure_place": self.__start,
                        "arrival_place": self.__end}]]

    def create_time(self):
        pass

    def create_cost(self):
        for path_i in range(len(self.paths)):
            for route_i in range(len(self.paths[path_i])):
                route = self.paths[path_i][route_i]
                conn = get_db_connection(self.data_path + route.get("file"))
                cursor = conn.cursor()

                a = route.get("departure_place")
                b = route.get("arrival_place")

                if self.discount is False:
                    a, b = b, a

                cursor.execute(f"""
                                SELECT {a}
                                FROM {self.reserved_table}
                                 WHERE 車站 IN ('{b}'))""")
                records = cursor.fetchone()

                route.update({"cost": round(records[0])})

    def create(self):
        self.create_path()
        self.create_time()
        self.create_cost()

    def get_path(self):
        return self.paths