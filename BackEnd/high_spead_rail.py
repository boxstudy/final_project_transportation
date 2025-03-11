from click.types import BoolParamType

from transportation_path import get_db_connection
from transportation_path import data_path


class HighSpadeRail:
    def __init__(self, departure_time, start, end, discount, reserved):
        self.departure_time = departure_time
        self.__start = start
        self.__end = end
        self.data_path = data_path + "/High_Speed_Rail"
        self.paths = [[]]

        self.discount = discount
        self.reserved_table = "reserved" if reserved is True else "non-reserved"

        self.ZuoYing_NanGang = {"to": "往北.db", "from": "往南.db"}

    def check_route_direction(self, db_file, start_station, end_station):

        conn = get_db_connection(self.data_path + db_file)
        cursor = conn.cursor()

        cursor.execute(f"""
                        SELECT 車站 FROM train 
                        WHERE 車站 IN ('{start_station}', '{end_station}') 
                        ORDER BY rowid;""")
        records = cursor.fetchone()
        return records[0] == start_station

    def create_path(self):
        file = self.ZuoYing_NanGang["to"]
        if not self.check_route_direction(file, self.__start, self.__end):
            file = self.ZuoYing_NanGang["from"]
        self.paths = [[{"type": "HighSpeedRail", "file": file, "departure_place": self.__start,
                        "arrival_place": self.__end}]]

    def create_time(self):
        for path in self.paths:
            for route in path:
                conn = get_db_connection(self.data_path + route.get("file"))
                cursor = conn.cursor()

                # 查詢當天有行駛的車次
                cursor.execute(f"""
                                SELECT train_no FROM available_day 
                                WHERE {self.travel_date} = 'T'""")
                available_trains = cursor.fetchall()
                available_trains = tuple(t[0] for t in available_trains)

                # 確保車次停靠出發站和目的地
                cursor.execute(f"""
                                SELECT train_no FROM higtrail 
                                WHERE train_no IN {available_trains} 
                                AND "{self.__start}" IS NOT NULL AND "{self.__start}" != '↓' 
                                AND "{self.__end}" IS NOT NULL AND "{self.__end}" != '↓'""")
                valid_trains = cursor.fetchall()
                valid_trains = tuple(t[0] for t in valid_trains)

                # 查詢最近的符合條件的車次
                cursor.execute(f"""
                                SELECT train_no, departure_time, arrival_time 
                                FROM higtrail 
                                WHERE train_no IN {valid_trains} 
                                AND departure_time >= '{self.departure_time}' 
                                ORDER BY departure_time ASC 
                                LIMIT 1""")
                record = cursor.fetchone()

                if record:
                    route.update({
                        "train_number": record[0],
                        "departure_time": record[1],
                        "arrival_time": record[2]
                    })
                conn.close()
            

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
        return self.paths