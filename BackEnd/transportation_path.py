from bus import Bus
from bus_X_express_train import Bus_X_ExpressTrain
from bus_X_express_train_X_high_speed_rail import Bus_X_ExpressTrain_X_HighSpeedRail
from high_speed_rail_X_express_train import HighSpeedRail_X_ExpressTrain
from express_train import ExpressTrain
from high_speed_rail import HighSpeedRail


class TransportationPath:
    def __init__(self):
        pass

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
            paths.update({Type.high_speed_rail: high_speed_rail_paths})

        if mask & Type.express_train:
            print("Express Train:")
            express_train = ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place)
            express_train_paths = express_train.create()
            paths.update({Type.express_train: express_train_paths})

        if mask & Type.bus:
            print("Bus:")
            bus = Bus(departure_time=start_date, start=departure_place, end=arrive_place)
            bus_paths = bus.create()
            paths.update({Type.bus: bus_paths})

        if mask & (Type.high_speed_rail | Type.express_train):
            print("High Speed Rail X Express Train:")
            high_speed_rail_express_train = HighSpeedRail_X_ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place,
                                                                         discount=high_speed_rail_discount, reserved=high_speed_rail_reserved)
            high_speed_rail_x_express_train_paths = high_speed_rail_express_train.create()
            paths.update({Type.high_speed_rail | Type.express_train: high_speed_rail_x_express_train_paths})

        if mask & (Type.bus | Type.express_train):
            print("Bus X Express Train:")
            bus_x_express_train = Bus_X_ExpressTrain(departure_time=start_date, start=departure_place, end=arrive_place)
            bus_x_express_train_paths = bus_x_express_train.create()
            paths.update({Type.bus | Type.express_train: bus_x_express_train_paths})

        if mask & (Type.bus | Type.express_train | Type.high_speed_rail):
            print("Bus X Express Train X High Speed Rail:")
            bus_x_express_train_x_high_speed_rail = Bus_X_ExpressTrain_X_HighSpeedRail(departure_time=start_date, start=departure_place, end=arrive_place,
                                                                                       discount=high_speed_rail_discount, reserved=high_speed_rail_reserved)
            bus_x_express_train_x_high_speed_rail_paths = bus_x_express_train_x_high_speed_rail.create()
            paths.update({Type.bus | Type.express_train | Type.high_speed_rail: bus_x_express_train_x_high_speed_rail_paths})

        for i in range(len(paths)):
            for j in range(len(paths[i])):
                paths[i][j].pop('file', None)

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

        for i in range(len(paths)):
            for j in range(len(paths[i])):
                paths[i][j].pop('file', None)

        return paths