from bus_X_express_train import Bus_X_ExpressTrain
from express_train import ExpressTrain
from high_speed_rail import HighSpeedRail
from transportation import ComplexTransport

class HighSpeedRail_X_ExpressTrain(ComplexTransport):
    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end)
        self.high_speed_rail = HighSpeedRail("", "", "", discount, reserved)
        self.bus_X_express_train = Bus_X_ExpressTrain(departure_time, start, end)

    def _create(self):
        if self.bus_X_express_train:
            self.bus_X_express_train.create()

        self.paths = super()._replace_part_of_path(self.bus_X_express_train,
                                      self.high_speed_rail,
                                      ["板橋", "臺北", "新烏日", "新左營"],
                                      ["板橋", "臺北", "高鐵臺中", "高鐵左營"],
                                      ExpressTrain.Caozhou_Jilong.values(),
                                      ("train", "車站"))