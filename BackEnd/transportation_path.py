from transportation import get_db_connection, get_spend_path_minutes
from express_train import ExpressTrain
from high_speed_rail import HighSpeedRail


class TransportationPath:
    def __init__(self):
        pass

    def get(self, start_date: str, departure_place: str, arrive_place: str):
        # path = [
        #         # path 1
        #         [{"type": "train", "transportation_name": "Train 201", "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:00", "arrival_time": "2025/02/01-10:30", "cost": 100},
        #          {"type": "bus",   "transportation_name": "Bus 203",   "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:30", "arrival_time": "2025/02/01-11:00", "cost": 100}],
        #
        #         # path 2
        #         [{"type": "train", "transportation_name": "Train 201", "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:00", "arrival_time": "2025/02/01-10:30", "cost": 100},
        #          {"type": "bus",   "transportation_name": "Bus 203",   "departure_place":"", "arrival_place":"", "departure_time": "2025/02/01-10:30", "arrival_time": "2025/02/01-11:00", "cost": 100}],
        # ]
        paths = []

        high_speed_rail = HighSpeedRail(departure_time=start_date, start=departure_place, end=arrive_place, discount=True, reserved=True)
        high_speed_rail_paths = high_speed_rail.create()
        paths.extend(high_speed_rail_paths)

        express_train = ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place)
        express_train_paths = express_train.create()
        paths.extend(express_train_paths)

        ExpressTrain_X_HighSpeedRail_paths = []
        if express_train_paths:
            ExpressTrain_transfer_points = ["板橋", "臺北", "新烏日", "新左營"]
            HighSpadeRail_transfer_points = ["板橋", "臺北", "臺中", "左營"]
            sql_transfer_points = "','".join(ExpressTrain_transfer_points)

            # 找到有覆蓋高鐵線路的台鐵，選最快的幾台
            tmp_express_train_paths = sorted(express_train_paths, key=get_spend_path_minutes)
            select_paths = []
            select_num = 1 # 最多選幾班車
            for i in range(len(tmp_express_train_paths)):
                path = tmp_express_train_paths[i]
                for j in range(len(path)):
                    if path[j]['file'] in express_train.Caozhou_Jilong.values():
                        select_paths.append(path)
                        select_num -= 1
                        if 0 == select_num:
                            break
                if 0 == select_num:
                    break

            if len(select_paths):
                for i in range(len(select_paths)):
                    for j in range(len(select_paths[i])):
                        part = select_paths[i][j]
                        if part['file'] in express_train.Caozhou_Jilong.values():
                            # 先獲取兩班車與transfer_points，會落在哪個位置，

                            conn = get_db_connection(express_train.data_path + part['file'])
                            cursor = conn.cursor()
                            try:
                                cursor.execute(f"""SELECT 車站 FROM train
                                                    WHERE 車站 IN ('{sql_transfer_points}', 
                                                                  '{part['departure_place']}',
                                                                  '{part['arrival_place']}')
                                                    ORDER BY rowid;""")
                                record = [trans[0] for trans in cursor.fetchall()]
                            finally:
                                cursor.close()
                                conn.close()
                            # 如果都在 "板橋" 往北，"新左營" 往南，則不考慮，
                            if record[1] is part['departure_place'] or record[-2] is part['arrival_place']:
                                break
                            # ! 如果獲取兩班車中包含兩或以上transfer_point則考慮換車，
                            departure_i = record.index(part['departure_place'])
                            arrival_i = record.index(part['arrival_place'])
                            trans = [1] if departure_i == 0 else [departure_i - 1, departure_i + 1]
                            if arrival_i is len(record) - 1:
                                trans = [(i, arrival_i - 1) for i in trans]
                            else:
                                trans = [(i, arrival_i - 1) for i in trans] + [(i, arrival_i + 1) for i in trans]

                            orig_spend_time = get_spend_path_minutes(select_paths[i][j:])

                            flag = False
                            for m, n in trans:
                                list1 = ExpressTrain(departure_time=start_date, start=part['departure_place'],
                                                     end=record[m]).create()
                                list2 = HighSpeedRail(departure_time=start_date,
                                                      start=HighSpadeRail_transfer_points[ExpressTrain_transfer_points.index(record[m])],
                                                      end=HighSpadeRail_transfer_points[ExpressTrain_transfer_points.index(record[n])],
                                                      discount=True, reserved=True).create()
                                list3 = ExpressTrain(departure_time=start_date, start=record[n],
                                                     end=select_paths[i][-1]['arrival_place']).create()

                                list1 = min(list1, key=get_spend_path_minutes)
                                list2 = min(list2, key=get_spend_path_minutes)
                                list3 = min(list3, key=get_spend_path_minutes)
                                if list1 and list2 and list3:
                                    spend_time = get_spend_path_minutes(list1 + list2 + list3)
                                    if spend_time < orig_spend_time:
                                        l = select_paths[i][:j] + list1 + list2 + list3
                                        if l not in ExpressTrain_X_HighSpeedRail_paths:
                                            ExpressTrain_X_HighSpeedRail_paths.append(l)
                                        print(select_paths[i][:j])
                                        flag = True
                            if flag:
                                break
            paths.extend(ExpressTrain_X_HighSpeedRail_paths)

        for i in range(len(paths)):
            for j in range(len(paths[i])):
                paths[i][j].pop('file', '')

        return paths