import express_train
from transportation import ComplexTransport
from high_speed_rail import HighSpeedRail
from express_train import ExpressTrain

class HighSpeedRail_X_ExpressTrain(ComplexTransport):
    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end)
        self.discount = discount
        self.reserved = reserved
        self.express_train = ExpressTrain(departure_time, start, end)
        self.high_speed_rail = HighSpeedRail(departure_time, start, end, discount, reserved)

    def _create(self):
        if not self.express_train.paths:
            self.express_train.create()

        ExpressTrain_transfer_points = ["板橋", "臺北", "新烏日", "新左營"]
        HighSpadeRail_transfer_points = ["板橋", "臺北", "高鐵臺中", "高鐵左營"]
        self.paths = super()._replace_part_of_path(self.express_train,
                                                  self.high_speed_rail,
                                                  ExpressTrain_transfer_points,
                                                  HighSpadeRail_transfer_points,
                                                  ExpressTrain.Caozhou_Jilong.values(),
                                                   ("train", "車站")) if self.express_train.paths else []
