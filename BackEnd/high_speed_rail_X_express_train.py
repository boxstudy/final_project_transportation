from transportation import ComplexTransport
from high_speed_rail import HighSpeedRail
from express_train import ExpressTrain

class HighSpeedRail_X_ExpressTrain(ComplexTransport):
    stations = HighSpeedRail.stations | ExpressTrain.stations
    def __init__(self, departure_time: str, start: str, end: str, discount: bool, reserved: bool):
        super().__init__(departure_time, start, end, self.stations)
        self.discount = discount
        self.reserved = reserved
        self.express_train = ExpressTrain(departure_time, start, end)
        self.high_speed_rail = HighSpeedRail(departure_time, start, end, discount, reserved)

    def _create(self):
        if not self.express_train.paths:
            self.express_train.create()

        ExpressTrain_transfer_points = ["板橋", "臺北", "新烏日", "新左營"]
        HighSpadeRail_transfer_points = ["板橋", "臺北", "高鐵臺中", "高鐵左營"]
        self.paths.extend(super()._replace_part_of_path(self.express_train,
                                                  self.high_speed_rail,
                                                  ExpressTrain_transfer_points,
                                                  HighSpadeRail_transfer_points,
                                                  ExpressTrain.Caozhou_Jilong.values(),
                                                   (ExpressTrain.data_path, "train", "車站")))
        self.paths.extend(super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                             departure_place=self.start,
                                                             arrival_place=self.end,
                                                             transportation_a=self.express_train,
                                                             transportation_b=self.high_speed_rail,
                                                             transfer_points_a=ExpressTrain_transfer_points,
                                                             transfer_points_b=HighSpadeRail_transfer_points))

if __name__ == "__main__":
    import json

    t = HighSpeedRail_X_ExpressTrain("2025-04-24 13:17", "新左營", "新營", False, True)
    t.create()
    print(json.dumps(t.paths, indent=2))
