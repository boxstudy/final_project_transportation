import copy
from datetime import datetime, timedelta
from enum import Enum

from transportation import Transportation, get_db_connection, DATA_PATH, TransportationError

"""
轉乘站
    臺北, 新竹, 彰化, 嘉義, 高雄(新左營), 枋寮, 臺東, 花蓮, 蘇澳(新蘇澳)
"""
class LocalTrain(Transportation):
    file0 = {"to": "西區間(基隆→新竹).db", "from": "西區間(新竹→基隆).db"}
    file1 = {"to": "西區間(新竹→彰化).db", "from": "西區間(彰化→新竹).db"}
    file2 = {"to": "西區間(彰化→嘉義).db", "from": "西區間(嘉義→彰化).db"}
    file3 = {"to": "西區間(嘉義→高雄).db", "from": "西區間(高雄→嘉義).db"}
    file4 = {"to": "西區間(新左營→枋寮).db", "from": "西區間(枋寮→新左營).db"}
    file5 = {"to": "南迴(枋寮→臺東).db", "from": "南迴(臺東→枋寮).db"}
    file6 = {"to": "東區間(臺東→花蓮).db", "from": "東區間(花蓮→臺東).db"}
    file7 = {"to": "東區間(花蓮→蘇澳新).db", "from": "東區間(蘇澳新→花蓮).db"}
    file8 = {"to": "東區間(蘇澳→臺北).db", "from": "東區間(臺北→蘇澳).db"}

    file0_5 = {"to": "支區間(新竹→內灣).db", "from": "支區間(內灣→新竹).db"}
    file2_5 = {"to": "支區間(二水→濁水).db", "from": "支區間(濁水→二水).db"}
    file3_5 = {"to": "支區間(善化→沙崙).db", "from": "支區間(沙崙→善化).db"}
    file8_5 = {"to": "支區間(八堵→菁桐).db", "from": "支區間(菁桐→八堵).db"}

    class VehicleType(Enum):
        MAIN = 0x00
        MOUNTAIN = 0x01
        COAST = 0x02
        BRANCH = 0x10

    data_path = DATA_PATH + "Local_Train/"

    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end)
        self.paths = []
        self.vehicle_type_start = None
        self.vehicle_type_end = None

    def _create_path(self):
        file_start, self.vehicle_type_start = self._find_file(self.start)
        if file_start is None:
            raise TransportationError(f"Cannot find {self.start} in database")
        file_end, self.vehicle_type_end = self._find_file(self.end)
        if file_end is None:
            raise TransportationError(f"Cannot find {self.end} in database")

        if file_start == file_end:
            if self.vehicle_type_start == self.vehicle_type_end:
                match self.vehicle_type_start:
                    case self.VehicleType.MOUNTAIN:
                        table = "local_train_mountain"
                    case self.VehicleType.COAST:
                        table = "local_train_coast"
                    case _:
                        table = "local_train"
                self.paths = [[{
                    "type": "LocalTrain",
                    "file": file_start if self._count_distance(self.start, self.end, file_start, table) > 0 else self._reverse_file(file_start),
                    "departure_place": self.start,
                    "arrival_place": self.end
                }]]
            else:
                table_start = "local_train_coast" if self.vehicle_type_start == self.VehicleType.COAST else "local_train_mountain"
                table_end = "local_train_coast" if self.vehicle_type_end == self.VehicleType.COAST else "local_train_mountain"
                dis = (self._count_distance(self.start, "竹南", file_start, table_start),
                       self._count_distance("竹南", self.end, file_end, table_end),
                       self._count_distance(self.start, "彰化", file_start, table_start),
                       self._count_distance("彰化", self.end, file_end, table_end))
                d = (abs(dis[0]) + abs(dis[1])) - (abs(dis[2]) + abs(dis[3]))

                def reverse_file1(file):
                    if file != self.file1["to"]:
                        return self.file1["to"]
                    return self.file1["from"]
                if d > 20:
                    self.paths = [[{
                        "type": "LocalTrain",
                        "file": file_start if dis[2] >= 0 else reverse_file1(file_start),
                        "departure_place": self.start,
                        "arrival_place": "彰化"
                    },
                    {
                        "type": "LocalTrain",
                        "file": file_end if dis[3] >= 0 else reverse_file1(file_end),
                        "departure_place": "彰化",
                        "arrival_place": self.end
                    }]]
                elif d < -20:
                    self.paths = [[{
                        "type": "LocalTrain",
                        "file": file_start if dis[0] >= 0 else reverse_file1(file_start),
                        "departure_place": self.start,
                        "arrival_place": "竹南"
                    },
                    {
                        "type": "LocalTrain",
                        "file": file_end if dis[1] >= 0 else reverse_file1(file_end),
                        "departure_place": "竹南",
                        "arrival_place": self.end
                    }]]
                else:
                    self.paths = [[{
                        "type": "LocalTrain",
                        "file": file_start if dis[0] >= 0 else reverse_file1(file_start),
                        "departure_place": self.start,
                        "arrival_place": "竹南"
                    },
                    {
                        "type": "LocalTrain",
                        "file": file_end if dis[1] >= 0 else reverse_file1(file_end),
                        "departure_place": "竹南",
                        "arrival_place": self.end
                    }],
                    [{
                        "type": "LocalTrain",
                        "file": file_start if dis[2] >= 0 else reverse_file1(file_start),
                        "departure_place": self.start,
                        "arrival_place": "彰化"
                    },
                    {
                        "type": "LocalTrain",
                        "file": file_end if dis[3] >= 0 else reverse_file1(file_end),
                        "departure_place": "彰化",
                        "arrival_place": self.end
                    }]]
            return

        main_line_counter_clockwise = (
            self.file0["to"], self.file1["to"], self.file2["to"], self.file3["to"], self.file4["to"],
            self.file5["to"], self.file6["to"], self.file7["to"], self.file8["to"])
        main_line_clockwise = (
            self.file0["from"], self.file1["from"], self.file2["from"], self.file3["from"], self.file4["from"],
            self.file5["from"], self.file6["from"], self.file7["from"], self.file8["from"])
        branch_line_in = (
            self.file0_5["to"], None, self.file2_5["to"], self.file3_5["to"], None,
            None, None, None, self.file8_5["to"])
        branch_line_out = (
            self.file0_5["from"], None, self.file2_5["from"], self.file3_5["from"], None,
            None, None, None, self.file8_5["from"])

        "臺北 新竹 彰化 嘉義 高雄 枋寮 臺東 花蓮 蘇澳新 臺北"
        # -> counter_clockwise
        # <- clockwise
        dis_main_line = (78.1, 104.5, 80.9, 108, 61.3, 98.2, 150.9, 79.2, 114.8)
        map_main_line = (("臺北", "新竹", "新竹"), ("新竹", "彰化"), ("彰化", "嘉義", "二水"), ("嘉義", "高雄", "善化"),
                         ("高雄", "枋寮"), ("枋寮", "臺東"), ("臺東", "花蓮"), ("花蓮", "蘇澳新"),
                         ("蘇澳新", "臺北", "三貂嶺")) # (clockwise_station, counter_clockwise_station, branch_station)

        match self.vehicle_type_start:

            case self.VehicleType.BRANCH:
                if self._is_in(file_start):
                    start_i = branch_line_in.index(file_start)
                else:
                    start_i = branch_line_out.index(file_start)

            case _:
                if self._is_counter_clockwise(file_start):
                    start_i = main_line_counter_clockwise.index(file_start)
                else:
                    start_i = main_line_clockwise.index(file_start)

        match self.vehicle_type_end:

            case self.VehicleType.BRANCH:
                if self._is_in(file_end):
                    end_i = branch_line_in.index(file_end)
                else:
                    end_i = branch_line_out.index(file_end)

            case _:
                if self._is_counter_clockwise(file_end):
                    end_i = main_line_counter_clockwise.index(file_end)
                else:
                    end_i = main_line_clockwise.index(file_end)

        # counter_clockwise
        i = start_i
        path1 = []
        dis1 = 0
        if self.vehicle_type_start != self.VehicleType.BRANCH:
            if self.start != map_main_line[i][1]:
                path1.append({
                    "type": "LocalTrain",
                    "file": main_line_counter_clockwise[i],
                    "departure_place": self.start,
                    "arrival_place": map_main_line[i][1]
                })
                match self.vehicle_type_start:
                    case self.VehicleType.MOUNTAIN:
                        table = "local_train_mountain"
                    case self.VehicleType.COAST:
                        table = "local_train_coast"
                    case _:
                        table = "local_train"
                dis1 += self._count_distance(self.start, map_main_line[i][1],
                                            main_line_counter_clockwise[i], table)
        else:
            if self.start != map_main_line[i][2]:
                path1.append({
                    "type": "LocalTrain",
                    "file": branch_line_out[i],
                    "departure_place": self.start,
                    "arrival_place": map_main_line[i][2]
                })
                dis1 += self._count_distance(self.start, map_main_line[i][2],
                                            branch_line_out[i], "local_train")
            if map_main_line[i][2] != map_main_line[i][1]:
                path1.append({
                    "type": "LocalTrain",
                    "file": main_line_counter_clockwise[i],
                    "departure_place": map_main_line[i][2],
                    "arrival_place": map_main_line[i][1]
                })
                dis1 += self._count_distance(map_main_line[i][2], map_main_line[i][1],
                                            main_line_counter_clockwise[i], "local_train")
        i = (1 + i) % len(map_main_line)
        while i != end_i:
            path1.append({
                    "type": "LocalTrain",
                    "file": main_line_counter_clockwise[i],
                    "departure_place": map_main_line[i][0],
                    "arrival_place": map_main_line[i][1]
                })
            dis1 += dis_main_line[i]
            i = (1 + i) % len(map_main_line)
        if self.vehicle_type_end != self.VehicleType.BRANCH:
            if map_main_line[i][0] != self.end:
                path1.append({
                    "type": "LocalTrain",
                    "file": main_line_counter_clockwise[i],
                    "departure_place": map_main_line[i][0],
                    "arrival_place": self.end
                })
                match self.vehicle_type_end:
                    case self.VehicleType.MOUNTAIN:
                        table = "local_train_mountain"
                    case self.VehicleType.COAST:
                        table = "local_train_coast"
                    case _:
                        table = "local_train"
                dis1 += self._count_distance(map_main_line[end_i][0], self.end,
                                             main_line_counter_clockwise[i], table)
        else:
            if map_main_line[i][2] != map_main_line[i][0]:
                path1.append({
                    "type": "LocalTrain",
                    "file": main_line_counter_clockwise[i],
                    "departure_place": map_main_line[i][0],
                    "arrival_place": map_main_line[i][2]
                })
                dis1 += self._count_distance(map_main_line[end_i][0], map_main_line[i][2],
                                             main_line_counter_clockwise[i], "local_train")
            if branch_line_in[i] != map_main_line[i][2]:
                path1.append({
                    "type": "LocalTrain",
                    "file": branch_line_in[i],
                    "departure_place": map_main_line[i][2],
                    "arrival_place": self.end
                })
                dis1 += self._count_distance(map_main_line[end_i][2], self.end,
                                             branch_line_in[i], "local_train")

        # clockwise
        i = start_i
        path2 = []
        dis2 = 0
        if self.vehicle_type_start != self.VehicleType.BRANCH:
            if self.start != map_main_line[i][0]:
                path2.append({
                    "type": "LocalTrain",
                    "file": main_line_clockwise[i],
                    "departure_place": self.start,
                    "arrival_place": map_main_line[i][0]
                })
                match self.vehicle_type_start:
                    case self.VehicleType.MOUNTAIN:
                        table = "local_train_mountain"
                    case self.VehicleType.COAST:
                        table = "local_train_coast"
                    case _:
                        table = "local_train"
                dis2 += self._count_distance(self.start, map_main_line[i][0],
                                            main_line_clockwise[i], table)
        else:
            if self.start != map_main_line[i][2]:
                path2.append({
                    "type": "LocalTrain",
                    "file": branch_line_out[i],
                    "departure_place": self.start,
                    "arrival_place": map_main_line[i][2]
                })
                dis2 += self._count_distance(self.start, map_main_line[i][2],
                                            branch_line_out[start_i], "local_train")
            if map_main_line[i][2] != map_main_line[i][0]:
                path2.append({
                    "type": "LocalTrain",
                    "file": main_line_clockwise[i],
                    "departure_place": map_main_line[i][2],
                    "arrival_place": map_main_line[i][0]
                })
                dis2 += self._count_distance(map_main_line[i][2], map_main_line[i][0],
                                            main_line_clockwise[i], "local_train")
        i = (-1 + i) % len(map_main_line)
        while i != end_i:
            path2.append({
                "type": "LocalTrain",
                "file": main_line_clockwise[i],
                "departure_place": map_main_line[i][1],
                "arrival_place": map_main_line[i][0]
            })
            dis2 += dis_main_line[i]
            i = (-1 + i) % len(map_main_line)
        if self.vehicle_type_end != self.VehicleType.BRANCH:
            if map_main_line[i][1] != self.end:
                path2.append({
                    "type": "LocalTrain",
                    "file": main_line_clockwise[i],
                    "departure_place": map_main_line[i][1],
                    "arrival_place": self.end
                })
                match self.vehicle_type_end:
                    case self.VehicleType.MOUNTAIN:
                        table = "local_train_mountain"
                    case self.VehicleType.COAST:
                        table = "local_train_coast"
                    case _:
                        table = "local_train"
                dis2 += self._count_distance(map_main_line[end_i][1], self.end,
                                             main_line_clockwise[i], table)
        else:
            if map_main_line[i][2] != map_main_line[i][1]:
                path2.append({
                    "type": "LocalTrain",
                    "file": main_line_clockwise[i],
                    "departure_place": map_main_line[i][1],
                    "arrival_place": map_main_line[i][2]
                })
                dis2 += self._count_distance(map_main_line[i][1], map_main_line[i][2],
                                             main_line_clockwise[i], "local_train")
            if map_main_line[i][2] != self.end:
                path2.append({
                    "type": "LocalTrain",
                    "file": branch_line_in[i],
                    "departure_place": map_main_line[i][2],
                    "arrival_place": self.end
                })
                dis2 += self._count_distance(map_main_line[i][2], self.end,
                                             branch_line_in[i], "local_train")

        d = dis1 - dis2

        if d > 20:
            self.paths = [path2]
        elif d < -20:
            self.paths = [path1]
        else:
            self.paths = [path1, path2]



    def _create_time(self):
        if len(self.paths) == 1: #只有path1
            train1, train2, train3, train4 = self._find_best_train(self.paths[0][0]["file"], self.paths[0][0]["departure_place"], self.paths[0][0]["arrival_place"], 4)

            for i in range(3):
                l = copy.deepcopy(self.paths[0])
                self.paths.append(l)

            if len(self.paths[0]) != 1:
                self.paths[0][0].update(train1)
                self.paths[1][0].update(train2)
                self.paths[2][0].update(train3)
                self.paths[3][0].update(train4)
                for i in range(1, len(self.paths[0])):
                        train1 = self._find_best_train(self.paths[0][i]["file"], self.paths[0][i]["departure_place"], self.paths[0][i]["arrival_place"], 1, train1["arrival_time"])[0]
                        train2 = self._find_best_train(self.paths[0][i]["file"], self.paths[0][i]["departure_place"], self.paths[0][i]["arrival_place"], 1, train2["arrival_time"])[0]
                        train3 = self._find_best_train(self.paths[0][i]["file"], self.paths[0][i]["departure_place"], self.paths[0][i]["arrival_place"], 1, train3["arrival_time"])[0]
                        train4 = self._find_best_train(self.paths[0][i]["file"], self.paths[0][i]["departure_place"], self.paths[0][i]["arrival_place"], 1, train4["arrival_time"])[0]
                        self.paths[0][i].update(train1)
                        self.paths[1][i].update(train2)
                        self.paths[2][i].update(train3)
                        self.paths[3][i].update(train4)



            else:
                self.paths[0][0].update(train1)
                self.paths[1][0].update(train2)
                self.paths[2][0].update(train3)
                self.paths[3][0].update(train4)
        else: #有兩個paths
            new_paths = []

            for path in self.paths:
                # Step1. 找第一段的 4 班車
                train1, train2, train3, train4 = self._find_best_train(path[0]["file"],path[0]["departure_place"],path[0]["arrival_place"],4)

                # 建立 4 個副本
                path_copies = [copy.deepcopy(path) for _ in range(4)]

                # 填入第一段
                path_copies[0][0].update(train1)
                path_copies[1][0].update(train2)
                path_copies[2][0].update(train3)
                path_copies[3][0].update(train4)

                # Step2. 接續處理後面的每一段
                for i in range(1, len(path)):
                    train1 = self._find_best_train(path_copies[0][i]["file"], path_copies[0][i]["departure_place"], path_copies[0][i]["arrival_place"], 1, path_copies[0][i - 1]["arrival_time"])[0]
                    train2 = self._find_best_train(path_copies[1][i]["file"], path_copies[1][i]["departure_place"], path_copies[1][i]["arrival_place"], 1, path_copies[1][i - 1]["arrival_time"])[0]
                    train3 = self._find_best_train(path_copies[2][i]["file"], path_copies[2][i]["departure_place"], path_copies[2][i]["arrival_place"], 1, path_copies[2][i - 1]["arrival_time"])[0]
                    train4 = self._find_best_train(path_copies[3][i]["file"], path_copies[3][i]["departure_place"], path_copies[3][i]["arrival_place"], 1, path_copies[3][i - 1]["arrival_time"])[0]

                    path_copies[0][i].update(train1)
                    path_copies[1][i].update(train2)
                    path_copies[2][i].update(train3)
                    path_copies[3][i].update(train4)

            # 最後重新設定 paths
            self.paths = new_paths

        # 刪除不完整的路線
        for i in range(len(self.paths) - 1, -1, -1):
            for j in range(len(self.paths[i])):
                if self.paths[i][j]["transportation_name"] is None:
                    self.paths.pop(i)
                    break





    def _find_best_train(self, db_file, departure_station, arrival_station, number_of_trains = 1, min_departure_time=None):

        date_part, time_part = self.departure_time.split(' ')
        if min_departure_time is not None:
            min_departure_time_datatime = datetime.strptime(min_departure_time, '%Y-%m-%d %H:%M').strftime('%H:%M')
        else:
            min_departure_time_datatime = time_part

        weekday = datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M").weekday() + 1

        conn = get_db_connection(self.data_path + db_file)
        cursor = conn.cursor()

        fast_trains = []
        count_train = 0

        try:
            if db_file in ["西區間(新竹→彰化).db", "西區間(彰化→新竹).db"]:
                all_rows = []

                # 山海線都查
                for table_set in [("available_day_coast", "local_train_coast"),
                                  ("available_day_mountain", "local_train_mountain")]:
                    available_day_table, local_train_table = table_set

                    # 確認出發地與到達地是否都在表格內
                    cursor.execute(f"""
                        SELECT COUNT(*)
                        FROM {local_train_table}
                        WHERE 車站 IN (?, ?)
                    """, (departure_station, arrival_station))
                    count = cursor.fetchone()[0]

                    if count == 2:
                        # 兩個站都有，才能查 available_day
                        cursor.execute(f"PRAGMA table_info({available_day_table})")
                        columns = [col[1] for col in cursor.fetchall() if col[1] != "行駛日"]


                        cursor.execute(f"SELECT * FROM {available_day_table} WHERE 行駛日 = {weekday}")
                        row = cursor.fetchone()
                        if not row:
                            continue

                        available_trains = [columns[i] for i, val in enumerate(row[1:]) if val == 'T']
                        if not available_trains:
                            continue

                        valid_trains_sql = ', '.join([f'"{t}"' for t in available_trains])

                        cursor.execute(f"""
                            SELECT 車站, {valid_trains_sql}
                            FROM {local_train_table}
                            WHERE 車站 IN (?, ?)
                            ORDER BY rowid
                        """, (departure_station, arrival_station))
                        rows = cursor.fetchall()
                        if rows:
                            all_rows.append((rows, available_trains))

            else:
                # 不是山海線的路線，查原本的 available_day + local_train
                cursor.execute("PRAGMA table_info(available_day)")
                columns = [col[1] for col in cursor.fetchall() if col[1] != "行駛日"]

                cursor.execute(f"SELECT * FROM available_day WHERE 行駛日 = {weekday}")
                row = cursor.fetchone()
                if not row:
                    raise TransportationError("找不到 available_day 資料")

                available_trains = [columns[i] for i, val in enumerate(row[1:]) if val == 'T']
                valid_trains_sql = ', '.join([f'"{t}"' for t in available_trains])

                cursor.execute(f"""
                    SELECT 車站, {valid_trains_sql}
                    FROM local_train
                    WHERE 車站 IN (?, ?)
                    ORDER BY rowid
                """, (departure_station, arrival_station))
                rows = cursor.fetchall()
                all_rows = [(rows, available_trains)]

        finally:
            cursor.close()
            conn.close()

        # 處理查到的全部 rows
        self_departure_dt = datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M")

        for rows, available_trains in all_rows:
            station_times = {}
            for row in rows:
                station_name = row[0]
                station_times[station_name] = row[1:]


            if departure_station in station_times and arrival_station in station_times:
                start_times = station_times[departure_station]
                end_times = station_times[arrival_station]



                for i, train_no in enumerate(available_trains):
                    start_time = start_times[i]
                    end_time_val = end_times[i]

                    if start_time and start_time.strip() not in ('↓', '-') and end_time_val and end_time_val.strip() not in ('↓', '-'):
                        train_departure_dt = datetime.strptime(start_time, "%H:%M")
                        if train_departure_dt.time() >= self_departure_dt.time() and start_time > min_departure_time_datatime:
                            format_departure_time = datetime.combine(self_departure_dt.date(),
                                                                     train_departure_dt.time())
                            if end_time_val and end_time_val.strip() != '':
                                train_arrival_dt = datetime.strptime(end_time_val, "%H:%M")
                            else:
                                continue  # 沒有到達時間，就跳過這班
                            format_arrival_time = datetime.combine(self_departure_dt.date(), train_arrival_dt.time())

                            if train_arrival_dt.strftime("%H") == "00":
                                format_arrival_time += timedelta(days=1)

                            fast_trains.append({
                                "transportation_name": train_no,
                                "departure_time": format_departure_time.strftime("%Y-%m-%d %H:%M"),
                                "arrival_time": format_arrival_time.strftime("%Y-%m-%d %H:%M"),
                            })

        # 排序
        fast_trains = sorted(fast_trains, key=lambda x: datetime.strptime(x["arrival_time"], "%Y-%m-%d %H:%M"))

        # 補齊
        if len(fast_trains) < number_of_trains:
            while len(fast_trains) < number_of_trains:
                fast_trains.append({
                    "transportation_name": None,
                    "departure_time": None,
                    "arrival_time": None,
                })

        return fast_trains[:number_of_trains]





    def _create_cost(self):
        for path_i in range(len(self.paths)):
            for route_i in range(len(self.paths[path_i])):
                route = self.paths[path_i][route_i]

                conn = get_db_connection(self.data_path + route["file"])
                cursor = conn.cursor()
                try:
                    if route["file"] not in self.file1.values():
                        cursor.execute("""
                                        SELECT 
                                            (SELECT 距離 FROM local_train WHERE 車站 = ?) AS 出發距離,
                                            (SELECT 距離 FROM local_train WHERE 車站 = ?) AS 到達距離
                                        """,
                                       (route["departure_place"], route["arrival_place"]))
                        departure_distance, arrival_distance = cursor.fetchone()
                    else:
                        cursor.execute("""
                                        SELECT 
                                            (SELECT 距離 FROM local_train_coast WHERE 車站 = ?) AS 出發距離,
                                            (SELECT 距離 FROM local_train_coast WHERE 車站 = ?) AS 到達距離
                                        """,
                                       (route["departure_place"], route["arrival_place"]))
                        departure_distance, arrival_distance = cursor.fetchone()
                        if not departure_distance or not arrival_distance:
                            cursor.execute("""
                                            SELECT 
                                                (SELECT 距離 FROM local_train_mountain WHERE 車站 = ?) AS 出發距離,
                                                (SELECT 距離 FROM local_train_mountain WHERE 車站 = ?) AS 到達距離
                                            """,
                                           (route["departure_place"], route["arrival_place"]))
                            departure_distance, arrival_distance = cursor.fetchone()

                finally:
                    cursor.close()
                    conn.close()
                distance = max(float(arrival_distance) - float(departure_distance), 10)
                # print(route["departure_place"], route["arrival_place"], distance, departure_distance, arrival_distance, route["file"])
                transportation_name = route["transportation_name"]
                cost = 0
                for name, rate in (("區間", 1.06), ("自強", 2.27)):
                    if name in transportation_name:
                        cost = rate * distance
                        break
                if cost == 0:
                    raise TransportationError(f"transportation {transportation_name} not in 區間")

                route.update({"cost": round(cost)})


    def _find_file(self, station1):
        import os

        file = None
        vehicle_type = None

        for file_name in os.listdir(self.data_path):
            conn = get_db_connection(self.data_path + file_name)
            cursor = conn.cursor()
            try:
                if file_name not in self.file1.values():
                    cursor.execute("SELECT 車站 FROM local_train WHERE 車站 IN (?)", (station1,))
                    #cursor.execute(f"SELECT 車站 FROM local_train WHERE 車站 IN ({station1})")
                    from itertools import chain

                    branch_files = chain(self.file0_5.values(), self.file2_5.values(), self.file3_5.values(), self.file8_5.values())
                    if file_name in branch_files:
                        vehicle_type = self.VehicleType.BRANCH
                    else:
                        vehicle_type = self.VehicleType.MAIN
                    result = cursor.fetchone()
                else:
                    cursor.execute("SELECT 車站 FROM local_train_coast WHERE 車站 IN (?)", (station1,))

                    #cursor.execute(f"SELECT 車站 FROM local_train_coast WHERE 車站 IN ({station1})")
                    vehicle_type = self.VehicleType.COAST
                    result = cursor.fetchall()
                    if not result:
                        cursor.execute("SELECT 車站 FROM local_train_mountain WHERE 車站 IN (?)", (station1,))

                        #cursor.execute(f"SELECT 車站 FROM local_train_mountain WHERE 車站 IN ({station1})")
                        vehicle_type = self.VehicleType.MOUNTAIN
                        result = cursor.fetchone()
            finally:
                cursor.close()
                conn.close()
            if result:
                file = file_name
                break
            else:
                vehicle_type = None
        return file, vehicle_type

    def _is_counter_clockwise(self, file):
        counter_clockwise_files = (self.file0["to"], self.file1["to"], self.file2["to"], self.file3["to"],
                                   self.file4["to"], self.file5["to"], self.file6["to"], self.file7["to"],
                                   self.file8["to"])
        return file in counter_clockwise_files

    def _is_in(self, file):
        in_files = (self.file0_5["to"], self.file2_5["to"], self.file3_5["to"], self.file8_5["to"])
        return file in in_files

    def _count_distance(self, place1, place2, file, table):
        # print(f"place1: {place1}, place2: {place2}, file: {file}")
        conn = get_db_connection(self.data_path + file)
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                             SELECT 
                                (SELECT 距離 FROM {table} WHERE 車站 = ?) AS 出發距離,
                                (SELECT 距離 FROM {table} WHERE 車站 = ?) AS 到達距離

                            """, (place1, place2))
            distance1, distance2 = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        return float(distance2) - float(distance1)

    def _reverse_file(self, file):
        counter_clockwise_files = (self.file0["to"], self.file1["to"], self.file2["to"], self.file3["to"],
                                   self.file4["to"], self.file5["to"], self.file6["to"], self.file7["to"],
                                   self.file8["to"])
        clockwise_files = (self.file0["from"], self.file1["from"], self.file2["from"], self.file3["from"],
                           self.file4["from"], self.file5["from"], self.file6["from"], self.file7["from"],
                           self.file8["from"])
        in_files = (self.file0_5["to"], self.file2_5["to"], self.file3_5["to"], self.file8_5["to"])
        out_files = (self.file0_5["from"], self.file2_5["from"], self.file3_5["from"], self.file8_5["from"])

        index = next((i for i, x in enumerate(counter_clockwise_files) if x == file), None)
        if index is not None:
            return clockwise_files[index]

        index = next((i for i, x in enumerate(clockwise_files) if x == file), None)
        if index is not None:
            return counter_clockwise_files[index]

        index = next((i for i, x in enumerate(in_files) if x == file), None)
        if index is not None:
            return out_files[index]

        index = next((i for i, x in enumerate(out_files) if x == file), None)
        if index is not None:
            return in_files[index]

        raise FileNotFoundError(file)


if __name__ == "__main__":
    import json
    t = LocalTrain("2025-04-09 06:30", "臺中", "新埔")
    t.create()
    print(json.dumps(t.paths, indent=2))