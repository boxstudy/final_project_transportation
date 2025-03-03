import sqlite3
from datetime import datetime
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
        self.data_path = data_path + "/Express_Train/"
        self.paths = [[]]

    # 找尋車站在哪個表之中
    def find_table(self, station_name, file_name=None):
        files = ["西部往北潮州基隆.db", "東部往北臺東樹林.db", "南迴往西臺東枋寮新左營.db"]

        if file_name is not None:
            i = files.index(file_name)
            if i != 0:
                files[0], files[i] = files[i], files[0]

        for file_name in files:
            conn = get_db_connection(self.data_path + file_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM train WHERE 車站 = ?", (station_name,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return file_name

        raise ValueError(f"{station_name} is not found in any of the databases")

    def create_path(self):
        file1= self.find_table(self.start)
        file2 = self.find_table(self.end, file1)
        file_set = frozenset({file1, file2})

        transfer_points = {
            frozenset({"西部往北潮州基隆.db", "東部往北臺東樹林.db"}): "臺北",
            frozenset({"東部往北臺東樹林.db", "南迴往西臺東枋寮新左營.db"}): "臺東",
            frozenset({"西部往北潮州基隆.db", "南迴往西臺東枋寮新左營.db"}): "高雄"
        }

        if file_set in transfer_points:
            transfer_station = transfer_points[file_set]
            self.paths = [[
                {"type": "Express_Train", "file": file1, "departure_place": self.start,       "arrival_place": transfer_station},
                {"type": "Express_Train", "file": file2, "departure_place": transfer_station, "arrival_place": self.end}
            ]]
        else:
            self.paths = [[{"type": "Express_Train", "file": file1, "departure_place": self.start, "arrival_place": self.end}]]

    def create_time(self):
        if len(self.paths) == 1:  # 不需轉車
            fastest_train, cheapest_train = self.find_best_train(self.paths[0][0]["file"], self.start, self.end)
            self.paths *= 2  # fast path, cheap path
            self.paths[0][0].update(fastest_train)
            self.paths[1][0].update(cheapest_train)
        else:  # 需轉車
            transfer_station = self.paths[0][0]["arrival_place"]
            first_leg_file = self.paths[0][0]["file"]
            second_leg_file = self.paths[0][1]["file"]

            # 取得第一段所有列車
            first_leg_fastest_train, first_leg_cheapest_train = self.find_best_train(first_leg_file, self.start, transfer_station)

            # 取得所有可銜接的第二段列車(最快)
            second_leg_fastest_train, _ = self.find_best_train(second_leg_file, transfer_station, self.end, first_leg_fastest_train["arrival_time"])

            # 取得所有可銜接的第二段列車(最便宜)
            _, second_leg_cheapest_train = self.find_best_train(second_leg_file, transfer_station, self.end, first_leg_cheapest_train["arrival_time"])

            self.paths *= 2  # fast path, cheap path
            self.paths[0][0].update(first_leg_fastest_train)
            self.paths[0][1].update(second_leg_fastest_train)
            self.paths[1][0].updata(first_leg_cheapest_train)
            self.paths[1][1].update(second_leg_cheapest_train)

    def find_best_train(self, db_file, departure_station, arrival_station, min_departure_time=None):
        conn = get_db_connection(self.data_path + db_file)
        cursor = conn.cursor()

        # 取得所有列車編號
        cursor.execute("PRAGMA table_info(train);")
        columns = [col[1] for col in cursor.fetchall() if col[1] != "車站"]

        available_trains = []

        for train_no in columns:
            query = f"""
            SELECT t1.車站 AS 出發站, t1."{train_no}" AS 出發時間, 
                t2.車站 AS 到達站, t2."{train_no}" AS 到達時間
            FROM train t1
            JOIN train t2 ON t1."{train_no}" IS NOT NULL AND t2."{train_no}" IS NOT NULL
            WHERE t1.車站 = ? AND t2.車站 = ?
            AND t1."{train_no}" < t2."{train_no}"
            ORDER BY t1."{train_no}";
            """
            cursor.execute(query, (departure_station, arrival_station))
            results = cursor.fetchall()

            for row in results:
                train_data = {
                    "transportation_name": train_no,
                    "departure_station": row[0],
                    "departure_time": row[1],
                    "arrival_station": row[2],
                    "arrival_time": row[3],
                }

                # 將時間字串轉換為 datetime 對象
                departure_time = datetime.strptime(train_data["departure_time"], "%H:%M")
                min_departure_time_datatime = datetime.strptime(min_departure_time, "%H:%M")

                # 如果是轉乘，確保出發時間比上一段晚
                if min_departure_time is None or departure_time > min_departure_time_datatime:
                    available_trains.append(train_data)

        conn.close()

        if not available_trains:
            return None

        # 找到最快火車
        fastest_train = min(available_trains, key=lambda x: x["departure_time"])

        #找到最便宜火車（優先順序：莒光號 > 自強號 > 其他）
        cheapest_train = None
        for priority in ["莒光號", "自強號"]:
            for train in available_trains:
                if priority in train["transportation_name"]:
                    cheapest_train = train
                    break
            if cheapest_train:
                break

        if cheapest_train is None:
            cheapest_train = fastest_train

        return fastest_train, cheapest_train

    def create_cost(self):
        for path_i in range(len(self.paths)):
            for route_i in range(len(self.paths[path_i])):
                route = self.paths[path_i][route_i]
                conn = get_db_connection(self.data_path + route.get("file"))
                cursor = conn.cursor()
                cursor.execute("""
                                SELECT 
                                    (SELECT 距離 FROM train WHERE 車站 = ?) AS 出發距離,
                                    (SELECT 距離 FROM train WHERE 車站 = ?) AS 到達距離
                                """, (route.get("departure_place"), route.get("arrival_place")))
                departure_distance, arrival_distance = cursor.fetchone()
                conn.close()

                distance = max(arrival_distance - departure_distance, 10)
                transportation_name = route.get("transportation_name")
                cost = 0
                for name, rate in (("莒光", 1.75), ("自強",2.27), ("普悠瑪", 2.27)):
                    if name  in transportation_name:
                        cost = rate * distance
                        break
                if cost == 0:
                    raise ValueError(f"transportation {transportation_name} not in 莒光, 自強 or 普悠瑪")

                route.update({"cost": cost})



    def create(self):
        self.create_path()
        self.create_time()
        self.create_cost()
        return self.paths

class TransportationPath:
    def __init__(self):
        pass

    def get(self, start_date, from_place, to_place):
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
        train = Train(departure_time=start_date, start=from_place, end=to_place)
        train_paths = train.create()
        for i in range(len(paths)):
            for train_path in train_paths:
                paths[i] += train_path

        # Implement the logic to get the transportation path from the train station to the closest location to the target.

        return paths