from local_train_X_express_train import LocalTrain_X_ExpressTrain
from bus import Bus
from transportation import ComplexTransport

class LocalTrain_X_Bus_X_ExpressTrain(ComplexTransport):
    ComplexTransport.stations = LocalTrain_X_ExpressTrain.stations | Bus.stations
    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end)
        self.bus = Bus("", "", "")
        self.local_train_X_express_train = LocalTrain_X_ExpressTrain("", "", "")

    def _create(self):

        Bus_transfer_points = ["花蓮"]
        LocalTrain_X_ExpressTrain_transfer_points = ["花蓮"]

        self.paths = super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                        departure_place=self.start,
                                                        arrival_place=self.end,
                                                        transportation_a=self.bus,
                                                        transportation_b=self.local_train_X_express_train,
                                                        transfer_points_a=Bus_transfer_points,
                                                        transfer_points_b=LocalTrain_X_ExpressTrain_transfer_points)