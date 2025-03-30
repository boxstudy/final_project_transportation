from bus import Bus
from express_train import ExpressTrain
from transportation import ComplexTransport


class Bus_X_ExpressTrain(ComplexTransport):
    def __init__(self, departure_time, start, end):
        super().__init__(departure_time, start, end)

    def _create_bus_to_express_train(self):
        bus = Bus(self.departure_time, self.start, "花蓮")
        bus_path = bus.create()
        if not bus_path:
            return
        for path in bus_path:
            express_train = ExpressTrain(path[-1]["arrival_time"], "花蓮", self.end)
            express_train_path = express_train.create()
            if express_train_path:
                self.paths.append(path + min(express_train_path, key=lambda x: x[0]["departure_time"]))

    def _create_express_train_to_bus(self):
        express_train = ExpressTrain(self.departure_time, self.start, "花蓮")
        express_train_path = express_train.create()
        if not express_train_path:
            return
        for path in express_train_path:
            bus = Bus(path[-1]["arrival_time"], "花蓮", self.end)
            bus_path = bus.create()
            if bus_path:
                self.paths.append(path + min(bus_path, key=lambda x: x[0]["departure_time"]))

    def _create(self):
        self._create_bus_to_express_train()
        self._create_express_train_to_bus()



if __name__ == "__main__":
    print(Bus_X_ExpressTrain("2022-03-15 10:00", "東華大學", "基隆").create())