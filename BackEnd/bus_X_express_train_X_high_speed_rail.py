from bus_X_express_train import Bus_X_ExpressTrain
from express_train import ExpressTrain
from high_speed_rail import HighSpeedRail
from transportation import ComplexTransport

class Bus_X_ExpressTrain_X_HighSpeedRail(ComplexTransport):
    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end)
        self.high_speed_rail = HighSpeedRail("", "", "", discount, reserved)
        self.bus_X_express_train = Bus_X_ExpressTrain(departure_time, start, end)

    def _create(self):
        if self.bus_X_express_train:
            self.bus_X_express_train.create()

        ExpressTrain_transfer_points = ["板橋", "臺北", "新烏日", "新左營"]
        HighSpadeRail_transfer_points = ["板橋", "臺北", "高鐵臺中", "高鐵左營"]

        paths1 = super()._replace_part_of_path(self.bus_X_express_train,
                                      self.high_speed_rail,
                                      ExpressTrain_transfer_points,
                                      HighSpadeRail_transfer_points,
                                      ExpressTrain.Caozhou_Jilong.values(),
                                      (ExpressTrain.data_path, "train", "車站"))
        paths2 = super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                     departure_place=self.start,
                                                     arrival_place=self.end,
                                                     transportation_a=self.bus_X_express_train,
                                                     transportation_b=self.high_speed_rail,
                                                     transfer_points_a=ExpressTrain_transfer_points,
                                                     transfer_points_b=HighSpadeRail_transfer_points)
        self.paths = paths1 + paths2