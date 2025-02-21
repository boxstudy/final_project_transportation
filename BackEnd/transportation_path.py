import sqlite3
from os import abort

data_path = r"../data"


def get_db_connection(data_path):
    conn = sqlite3.connect(data_path)
    conn.row_factory = sqlite3.Row
    return conn

"""
轉乘路線站點
     樹林→台東 x 潮州→基隆 : 臺北
     潮州→基隆 x 台東→枋寮→新左營 : 高雄
     台東→枋寮→新左營 x 樹林→台東 : 臺東
"""
class Train:
    def __init__(self, departure_time, start, end):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        self.path = []

    # 找尋車站在哪個表之中
    def find_table(self, station_name):
        train_data_path = data_path + "/Express_Train/"
        files = ["西部往北（潮州→基隆）.db", "東部往北（臺東→樹林）.db", "南迴往西（臺東→枋寮→新左營）.db"]
        for file_name in files:
            conn = get_db_connection(train_data_path + file_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM train WHERE 車站 = ?", (station_name,))
            result = cursor.fetchall()
            conn.close()
            if result:
                return file_name
        print(f"{station_name} is not found in database")
        abort()

    def create_path(self):
        (file1, file2) = self.find_table(self.start), self.find_table(self.end)
        file_set = frozenset({file1, file2})  # 改為 frozenset，使其可哈希

        transfer_points = {
            frozenset({"西部往北（潮州→基隆）.db", "東部往北（臺東→樹林）.db"}): "臺北",
            frozenset({"東部往北（臺東→樹林）.db", "南迴往西（臺東→枋寮→新左營）.db"}): "臺東",
            frozenset({"西部往北（潮州→基隆）.db", "南迴往西（臺東→枋寮→新左營）.db"}): "高雄"
        }

        if file_set in transfer_points:
            self.path = [
                {"name": file1, "departure_place": self.start, "arrival_place": transfer_points[file_set]},
                {"name": file2, "departure_place": transfer_points[file_set], "arrival_place": self.end}
            ]
            return

        self.path = [{"name": file1, "departure_place": self.start, "arrival_place": self.end}]

    def create_time(self):
        if len(self.path) == 1:
            
            for i in self.path:
            conn = get_db_connection(data_path + "/Express_Train/" + i["name"])
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM train WHERE 車站 = ?", (i["arrival_place"],))
            result = cursor.fetchone()
            print(result)
            # i["arrival_time"] = result["時間"]
            # cursor.execute("SELECT * FROM train WHERE 車站 = ?", i["departure_place"])
            # result = cursor.fetchone()
            # i["departure_time"] = result["時間"]
            conn.close()

    def create_cost(self):
        pass

    def create(self):
        self.create_path()
        self.create_time()
        self.create_cost()
        return self.path

class TransportationPath:
    def __init__(self):
        pass

    def get(self, start_date, from_place, to_place):
        # path = [
        #         # path 1
        #         [{"type": "train", "name": "Train 201", "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:00", "arrival_time": "2025/02/01-10:30", "cost": 100},
        #          {"type": "bus",   "name": "Bus 203",   "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:30", "arrival_time": "2025/02/01-11:00", "cost": 100}],
        #
        #         # path 2
        #         []
        # ]
        path = []

        # Implement the logic to get the transportation path to the train station.

        # Implement the logic to get the transportation path between two train station to the closest location to the target.
        train = Train(departure_time=start_date, start=from_place, end=to_place)
        path.append(train.create())

        # Implement the logic to get the transportation path from the train station to the closest location to the target.

        return path