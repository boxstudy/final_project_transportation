from bus import Bus
from express_train import ExpressTrain
from transportation import ComplexTransport


class Bus_X_Express(ComplexTransport):
    def __init__(self, start_place, end_place):
        super().__init__()