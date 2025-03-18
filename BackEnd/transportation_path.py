from transportation import get_db_connection
from express_train import ExpressTrain
from high_speed_rail import HighSpadeRail


class TransportationPath:
    def __init__(self):
        pass

    def get(self, start_date: str, from_place: str, to_place: str):
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

        high_speed_rail = HighSpadeRail(departure_time=start_date, start=from_place, end=to_place, discount=True, reserved=True)
        high_speed_rail_paths = high_speed_rail.create()
        if high_speed_rail_paths is not None:
            paths.extend(high_speed_rail_paths)

        express_train = ExpressTrain(departure_time=start_date, start=from_place, end=to_place)
        express_train_paths = express_train.create()
        if express_train_paths is not None:
            paths.extend(express_train_paths)

        ExpressTrain_X_HighSpeedRail_paths = None
        if high_speed_rail_paths and express_train_paths is not None:
            HighSpadeRail_ExpressTrain_transfer_points = ["板橋", "台北", "新烏日", "新左營"]
            sql_transfer_points = "','".join(HighSpadeRail_ExpressTrain_transfer_points)

            # 找到一台合適的台鐵
            for i in range(len(express_train_paths)):
                for j in range(len(express_train_paths[i])):
                    part = express_train_paths[i][j]
                    if part['file'] in express_train.Caozhou_Jilong.values():

                        if "莒光" in part['transportation_name']:
                            continue

                        # 先獲取兩班車與transfer_points，會落在哪個位置，
                        conn = get_db_connection(express_train.data_path + part['file'])
                        cursor = conn.cursor()
                        cursor.execute(f"""SELECT 車站 FROM train
                                                                WHERE 車站 IN ('{sql_transfer_points}', '{part['departure_place']}', '{part['arrival_place']}')
                                                                ORDER BY rowid;""")
                        record = [trans[0] for trans in cursor.fetchall()]
                        conn.close()
                        # 如果都在 "板橋" 往北，"新左營" 往南，則不考慮，
                        if record[1] is part['departure_place'] or record[-2] is part['arrival_place']:
                            break
                        # ! 如果獲取兩班車中包含兩或以上transfer_point則考慮換車，
                        departure_i = record.index(part['departure_time'])
                        arrival_i = record.index(part['arrival_place'])
                        trans = []
                        if departure_i is 0:
                            trans = [1]
                        else:
                            trans = [departure_i - 1, departure_i + 1]
                        if arrival_i is -1:
                            trans = [(i, arrival_i - 1) for i in trans]
                        else:
                            trans = [(i, arrival_i - 1) for i in trans] + [(i, arrival_i + 1) for i in trans]

                        temple_ExpressTrain_X_HighSpeedRail_path = express_train_paths[i][:j]

                        for m, n in trans:
                            list1 = ExpressTrain(departure_time=start_date, start=part['departure_time'], end=record[m])
                            list2 = HighSpadeRail(departure_time=start_date, start=record[m], end=record[n],
                                                  discount=True, reserved=True)
                            list3 = ExpressTrain(departure_time=start_date, start=record[n],
                                                 end=express_train_paths[i]['arrival_place'])

        for i in range(len(paths)):
            for j in range(len(paths[i])):
                paths[i][j].pop('file', '')

        return paths