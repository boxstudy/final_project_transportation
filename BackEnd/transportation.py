import sqlite3
import sys
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union
import statistics

DATA_PATH = r"../data/"

def get_db_connection(data_path):
    conn = sqlite3.connect(data_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_spend_path_minutes(path):
    departure_time = datetime.strptime(path[0]["departure_time"], '%Y-%m-%d %H:%M')
    arrive_time = datetime.strptime(path[-1]["arrival_time"], '%Y-%m-%d %H:%M')
    spend_time = arrive_time - departure_time
    return spend_time.total_seconds() / 60

class TransportationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Transportation(ABC):

    def __init__(self, departure_time: str, start: str, end: str, stations: set):
        self.stations = stations
        self._reset(departure_time, start, end)

    def reinit(self, departure_time: str, start: str, end: str):
        self._reset(departure_time, start, end)
        return self

    def _reset(self, departure_time: str, start: str, end: str):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        self.paths = []

    @abstractmethod
    def _create_path(self):
        pass

    @abstractmethod
    def _create_time(self):
        pass

    @abstractmethod
    def _create_cost(self):
        pass

    def create(self):
        try:
            if self.start == self.end:
                return self.paths
            if self.start not in self.stations:
                raise TransportationError(f"Invalid start {self.start}")
            if self.end not in self.stations:
                raise TransportationError(f"Invalid end {self.end}")
            self._create_path()
            self._create_time()
            self._create_cost()
        except TransportationError as e:
            self.paths = []
            print(e)
        except Exception as e:
            self.paths = []
            print(e, file=sys.stderr)
            traceback.print_exc()
        return self.paths



class ComplexTransport(ABC):

    def __init__(self, departure_time: str, start: str, end: str, stations: set):
        self.stations = stations
        self._reset(departure_time, start, end)

    def reinit(self, departure_time: str, start: str, end: str):
        self._reset(departure_time, start, end)
        return self

    def _reset(self, departure_time: str, start: str, end: str):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        self.paths = []

    @abstractmethod
    def _create(self):
        pass

    def create(self):
        try:
            if self.start == self.end:
                return self.paths
            if self.start not in self.stations:
                raise TransportationError(f"Invalid start {self.start}")
            if self.end not in self.stations:
                raise TransportationError(f"Invalid end {self.end}")
            self._create()
        except TransportationError as e:
            self.paths = []
            print(e)
        except Exception as e:
            self.paths = []
            print(e, file=sys.stderr)
            traceback.print_exc()
        return self.paths

    @staticmethod
    def _replace_part_of_path(transportation_src: Union[Transportation, "ComplexTransport"],
                              transportation_inner: Union[Transportation, "ComplexTransport"],
                              src_transfer_points: list,
                              inner_transfer_points: list,
                              condition_src_files,
                              order_path_table_col):
        if transportation_src.start in transportation_inner.stations and transportation_src.start in transportation_inner.stations:
            return []
        select_num = 3  # 最多選幾班車

        if not transportation_src.paths:
            return []

        sql_transfer_points = "','".join(src_transfer_points)

        # 找到有覆蓋dst線路的src，選src最快的幾台
        tmp_express_train_paths = sorted(transportation_src.paths, key=get_spend_path_minutes)


        select_paths = []
        for path in tmp_express_train_paths:
            for j in range(len(path)):
                if path[j]['file'] in condition_src_files:
                    select_paths.append(path)
                    select_num -= 1
                    if select_num == 0:
                        break
            if select_num == 0:
                break

        if not select_paths:
            return []

        res_paths = []
        for i in range(len(select_paths)):
            for j in range(len(select_paths[i])):

                part = select_paths[i][j]
                if part['file'] not in condition_src_files:
                    continue
                # 先獲取兩班車與transfer_points，會落在哪個位置，
                data_path, table, col = order_path_table_col
                conn = get_db_connection(data_path + part['file'])
                cursor = conn.cursor()
                try:
                    cursor.execute(f"""SELECT {col} FROM {table}
                                        WHERE {col} IN ('{sql_transfer_points}', 
                                                      '{part['departure_place']}',
                                                      '{part['arrival_place']}')
                                        ORDER BY rowid;""")
                    record = [trans[0] for trans in cursor.fetchall()]
                finally:
                    cursor.close()
                    conn.close()

                if len(record) < 3:
                    continue

                if record[1] == part['arrival_place'] or record[-2] == part['departure_place']:
                    continue

                if len(record) + 2 == len(src_transfer_points) and len(select_paths[i]) == 1:
                    continue

                # ! 如果獲取兩班車中包含兩或以上transfer_point則考慮換車，
                departure_i = record.index(part['departure_place'])
                arrival_i = record.index(part['arrival_place'])


                if departure_i == 0:
                    trans = [1]
                elif record[departure_i] in src_transfer_points:
                    trans = [departure_i]
                elif departure_i + 1 != arrival_i:
                    trans = [departure_i - 1, departure_i + 1]
                else:
                    trans = [departure_i - 1]

                if arrival_i == len(record) - 1:
                    trans = [(i, arrival_i - 1) for i in trans]
                elif record[arrival_i] in src_transfer_points:
                    trans = [(i, arrival_i) for i in trans]
                elif arrival_i - 1 != departure_i:
                    trans = [(i, arrival_i - 1) for i in trans] + [(i, arrival_i + 1) for i in trans]
                else:
                    trans = [(i, arrival_i + 1) for i in trans]

                orig_spend_time = get_spend_path_minutes(select_paths[i][j:])

                flag = False
                for m, n in trans:
                    if m == n:
                        continue

                    list1 = transportation_src.reinit(departure_time=part['departure_time'],
                                                      start=part['departure_place'],
                                                      end=record[m]).create()
                    if not list1:
                        continue
                    if part['departure_place'] != record[m]:
                        list1 = min(list1, key=get_spend_path_minutes)

                    list2 = transportation_inner.reinit(departure_time=list1[-1]['arrival_time'],
                                                        start=inner_transfer_points[src_transfer_points.index(record[m])],
                                                        end=inner_transfer_points[src_transfer_points.index(record[n])]).create()
                    if not list2:
                        continue
                    list2 = min(list2, key=get_spend_path_minutes)

                    list3 = transportation_src.reinit(departure_time=list2[-1]['arrival_time'],
                                                      start=record[n],
                                                      end=select_paths[i][-1]['arrival_place']).create()
                    if not list3:
                        continue
                    if record[n] != select_paths[i][-1]['arrival_place']:
                        list3 = min(list3, key=get_spend_path_minutes)

                    combined_list = list1 + list2 + list3
                    if combined_list and get_spend_path_minutes(combined_list) < orig_spend_time:
                        l = select_paths[i][:j] + combined_list
                        if l not in res_paths:
                            res_paths.append(l)
                        flag = True
                if flag:
                    break

        return res_paths

    @staticmethod
    def _switch_by_transfer_points(departure_time, departure_place, arrival_place,
                                   transportation_a: "Transportation | ComplexTransport",
                                   transportation_b: "Transportation | ComplexTransport",
                                   transfer_points_a: list,
                                   transfer_points_b: list
                                   ):
        paths = []

        def t1_to_t2(t1, t2, t1_transfer_points, t2_transfer_points):
            import sys
            cost_time = sys.maxsize
            transfer_point_i = 0
            best_paths = None
            for i in range(len(transfer_points_a)):
                t1_paths = t1.reinit(departure_time=departure_time,
                                     start=departure_place,
                                     end=t1_transfer_points[i]).create()
                if not t1_paths:
                    continue
                t1_path = min(t1_paths, key=get_spend_path_minutes)

                t2_paths = t2.reinit(departure_time=t1_path[-1]['arrival_time'],
                                     start=t2_transfer_points[i],
                                     end=arrival_place).create()
                if not t2_paths:
                    continue
                t2_path = min(t2_paths, key=get_spend_path_minutes)

                cost_time_tmp = get_spend_path_minutes(t1_path + t2_path)
                if cost_time_tmp < cost_time:
                    cost_time = cost_time_tmp
                    transfer_point_i = i
                    best_paths = t1_paths

            if not best_paths:
                return

            transfer_point_b = transfer_points_b[transfer_point_i]
            for path in best_paths:
                transportation2_paths = t2.reinit(path[-1]["arrival_time"], transfer_point_b, arrival_place).create()
                if transportation2_paths:
                    paths.append(path + min(transportation2_paths, key=lambda x: x[-1]["arrival_time"]))
                else:
                    break

        if departure_place in transportation_a.stations and arrival_place in transportation_b.stations:
            t1_to_t2(transportation_a, transportation_b, transfer_points_a, transfer_points_b)

        if departure_place in transportation_b.stations and arrival_place in transportation_a.stations:
            t1_to_t2(transportation_b, transportation_a, transfer_points_b, transfer_points_a)

        return paths

    @staticmethod
    def _insert_transportation(departure_time, departure_place, arrival_place,
                               transportation_src: "Transportation | ComplexTransport",
                               transportation_inner: "Transportation | ComplexTransport",
                               transfer_points_src: list,
                               transfer_points_inner: list
                               ):
        if departure_place in transportation_inner.stations and arrival_place in transportation_inner.stations:
            return []
        paths_record1 = []
        for i, point_src in enumerate(transfer_points_src):
            transportation_src = transportation_src.reinit(departure_time=departure_time,
                                                           start=departure_place,
                                                           end=point_src)
            if transportation_src.create():
                paths_record1.append((i, transportation_src.paths))
            else:
                break

        paths_record2 = []
        for i, point_inner in enumerate(transfer_points_inner):
            transportation_inner = transportation_inner.reinit(departure_time=departure_time,
                                                               start=point_inner,
                                                               end=arrival_place)
            if transportation_inner.create():
                paths_record2.append((i, transportation_inner.paths))
            else:
                break

        if not paths_record2:
            return []

        min_record = min(paths_record1, key=lambda x: statistics.mean(get_spend_path_minutes(item) for item in x[1]))
        start_i, paths1 = min_record
        min_record = min(paths_record2, key=lambda x: statistics.mean(get_spend_path_minutes(item) for item in x[1]))
        end_i, _ = min_record

        if start_i == end_i:
            return []


        paths2 = []
        for path in paths1:
            transportation_inner = transportation_inner.reinit(departure_time=path[-1]["arrival_time"],
                                                               start=transfer_points_inner[start_i],
                                                               end=transfer_points_inner[end_i])
            if transportation_inner.create():
                paths2.append(path + min(transportation_inner.paths, key=lambda x: x[-1]["arrival_time"]))
            else:
                break

        paths3 = []
        for path in paths2:
            transportation_src = transportation_src.reinit(departure_time=path[-1]["arrival_time"],
                                                           start=transfer_points_src[end_i],
                                                           end=arrival_place)
            if transportation_src.create():
                paths3.append(path + min(transportation_src.paths, key=lambda x: x[-1]["arrival_time"]))
            else:
                break
        if not paths3:
            return []

        transportation_src = transportation_src.reinit(departure_time=departure_time,
                                                       start=departure_place,
                                                       end=arrival_place)
        if not transportation_src.create():
            return []

        paths = []
        path_src = min(transportation_src.paths, key=lambda x: x[-1]["arrival_time"])
        time_src = get_spend_path_minutes(path_src)
        for path in paths3:
            if time_src > get_spend_path_minutes(path):
                paths.append(path)

        return paths

