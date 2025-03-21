from datetime import datetime, timedelta
from importlib.metadata import files

from transportation import Transportation, get_db_connection

"""
轉乘路線站點
     樹林→台東 x 潮州→基隆 : 臺北
     潮州→基隆 x 台東→枋寮→新左營 : 高雄
     台東→枋寮→新左營 x 樹林→台東 : 臺東
"""
class ExpressTrain(Transportation):
    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end, "Express_Train/")

        self.Caozhou_Jilong = {"to": "西部往北（潮州→基隆）.db", "from": "西部往南（基隆→潮州).db"}
        self.Taidong_Shulin = {"to": "東部往北（臺東→樹林）.db", "from": "東部往南（樹林→臺東).db"}
        self.Taidong_Xinzuoying = {"to": "南迴往西（臺東→枋寮→新左營）.db", "from": "南迴往東（新左營→枋寮→臺東）.db"}

    # 找尋車站在哪個表之中
    def find_table(self, station_name):
        files = [self.Caozhou_Jilong["to"], self.Taidong_Shulin["to"], self.Taidong_Xinzuoying["to"]]

        file_set = set()

        for file_name in files:
            conn = get_db_connection(self.data_path + file_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM train WHERE 車站 = ?", (station_name,))
            result = cursor.fetchone()
            conn.close()
            if result:
                file_set.add(file_name)

        if len(file_set) != 0:
            return file_set

        raise ValueError(f"{station_name} is not found in any of the databases")

    def check_route_direction(self, db_file, start_station, end_station):
        conn = get_db_connection(self.data_path + db_file)
        cursor = conn.cursor()

        cursor.execute(f"""SELECT 車站 FROM train 
                            WHERE 車站 IN ('{start_station}', '{end_station}') 
                            ORDER BY rowid;""")
        records = cursor.fetchone()
        conn.close()
        if records is None:
            raise ValueError(f"Cannot find a valid route from {start_station} to {end_station} in {db_file}")
        return records[0] == start_station

    def create_path(self):
        file1= self.find_table(self.start)
        file2 = self.find_table(self.end)
        same_file = file1.intersection(file2)
        if len(same_file):
            same_file = same_file.pop()
            file_set = frozenset({same_file, same_file})
        else:
            file1 = file1.pop()
            file2 = file2.pop()
            file_set = frozenset({file1, file2})

        transfer_points = {
            frozenset({self.Caozhou_Jilong["to"], self.Taidong_Shulin["to"]}): "臺北",
            frozenset({self.Taidong_Shulin["to"], self.Taidong_Xinzuoying["to"]}): "臺東",
            frozenset({self.Caozhou_Jilong["to"], self.Taidong_Xinzuoying["to"]}): "高雄"
        }

        reverse_direction = {self.Caozhou_Jilong["to"]: self.Caozhou_Jilong["from"],
                           self.Taidong_Shulin["to"]: self.Taidong_Shulin["from"],
                           self.Caozhou_Jilong["to"]: self.Taidong_Shulin["from"]}

        if file_set in transfer_points:
            transfer_station = transfer_points[file_set]

            if not self.check_route_direction(file1, self.start, transfer_station):
                file1 = reverse_direction[file1]
            if not self.check_route_direction(file2, transfer_station, self.end):
                file2 = reverse_direction[file2]

            self.paths = [[
                {"type": "Express_Train", "file": file1, "departure_place": self.start,
                 "arrival_place": transfer_station},
                {"type": "Express_Train", "file": file2, "departure_place": transfer_station,
                 "arrival_place": self.end}
            ]]
        else:
            self.paths = [[{"type": "Express_Train", "file": same_file, "departure_place": self.start,
                            "arrival_place": self.end}
            ]]

    def create_time(self):
        if len(self.paths[0]) == 1:  # 不需轉車
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
            self.paths[1][0].update(first_leg_cheapest_train)
            self.paths[1][1].update(second_leg_cheapest_train)

    def find_best_train(self, db_file, departure_station, arrival_station, min_departure_time=None):
        date_part, time_part = self.departure_time.split(' ')
        if min_departure_time is not None:
            time_part = datetime.strptime(self.departure_time, '%Y-%m-%d %H:%M').strftime('%H:%M')
        min_departure_time_datatime = datetime.strptime(time_part, "%H:%M")

        conn = get_db_connection(self.data_path + db_file)
        cursor = conn.cursor()

        # 取得所有列車編號
        cursor.execute("PRAGMA table_info(train);")
        columns = [col[1] for col in cursor.fetchall() if col[1] not in ("車站", "距離")]

        available_trains = []

        for train_no in columns:
            query = f"""
            SELECT t1.車站 AS 出發站, t1."{train_no}" AS 出發時間, 
                   t2.車站 AS 到達站, t2."{train_no}" AS 到達時間
            FROM train t1
            JOIN train t2 ON t1."{train_no}" IS NOT NULL 
                          AND t2."{train_no}" IS NOT NULL
                          AND t1."{train_no}" != '↓' 
                          AND t2."{train_no}" != '↓' 
            WHERE t1.車站 = ? 
              AND t2.車站 = ?
            ORDER BY t1."{train_no}";

            """
            cursor.execute(query, (departure_station, arrival_station))
            results = cursor.fetchall()

            for row in results:
                train_data = {
                    "transportation_name": train_no,
                    # "departure_station": row[0],
                    "departure_time": row[1],
                    # "arrival_station": row[2],
                    "arrival_time": row[3],
                }

                # 將時間字串轉換為 datetime 對象
                departure_time = datetime.strptime(train_data["departure_time"], "%H:%M")

                # 確保出發時間比設定晚
                if departure_time > min_departure_time_datatime:
                    train_data["departure_time"] = date_part + " " + train_data["departure_time"]
                    if departure_time > datetime.strptime(train_data["arrival_time"], "%H:%M"):
                        date = datetime.strptime(date_part, "%Y-%m-%d")
                        date += timedelta(days=1)
                        train_data["arrival_time"] = date.strftime("%Y-%m-%d") + " " + train_data["arrival_time"]
                    else:
                        train_data["arrival_time"] = date_part + " " + train_data["arrival_time"]
                    available_trains.append(train_data)

        conn.close()

        if not available_trains:
            raise ValueError("No trains available")

        # 找到最快火車
        fastest_train = min(available_trains, key=lambda x: x["departure_time"])

        #找到最便宜火車（優先順序：莒光號 > 其他)
        cheapest_train = None
        for train in available_trains:
            if "莒光" in train["transportation_name"]:
                cheapest_train = train
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

                distance = max(float(arrival_distance) - float(departure_distance), 10)
                transportation_name = route.get("transportation_name")
                cost = 0
                for name, rate in (("莒光", 1.75), ("自強",2.27), ("普悠瑪", 2.27)):
                    if name  in transportation_name:
                        cost = rate * distance
                        break
                if cost == 0:
                    raise ValueError(f"transportation {transportation_name} not in 莒光, 自強 or 普悠瑪")

                route.update({"cost": round(cost)})