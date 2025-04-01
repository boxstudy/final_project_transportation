import copy
from datetime import datetime, timedelta

from transportation import Transportation, get_db_connection, DATA_PATH

"""
轉乘路線站點
     樹林→台東 x 潮州→基隆 : 臺北
     潮州→基隆 x 台東→枋寮→新左營 : 高雄
     台東→枋寮→新左營 x 樹林→台東 : 臺東
"""
class ExpressTrain(Transportation):

    Caozhou_Jilong = {"to": "西部往北（潮州→基隆）.db", "from": "西部往南（基隆→潮州).db"}
    Shulin_Taidong = {"to": "東部往南（樹林→臺東).db", "from": "東部往北（臺東→樹林）.db"}
    Taidong_Xinzuoying = {"to": "南迴往西（臺東→枋寮→新左營）.db", "from": "南迴往東（新左營→枋寮→臺東）.db"}
    data_path = DATA_PATH + "Express_Train/"

    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end)

    def _count_distance(self, place1, place2, file):
        # print(f"place1: {place1}, place2: {place2}, file: {file}")
        conn = get_db_connection(self.data_path + file)
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                             SELECT 
                                (SELECT 距離 FROM train WHERE 車站 = ?) AS 出發距離,
                                (SELECT 距離 FROM train WHERE 車站 = ?) AS 到達距離
                                    
                            """, (place1, place2))
            distance1, distance2 = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        return abs(float(distance2) - float(distance1))

    # 找尋車站在哪個表之中
    def _find_table(self, station_name):
        files = [self.Caozhou_Jilong["to"], self.Shulin_Taidong["to"], self.Taidong_Xinzuoying["to"]]

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

    def _check_route_direction(self, file, start_station, end_station):
        conn = get_db_connection(self.data_path + file)
        cursor = conn.cursor()
        try:
            cursor.execute(f"""SELECT 車站 FROM train 
                                WHERE 車站 IN ('{start_station}', '{end_station}') 
                                ORDER BY rowid;""")
            records = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if records is None:
            raise ValueError(f"Cannot find a valid route from {start_station} to {end_station} in {file}")
        return records[0] == start_station

    def _create_path(self):
        # 順時針
        clockwise_to_file = {"高雄": self.Caozhou_Jilong["to"], "臺北": self.Shulin_Taidong["to"], "臺東": self.Taidong_Xinzuoying["to"]}
        # 逆時針
        counterclockwise_to_file = {"臺北": self.Caozhou_Jilong["to"], "臺東": self.Taidong_Xinzuoying["to"], "高雄": self.Taidong_Xinzuoying["to"]}
        file_to_start_end = {self.Caozhou_Jilong["to"]: ("高雄", "臺北"), self.Shulin_Taidong["to"]: ("臺北", "臺東"), self.Taidong_Xinzuoying["to"]: ("臺東", "高雄")}
        
        files1= self._find_table(self.start)
        files2 = self._find_table(self.end)
        if len(files1) == 0 or len(files2) == 0:
            raise ValueError(f"Cannot find a valid route from {self.start} to {self.end}")

        same_file = files1.intersection(files2)
        if len(same_file) > 0:
            same_file = same_file.pop()
            file_set = frozenset({same_file, same_file})
        else:
            file1 = files1.pop()
            file2 = files2.pop()
            if len(files1) == 0 and len(files2) == 0:
                file_set = frozenset({file1, file2})
            elif len(files1) == 0:
                start, end = file_to_start_end[file1]
                distance1 = self._count_distance(start, self.start, file1) + self._count_distance(start, self.end, counterclockwise_to_file[start])
                distance2 = self._count_distance(end, self.start, file1) + self._count_distance(end, self.end, clockwise_to_file[end])
                file2 = counterclockwise_to_file[start] if distance1 < distance2 else clockwise_to_file[end]
                file_set = frozenset({file1, file2})
            elif len(files2) == 0:
                start, end = file_to_start_end[file2]
                distance1 = (self._count_distance(start, self.end, file2) + self._count_distance(start, self.start, counterclockwise_to_file[start]))
                distance2 = self._count_distance(end, self.end, file2) + self._count_distance(end, self.start, clockwise_to_file[end])
                file1 = counterclockwise_to_file[start] if distance1 < distance2 else clockwise_to_file[end]
                file_set = frozenset({file1, file2})
            else:
                raise ValueError(f"Cannot find a valid route from {self.start} to {self.end}")

        transfer_points = {
            frozenset({self.Caozhou_Jilong["to"], self.Shulin_Taidong["to"]}): "臺北",
            frozenset({self.Shulin_Taidong["to"], self.Taidong_Xinzuoying["to"]}): "臺東",
            frozenset({self.Caozhou_Jilong["to"], self.Taidong_Xinzuoying["to"]}): "高雄"
        }

        reverse_direction = {self.Caozhou_Jilong["to"]: self.Caozhou_Jilong["from"],
                             self.Shulin_Taidong["to"]: self.Shulin_Taidong["from"],
                             self.Taidong_Xinzuoying["to"]: self.Taidong_Xinzuoying["from"]}

        if file_set in transfer_points:
            transfer_station = transfer_points[file_set]

            if not self._check_route_direction(file1, self.start, transfer_station):
                file1 = reverse_direction[file1]
            if not self._check_route_direction(file2, transfer_station, self.end):
                file2 = reverse_direction[file2]

            self.paths = [[
                {"type": "ExpressTrain", "file": file1, "departure_place": self.start,
                 "arrival_place": transfer_station},
                {"type": "ExpressTrain", "file": file2, "departure_place": transfer_station,
                 "arrival_place": self.end}
            ]]
        else:
            if not self._check_route_direction(same_file, self.start, self.end):
                same_file = reverse_direction[same_file]
            self.paths = [[{"type": "ExpressTrain", "file": same_file, "departure_place": self.start,
                            "arrival_place": self.end}
            ]]

    def _create_time(self):
        if len(self.paths[0]) == 1:  # 不需轉車
            fastest_train, cheapest_train = self._find_best_train(self.paths[0][0]["file"], self.start, self.end, 5)

            for data in fastest_train:
                l = copy.deepcopy(self.paths[0])
                l[0].update(data)
                self.paths.append(l)

            if cheapest_train is not None:
                self.paths[0][0].update(cheapest_train)
            else:
                self.paths.pop(0)

        else:  # 需轉車
            transfer_station = self.paths[0][0]["arrival_place"]
            first_leg_file = self.paths[0][0]["file"]
            second_leg_file = self.paths[0][1]["file"]

            # 取得第一段所有列車
            first_leg_fastest_train, first_leg_cheapest_train = self._find_best_train(first_leg_file, self.start, transfer_station,3)

            for i in range(len(first_leg_fastest_train)):
                # 取得所有可銜接的第二段列車(最快)
                second_leg_fastest_train, _ = self._find_best_train(second_leg_file, transfer_station, self.end, 1, first_leg_fastest_train[i]["arrival_time"])
                if second_leg_fastest_train is not None:
                    l = copy.deepcopy(self.paths[0])
                    l[0].update(first_leg_fastest_train[i])
                    l[1].update(second_leg_fastest_train[0])
                    self.paths.append(l)
            if self.paths:
                self.paths.pop(0)

            # 取得所有可銜接的第二段列車(最便宜)
            if first_leg_cheapest_train is None:
                _, second_leg_cheapest_train = self._find_best_train(second_leg_file, transfer_station, self.end, 1)
            else:
                _, second_leg_cheapest_train = self._find_best_train(second_leg_file, transfer_station, self.end, 1, first_leg_cheapest_train["arrival_time"])


            #更新最便宜路線火車1班
            if first_leg_cheapest_train is not None and second_leg_cheapest_train is not None:
                l = copy.deepcopy(self.paths[0])
                l[0].update(first_leg_cheapest_train)
                l[1].update(second_leg_cheapest_train)

            elif first_leg_cheapest_train is not None and second_leg_cheapest_train is None:
                l = copy.deepcopy(self.paths[0])
                l[0].update(first_leg_cheapest_train)
                l[1].update(second_leg_fastest_train[0])
                self.paths.append(l)
            elif first_leg_cheapest_train is None and second_leg_cheapest_train is not None:
                l = copy.deepcopy(self.paths[0])
                l[0].update(first_leg_fastest_train[0])
                l[1].update(second_leg_cheapest_train)
                self.paths.append(l)
            else:
                return None


    def _find_best_train(self, db_file, departure_station, arrival_station, number_of_trains = 1, min_departure_time=None):
        date_part, time_part = self.departure_time.split(' ')
        if min_departure_time is not None:
            time_part = datetime.strptime(min_departure_time, '%Y-%m-%d %H:%M').strftime('%H:%M')
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
                if departure_time >= min_departure_time_datatime:
                    train_data["departure_time"] = date_part + " " + train_data["departure_time"]
                    if departure_time >= datetime.strptime(train_data["arrival_time"], "%H:%M"):
                        date = datetime.strptime(date_part, "%Y-%m-%d")
                        date += timedelta(days=1)
                        train_data["arrival_time"] = date.strftime("%Y-%m-%d") + " " + train_data["arrival_time"]
                    else:
                        train_data["arrival_time"] = date_part + " " + train_data["arrival_time"]
                    available_trains.append(train_data)
        cursor.close()
        conn.close()

        if not available_trains:
            return [], None

        # 沒轉車找5班，有轉車找3班
        fastest_trains = sorted(available_trains, key=lambda x: x["arrival_time"])[:number_of_trains]

        #找到最便宜火車（優先順序：莒光號 > 其他)
        cheapest_train = None
        for train in available_trains:
            if "莒光" in train["transportation_name"]:
                cheapest_train = train
                break

        return fastest_trains, cheapest_train

    def _create_cost(self):
        for path_i in range(len(self.paths)):
            for route_i in range(len(self.paths[path_i])):
                route = self.paths[path_i][route_i]

                conn = get_db_connection(self.data_path + route["file"])
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                                    SELECT 
                                        (SELECT 距離 FROM train WHERE 車站 = ?) AS 出發距離,
                                        (SELECT 距離 FROM train WHERE 車站 = ?) AS 到達距離
                                    """, (route.get("departure_place"), route.get("arrival_place")))
                    departure_distance, arrival_distance = cursor.fetchone()
                finally:
                    cursor.close()
                    conn.close()
                distance = max(float(arrival_distance) - float(departure_distance), 10)
                # print(route["departure_place"], route["arrival_place"], distance, departure_distance, arrival_distance, route["file"])
                transportation_name = route.get("transportation_name")
                cost = 0
                for name, rate in (("莒光", 1.75), ("自強",2.27), ("普悠瑪", 2.27), ("太魯閣", 2.27)):
                    if name  in transportation_name:
                        cost = rate * distance
                        break
                if cost == 0:
                    raise ValueError(f"transportation {transportation_name} not in 莒光, 自強 or 普悠瑪")

                route.update({"cost": round(cost)})

if __name__ == "__main__":
    t = ExpressTrain("2025-08-26 11:42", "新烏日", "新竹")
    t.create()
    print(t.paths)