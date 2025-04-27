from local_train import LocalTrain
from high_speed_rail import HighSpeedRail
from transportation import ComplexTransport

class LocalTrain_X_HighSpeedRail(ComplexTransport):
    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end)
        self.local_train = LocalTrain("", "", "")
        self.high_speed_rail = HighSpeedRail("", "", "")

    def _create(self):
        if self.local_train.paths:
            self.local_train.create()

        ExpressTrain_transfer_points = ["板橋", "臺北", "新烏日", "新左營"]
        HighSpadeRail_transfer_points = ["板橋", "臺北", "高鐵臺中", "高鐵左營"]

        self.paths += super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                     departure_place=self.start,
                                                     arrival_place=self.end,
                                                     transportation_a=self.local_train,
                                                     transportation_b=self.high_speed_rail,
                                                     transfer_points_a=ExpressTrain_transfer_points,
                                                     transfer_points_b=HighSpadeRail_transfer_points)

        self.paths += super()._insert_transportation(departure_time=self.departure_time,
                                                     departure_place=self.start,
                                                     arrival_place=self.end,
                                                     transportation_src=self.local_train,
                                                     transportation_inner=self.high_speed_rail,
                                                     transfer_points_src=ExpressTrain_transfer_points,
                                                     transfer_points_inner=HighSpadeRail_transfer_points)
