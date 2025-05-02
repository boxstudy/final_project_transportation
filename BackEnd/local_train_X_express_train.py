from local_train import LocalTrain
from express_train import ExpressTrain
from transportation import ComplexTransport

class LocalTrain_X_ExpressTrain(ComplexTransport):
    stations = LocalTrain.stations | ExpressTrain.stations
    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end, self.stations)
        self.local_train = LocalTrain("", "", "")
        self.express_train = ExpressTrain("", "", "")

    def _create(self):

        # transfer_points 剛好就是 ExpressTrain.stations
        # LocalTrain_transfer_points = ['七堵', '三義', '中壢', '九曲堂', '二水', '光復', '內獅', '八堵', '冬山', '加祿', '北埔', '南州', '南平', '南港', '南澳', '吉安', '后里', '和平', '員林', '善化', '嘉義', '基隆', '壽豐', '大林', '大武', '大湖', '太麻里', '宜蘭', '富源', '富里', '屏東', '岡山', '康樂', '彰化', '志學', '斗六', '斗南', '新城', '新左營', '新市', '新烏日', '新營', '新竹', '新豐', '東澳', '東竹', '東里', '松山', '板橋', '枋寮', '枋山', '林內', '林榮新光', '林邊', '桃園', '楊梅', '楠梓', '樹林', '民雄', '永康', '汐止', '池上', '湖口', '潭子', '潮州', '瀧溪', '猴硐', '玉里', '瑞源', '瑞穗', '瑞芳', '田中', '知本', '礁溪', '社頭', '福隆', '竹北', '竹南', '羅東', '臺中', '臺北', '臺南', '臺東', '花蓮', '苗栗', '萬榮', '萬華', '蘇澳', '蘇澳新', '西勢', '豐原', '豐田', '貢寮', '路竹', '金崙', '銅鑼', '關山', '隆田', '雙溪', '頭城', '高雄', '鳳山', '鳳林', '鶯歌', '鹿野']
        # ExpressTrain_transfer_points = ['七堵', '三義', '中壢', '九曲堂', '二水', '光復', '內獅', '八堵', '冬山', '加祿', '北埔', '南州', '南平', '南港', '南澳', '吉安', '后里', '和平', '員林', '善化', '嘉義', '基隆', '壽豐', '大林', '大武', '大湖', '太麻里', '宜蘭', '富源', '富里', '屏東', '岡山', '康樂', '彰化', '志學', '斗六', '斗南', '新城', '新左營', '新市', '新烏日', '新營', '新竹', '新豐', '東澳', '東竹', '東里', '松山', '板橋', '枋寮', '枋山', '林內', '林榮新光', '林邊', '桃園', '楊梅', '楠梓', '樹林', '民雄', '永康', '汐止', '池上', '湖口', '潭子', '潮州', '瀧溪', '猴硐', '玉里', '瑞源', '瑞穗', '瑞芳', '田中', '知本', '礁溪', '社頭', '福隆', '竹北', '竹南', '羅東', '臺中', '臺北', '臺南', '臺東', '花蓮', '苗栗', '萬榮', '萬華', '蘇澳', '蘇澳新', '西勢', '豐原', '豐田', '貢寮', '路竹', '金崙', '銅鑼', '關山', '隆田', '雙溪', '頭城', '高雄', '鳳山', '鳳林', '鶯歌', '鹿野']
        transfer_points = list(self.express_train._get_up_and_down_station(self.start)) + list(self.express_train._get_up_and_down_station(self.end))

        self.paths += super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                         departure_place=self.start,
                                                         arrival_place=self.end,
                                                         transportation_a=self.local_train,
                                                         transportation_b=self.express_train,
                                                         transfer_points_a=transfer_points,
                                                         transfer_points_b=transfer_points)

        self.paths += super()._insert_transportation(departure_time=self.departure_time,
                                                     departure_place=self.start,
                                                     arrival_place=self.end,
                                                     transportation_src=self.local_train,
                                                     transportation_inner=self.express_train,
                                                     transfer_points_src=transfer_points,
                                                     transfer_points_inner=transfer_points)


if __name__ == "__main__":

    # common_stations = ExpressTrain.stations & LocalTrain.stations
    #
    # # 排序並列印結果
    # print("同時承擔對號與非對號列車的站點：")
    # print('[', end="")
    # for station in sorted(common_stations):
    #     print(f", '{station}'", end="")
    # print(']')

    t = LocalTrain_X_ExpressTrain("2022-01-01 08:00", "基隆", "臺北")
    t.create()
    print(t.paths)
