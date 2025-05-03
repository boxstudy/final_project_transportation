from bus import Bus
from express_train import ExpressTrain
from transportation import ComplexTransport


class Bus_X_ExpressTrain(ComplexTransport):
    stations = ExpressTrain.stations | Bus.stations

    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end, self.stations)
        self.bus = Bus("", "", "")
        self.express_train = ExpressTrain("", "", "")

    def _create(self):
        Bus_transfer_points = ["花蓮"]
        ExpressTrain_transfer_points = ["花蓮"]

        self.paths = super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                        departure_place=self.start,
                                                        arrival_place=self.end,
                                                        transportation_a=self.bus,
                                                        transportation_b=self.express_train,
                                                        transfer_points_a=Bus_transfer_points,
                                                        transfer_points_b=ExpressTrain_transfer_points)


if __name__ == "__main__":
    print(Bus_X_ExpressTrain("2022-03-15 10:00", "東華大學", "基隆").create())