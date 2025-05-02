import local_train
from local_train import LocalTrain
from high_speed_rail import HighSpeedRail
from local_train_X_express_train import LocalTrain_X_ExpressTrain
from transportation import ComplexTransport

class LocalTrain_X_HighSpeedRail(ComplexTransport):
    stations = LocalTrain.stations | HighSpeedRail.stations
    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end, self.stations)
        self.local_train = LocalTrain("", "", "")
        self.high_speed_rail = HighSpeedRail("", "", "", discount, reserved)

    def _create(self):

        LocalTrain_transfer_points = ["板橋", "臺北", "新烏日", "新左營"]
        HighSpadeRail_transfer_points = ["板橋", "臺北", "高鐵臺中", "高鐵左營"]

        self.paths += super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                     departure_place=self.start,
                                                     arrival_place=self.end,
                                                     transportation_a=self.local_train,
                                                     transportation_b=self.high_speed_rail,
                                                     transfer_points_a=LocalTrain_transfer_points,
                                                     transfer_points_b=HighSpadeRail_transfer_points)

        self.paths += super()._insert_transportation(departure_time=self.departure_time,
                                                     departure_place=self.start,
                                                     arrival_place=self.end,
                                                     transportation_src=self.local_train,
                                                     transportation_inner=self.high_speed_rail,
                                                     transfer_points_src=LocalTrain_transfer_points,
                                                     transfer_points_inner=HighSpadeRail_transfer_points)
