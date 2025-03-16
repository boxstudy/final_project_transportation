import express_train
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
            paths.append(express_train_paths)



            HighSpadeRail_ExpressTrain_transfer_points = ["板橋", "台北", "新烏日", "新左營"]
            for express_train_path in express_train_paths:
                for part in express_train_path:
                    if part['file'] == express_train.Caozhou_Jilong.values():
                        # 先獲取兩班車與transfer_points，會落在哪個位置，
                        # 如果都在 "板橋" 往北，"新左營" 往南，則不考慮，
                        # ! 如果獲取兩班車中包含兩或以上transfer_point則考慮換車，
                        pass



        for i in range(len(paths)):
            for j in range(len(paths[i])):
                del paths[i][j]['file']

        return paths