from transportation import ComplexTransport
from high_speed_rail import HighSpeedRail
from express_train import ExpressTrain

class HighSpeedRail_X_ExpressTrain(ComplexTransport):
    def __init__(self, express_train: ExpressTrain, high_speed_rail: HighSpeedRail):
        super().__init__()
        self.express_train = express_train
        self.high_speed_rail = high_speed_rail

    def create(self):
        ExpressTrain_transfer_points = ["板橋", "臺北", "新烏日", "新左營"]
        HighSpadeRail_transfer_points = ["板橋", "臺北", "高鐵臺中", "高鐵左營"]
        self.paths = super()._replace_part_of_path(self.express_train,
                                                  self.high_speed_rail,
                                                  ExpressTrain_transfer_points,
                                                  HighSpadeRail_transfer_points,
                                                  ExpressTrain.Caozhou_Jilong.values(),
                                                   ("train", "車站")) if self.express_train.paths else []
        return self.paths