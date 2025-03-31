from bus import Bus
from bus_X_express_train import Bus_X_ExpressTrain
from bus_X_express_train_X_high_speed_rail import Bus_X_ExpressTrain_X_HighSpeedRail
from high_speed_rail_X_express_train import HighSpeedRail_X_ExpressTrain
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

        print("1.High Speed Rail:")
        high_speed_rail = HighSpeedRail(departure_time=start_date, start=departure_place, end=arrive_place, discount=False, reserved=True)
        high_speed_rail_paths = high_speed_rail.create()
        paths.extend(high_speed_rail_paths)

        print("2.Express Train:")
        express_train = ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place)
        express_train_paths = express_train.create()
        paths.extend(express_train_paths)

        print("3.Bus:")
        bus = Bus(departure_time=start_date, start=departure_place, end=arrive_place)
        bus_paths = bus.create()
        paths.extend(bus_paths)

        print("4.High Speed Rail X Express Train:")
        HighSpeedRail_X_ExpressTrain_paths = HighSpeedRail_X_ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place, discount=False, reserved=True).create()
        paths.extend(HighSpeedRail_X_ExpressTrain_paths)

        print("5.Bus X Express Train:")
        Bus_X_ExpressTrain_paths = Bus_X_ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place).create()
        paths.extend(Bus_X_ExpressTrain_paths)

        print("6.Bus X Express Train X High Speed Rail:")
        Bus_X_ExpressTrain_X_HighSpeedRail_paths = Bus_X_ExpressTrain_X_HighSpeedRail(departure_time=start_date, start=departure_place, end=arrive_place).create()
        paths.extend(Bus_X_ExpressTrain_X_HighSpeedRail_paths)

        for i in range(len(paths)):
            for j in range(len(paths[i])):
                paths[i][j].pop('file', None)

        return paths