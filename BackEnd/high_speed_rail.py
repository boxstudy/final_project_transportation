from transportation import Transportation, get_db_connection, DATA_PATH, TransportationError
import datetime


class HighSpeedRail(Transportation):
    stations = {
        "高鐵左警", "臺南", "嘉義", "雲林", "彰化", "高鐵臺中", "苗栗", "新竹", "桃園", "板橋", "臺北", "南港"
    }

    data_path = DATA_PATH + "High_Speed_Rail/"

    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end, self.stations)

        self.discount = discount
        self.reserved_table = "reserved" if reserved is True else "non-reserved"

        self.ZuoYing_NanGang = {"to": "往北.db", "from": "往南.db"}

    def _check_route_direction(self, file, start_station, end_station):
        conn = get_db_connection(self.data_path + file)
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                            SELECT 車站 FROM train 
                            WHERE 車站 IN ('{start_station}', '{end_station}') 
                            ORDER BY rowid;""")
            records = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        # i = 0
        # for _ in records:
        #     i += 1
        # if i < 2:
        #     raise TransportationError(f"Cannot find a valid route from {start_station} to {end_station} in {file}")
        return records[0][0] == start_station

    def _create_path(self):
        file = self.ZuoYing_NanGang["to"]
        if not self._check_route_direction(file, self.start, self.end):
            file = self.ZuoYing_NanGang["from"]
        self.paths = [[{"type": "HighSpeedRail", "file": file, "departure_place": self.start,
                        "arrival_place": self.end}]]

    def _create_time(self):
        for path in self.paths:
            for route in path:
                # 轉換日期為星期幾 (1 = 週一, 2 = 週二, ...)
                weekday = datetime.datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M").weekday() + 1

                conn = get_db_connection(self.data_path + route["file"])
                cursor = conn.cursor()
                try:
                    # 取得 available_day 資料表中的所有車次名稱（欄位名）
                    cursor.execute("PRAGMA table_info(available_day)")
                    columns = [col[1] for col in cursor.fetchall() if col[1] != "行駛日"]

                    # 查詢當天有運行的所有車次
                    cursor.execute(f"SELECT * FROM available_day WHERE 行駛日 = {weekday}")
                    row = cursor.fetchone()

                    if not row:
                        return

                    # 取得當天有行駛的車次（欄位值為 'T'）
                    available_trains = [columns[i] for i, val in enumerate(row[1:]) if val == 'T'] #row表示車次T或F

                    if not available_trains:
                        return

                    # 建立查詢的 SQL
                    valid_trains_sql = ', '.join([f'"{t}"' for t in available_trains])

                    # 查詢起訖站的所有車次時刻
                    cursor.execute(f"""
                        SELECT 車站, {valid_trains_sql}
                        FROM train
                        WHERE 車站 IN ('{self.start}', '{self.end}')
                        ORDER BY rowid
                    """)
                    rows = cursor.fetchall()    #rows表示
                finally:
                    cursor.close()
                    conn.close()

                # 建立站點對應的時間表
                station_times = {}
                for row in rows:
                    station_name = row[0]  # 車站名稱
                    station_times[station_name] = row[1:]  # 該站對應所有車次的時間

                # 確保 start 和 end 站點存在
                if self.start in station_times and self.end in station_times:
                    start_times = station_times[self.start]
                    end_times = station_times[self.end]

                    # 轉換 self.departure_time 為 datetime 物件
                    self_departure_dt = datetime.datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M")

                    # 找到最早的可行車次
                    for i, train_no in enumerate(available_trains):
                        start_time = start_times[i]
                        end_time = end_times[i]

                        # 確保該火車在出發站與目的地都停靠（非 NULL 且非 '↓'）
                        if start_time not in (None, '↓') and end_time not in (None, '↓'):
                            # 轉換火車的出發時間為 datetime
                            train_departure_dt = datetime.datetime.strptime(start_time, "%H:%M")

                            # 確保班次出發時間晚於 self.departure_time
                            if train_departure_dt.time() >= self_departure_dt.time():
                                # 直接使用 self_departure_dt 的日期
                                format_departure_time = datetime.datetime.combine(self_departure_dt.date(),
                                                                                  train_departure_dt.time())

                                # 轉換抵達時間
                                train_arrival_dt = datetime.datetime.strptime(end_time, "%H:%M")
                                format_arrival_time = datetime.datetime.combine(self_departure_dt.date(),
                                                                                train_arrival_dt.time())

                                # 如果抵達時間是 "00:XX"，則應該是隔天
                                if train_arrival_dt.strftime("%H") == "00":
                                    format_arrival_time += datetime.timedelta(days=1)

                                # 更新路徑資訊
                                if train_no:
                                    route.update({
                                        "train_number": train_no,
                                        "departure_time": format_departure_time.strftime("%Y-%m-%d %H:%M"),
                                        "arrival_time": format_arrival_time.strftime("%Y-%m-%d %H:%M")
                                    })
                                    self.paths[0][0].update({"train_number": train_no})

                                break  # 找到第一個符合條件的班次就結束




    def _create_cost(self):
        for path_i in range(len(self.paths)):
            for route_i in range(len(self.paths[path_i])):
                route = self.paths[path_i][route_i]

                a = route.get("departure_place")
                b = route.get("arrival_place")

                if self.discount is False:
                    a, b = b, a

                conn = get_db_connection(self.data_path + "價格.db")
                cursor = conn.cursor()

                try:
                    cursor.execute(f"""
                                    SELECT {a}
                                    FROM '{self.reserved_table}'
                                    WHERE 車站 in ('{b}')""")
                    records = cursor.fetchone()
                finally:
                    cursor.close()
                    conn.close()

                route.update({"cost": int(records[0])})