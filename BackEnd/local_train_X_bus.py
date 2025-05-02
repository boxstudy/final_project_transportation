from local_train import LocalTrain
from bus import Bus
from transportation import ComplexTransport

class LocalTrain_X_Bus(ComplexTransport):
    stations = LocalTrain.stations | Bus.stations
    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end, self.stations)
        self.bus = Bus("", "", "")
        self.local_train = LocalTrain("", "", "")

    def _create(self):

        Bus_transfer_points = ["花蓮"]
        LocalTrain_transfer_points = ["花蓮"]

        self.paths = super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                        departure_place=self.start,
                                                        arrival_place=self.end,
                                                        transportation_a=self.bus,
                                                        transportation_b=self.local_train,
                                                        transfer_points_a=Bus_transfer_points,
                                                        transfer_points_b=LocalTrain_transfer_points)