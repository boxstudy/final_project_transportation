import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime

def get_db_connection(data_path):
    conn = sqlite3.connect(data_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_spend_path_minutes(path):
    departure_time = datetime.strptime(path[0]["departure_time"], '%Y-%m-%d %H:%M')
    arrive_time = datetime.strptime(path[-1]["arrival_time"], '%Y-%m-%d %H:%M')
    spend_time = arrive_time - departure_time
    return spend_time.total_seconds() / 60

class Transportation(ABC):
    def __init__(self, departure_time: str, start: str, end: str, folder: str):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        self.data_path = r"../data/" + folder
        self.paths = []

    def reinit(self, departure_time: str, start: str, end: str):
        self.departure_time = departure_time
        self.start = start
        self.end = end
        return self

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
            self._create_path()
            self._create_time()
            self._create_cost()
        except Exception as e:
            self.paths = []
            print(e)
        return self.paths

class ComplexTransport:
    def __init__(self):
        self.paths = []

    @abstractmethod
    def create(self):
        pass

    @staticmethod
    def _replace_part_of_path(transportation_src: Transportation,
                              transportation_inner: Transportation,
                              src_transfer_points: list,
                              inner_transfer_points: list,
                              condition_src_files,
                              order_table_col):
        res_paths = []

        sql_transfer_points = "','".join(src_transfer_points)

        # 找到有覆蓋dst線路的src，選src最快的幾台
        tmp_express_train_paths = sorted(transportation_src.paths, key=get_spend_path_minutes)
        select_num = 2  # 最多選幾班車

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
            return res_paths

        for i in range(len(select_paths)):
            for j in range(len(select_paths[i])):
                part = select_paths[i][j]
                if part['file'] not in condition_src_files:
                    continue
                # 先獲取兩班車與transfer_points，會落在哪個位置，
                conn = get_db_connection(transportation_src.data_path + part['file'])
                cursor = conn.cursor()
                try:
                    table, col = order_table_col
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

                # 如果都在 "板橋" 往北，"新左營" 往南，則不考慮，
                if record[1] is part['departure_place'] or record[-2] is part['arrival_place']:
                    continue

                # ! 如果獲取兩班車中包含兩或以上transfer_point則考慮換車，
                departure_i = record.index(part['departure_place'])
                arrival_i = record.index(part['arrival_place'])

                trans = []
                if departure_i == 0:
                    trans = [1]
                else:
                    if departure_i + 1 != arrival_i:
                        trans = [departure_i - 1, departure_i + 1]
                    else:
                        trans = [departure_i - 1]
                if arrival_i is len(record) - 1:
                    trans = [(i, arrival_i - 1) for i in trans]
                else:
                    if arrival_i - 1 != departure_i:
                        trans = [(i, arrival_i - 1) for i in trans] + [(i, arrival_i + 1) for i in trans]
                    else:
                        trans = [(i, departure_i + 1) for i in trans]

                orig_spend_time = get_spend_path_minutes(select_paths[i][j:])

                flag = False
                for m, n in trans:
                    list1 = transportation_src.reinit(departure_time=part['departure_time'],
                                         start=part['departure_place'],
                                         end=record[m]).create()
                    list1 = min(list1, key=get_spend_path_minutes)

                    # print("m, n", m, n)
                    # print("record", record)

                    list2 = transportation_inner.reinit(departure_time=list1[-1]['arrival_time'],
                                                        start=inner_transfer_points[src_transfer_points.index(record[m])],
                                                        end=inner_transfer_points[src_transfer_points.index(record[n])]).create()
                    list2 = min(list2, key=get_spend_path_minutes)

                    list3 = transportation_src.reinit(departure_time=list2[-1]['arrival_time'], start=record[n],
                                         end=select_paths[i][-1]['arrival_place']).create()
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