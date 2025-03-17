from transportation import Transportation, get_db_connection
import datetime


class HighSpadeRail(Transportation):
    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end, "High_Speed_Rail/")

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
        conn.close()
        if records is None:
            raise ValueError(f"Cannot find a valid route from {start_station} to {end_station} in {db_file}")
        return records[0] == start_station

    def create_path(self):
        file = self.ZuoYing_NanGang["to"]
        if not self.check_route_direction(file, self.start, self.end):
            file = self.ZuoYing_NanGang["from"]
        self.paths = [[{"type": "HighSpeedRail", "file": file, "departure_place": self.start,
                        "arrival_place": self.end}]]

    import datetime

    def create_time(self):
        for path in self.paths:
            for route in path:
                conn = get_db_connection(self.data_path + route.get("file"))
                cursor = conn.cursor()

                # 轉換日期為星期幾 (1 = 週一, 2 = 週二, ...)
                weekday = datetime.datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M").weekday() + 1

                # 取得 available_day 資料表中的所有車次名稱（欄位名）
                cursor.execute("PRAGMA table_info(available_day)")
                columns = [col[1] for col in cursor.fetchall() if col[1] != "行駛日"]

                # 查詢當天有運行的所有車次
                cursor.execute(f"SELECT * FROM available_day WHERE 行駛日 = {weekday}")
                row = cursor.fetchone()

                if not row:
                    conn.close()
                    return

                # 取得當天有行駛的車次（欄位值為 'T'）
                available_trains = [columns[i] for i, val in enumerate(row[1:]) if val == 'T']

                if not available_trains:
                    conn.close()
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
                rows = cursor.fetchall()

                # 建立站點對應的時間表
                station_times = {row[0]: row[1:] for row in rows}

                # 確保 start 和 end 站點存在
                if self.start in station_times and self.end in station_times:
                    start_times = station_times[self.start]
                    end_times = station_times[self.end]

                    selected_train = None
                    selected_departure_time = None
                    selected_arrival_time = None

                    # 轉換 self.departure_time 為 datetime 物件
                    self_departure_dt = datetime.datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M")

                    # 找到最早的可行車次
                    for i, train_no in enumerate(available_trains):
                        start_time = start_times[i]
                        end_time = end_times[i]

                        # 確保該火車在出發站與目的地都停靠（非 NULL 且非 '↓'）
                        if start_time not in (None, '↓') and end_time not in (None, '↓'):
                            try:
                                # 轉換火車的出發時間為 datetime
                                train_departure_dt = datetime.datetime.strptime(start_time, "%H:%M")

                                # 確保班次出發時間晚於 self.departure_time
                                if train_departure_dt.time() >= self_departure_dt.time():
                                    selected_train = train_no
                                    selected_departure_time = start_time
                                    selected_arrival_time = end_time
                                    break  # 找到第一個符合條件的班次就結束
                            except ValueError:
                                continue  # 如果時間格式錯誤，跳過該班車

                # 更新路徑資訊
                if selected_train:
                    route.update({
                        "train_number": selected_train,
                        "departure_time": selected_departure_time,
                        "arrival_time": selected_arrival_time
                    })

                conn.close()

    def create_cost(self):
        for path_i in range(len(self.paths)):
            for route_i in range(len(self.paths[path_i])):
                route = self.paths[path_i][route_i]
                conn = get_db_connection(self.data_path + "價格.db")
                cursor = conn.cursor()

                a = route.get("departure_place")
                b = route.get("arrival_place")

                if self.discount is False:
                    a, b = b, a

                cursor.execute(f"""
                                SELECT {a}
                                FROM {self.reserved_table}
                                WHERE 車站 in ('{b}')""")
                records = cursor.fetchone()

                route.update({"cost": records[0]})
                conn.close()