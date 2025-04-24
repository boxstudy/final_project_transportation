from bus import Bus
from bus_X_express_train import Bus_X_ExpressTrain
from bus_X_express_train_X_high_speed_rail import Bus_X_ExpressTrain_X_HighSpeedRail
from high_speed_rail_X_express_train import HighSpeedRail_X_ExpressTrain
from express_train import ExpressTrain
from high_speed_rail import HighSpeedRail


class TransportationPath:
    def __init__(self):
        pass

    def _remove_file_from_paths(self, paths):
        for i in range(len(paths)):
            for j in range(len(paths[i])):
                paths[i][j].pop('file', None)

    def _simplify_paths(self, paths):
        from datetime import datetime, timedelta
        for path in paths:
            j = len(path) - 1
            while j > 0:
                if (path[j - 1]["type"] == path[j]["type"] and
                        path[j - 1]["transportation_name"] == path[j]["transportation_name"] and
                        datetime.strptime(path[j - 1]["arrive_time"], "%Y-%m-%d %H:%M") + timedelta(minutes=10) <
                        datetime.strptime(path[j]["departure_time"], "%Y-%m-%d %H:%M")):
                    path[j - 1]["arrive_time"] = path[j]["arrive_time"]
                    path[j - 1]["arrive_place"] = path[j]["arrive_place"]
                    path[j - 1]["cost"] += path[j]["cost"]
                    path.pop(j)
                j -= 1
    def get_division(self, start_date: str, departure_place: str, arrive_place: str, mask: int,
                     high_speed_rail_discount: bool, high_speed_rail_reserved: bool):
        '''
        :param start_date: 起始日期
        :param departure_place: 出發地點
        :param arrive_place: 抵達地點
        :return: { int(類別1): [路線1, 路線2, 路線3,...], int(類別2): [路線1, 路線2, 路線3,...],... }
                 int(類別): 由後方對應數字按位與決定使用哪些交通方式， 0x1 -> high_speed_rail, 0x2 -> express_train, 0x4 -> bus
        '''

        class Type:
            high_speed_rail = 0x1
            express_train = 0x2
            bus = 0x4

        paths = {}

        if mask & Type.high_speed_rail:
            print("High Speed Rail:")
            high_speed_rail = HighSpeedRail(departure_time=start_date, start=departure_place, end=arrive_place,
                                            discount=high_speed_rail_discount, reserved=high_speed_rail_reserved)
            high_speed_rail_paths = high_speed_rail.create()
            self._simplify_paths(high_speed_rail_paths)
            self._remove_file_from_paths(high_speed_rail_paths)
            paths.update({Type.high_speed_rail: high_speed_rail_paths})

        if mask & Type.express_train:
            print("Express Train:")
            express_train = ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place)
            express_train_paths = express_train.create()
            self._simplify_paths(express_train_paths)
            self._remove_file_from_paths(express_train_paths)
            paths.update({Type.express_train: express_train_paths})

        if mask & Type.bus:
            print("Bus:")
            bus = Bus(departure_time=start_date, start=departure_place, end=arrive_place)
            bus_paths = bus.create()
            self._simplify_paths(bus_paths)
            self._remove_file_from_paths(bus_paths)
            paths.update({Type.bus: bus_paths})

        if mask & (Type.high_speed_rail | Type.express_train):
            print("High Speed Rail X Express Train:")
            high_speed_rail_express_train = HighSpeedRail_X_ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place,
                                                                         discount=high_speed_rail_discount, reserved=high_speed_rail_reserved)
            high_speed_rail_x_express_train_paths = high_speed_rail_express_train.create()
            self._simplify_paths(high_speed_rail_x_express_train_paths)
            self._remove_file_from_paths(high_speed_rail_x_express_train_paths)
            paths.update({Type.high_speed_rail | Type.express_train: high_speed_rail_x_express_train_paths})

        if mask & (Type.bus | Type.express_train):
            print("Bus X Express Train:")
            bus_x_express_train = Bus_X_ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place)
            bus_x_express_train_paths = bus_x_express_train.create()
            self._simplify_paths(bus_x_express_train_paths)
            self._remove_file_from_paths(bus_x_express_train_paths)
            paths.update({Type.bus | Type.express_train: bus_x_express_train_paths})

        if mask & (Type.bus | Type.express_train | Type.high_speed_rail):
            print("Bus X Express Train X High Speed Rail:")
            bus_x_express_train_x_high_speed_rail = Bus_X_ExpressTrain_X_HighSpeedRail(departure_time=start_date, start=departure_place, end=arrive_place,
                                                                                       discount=high_speed_rail_discount, reserved=high_speed_rail_reserved)
            bus_x_express_train_x_high_speed_rail_paths = bus_x_express_train_x_high_speed_rail.create()
            self._simplify_paths(bus_x_express_train_x_high_speed_rail_paths)
            self._remove_file_from_paths(bus_x_express_train_x_high_speed_rail_paths)
            paths.update({Type.bus | Type.express_train | Type.high_speed_rail: bus_x_express_train_x_high_speed_rail_paths})

        return paths

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
        Bus_X_ExpressTrain_X_HighSpeedRail_paths = Bus_X_ExpressTrain_X_HighSpeedRail(departure_time=start_date, start=departure_place, end=arrive_place,
                                                                                       discount=False, reserved=True).create()
        paths.extend(Bus_X_ExpressTrain_X_HighSpeedRail_paths)


        self._simplify_paths(paths)
        self._remove_file_from_paths(paths)

        return paths