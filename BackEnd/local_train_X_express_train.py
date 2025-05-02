from local_train import LocalTrain
from express_train import ExpressTrain
from transportation import ComplexTransport

class LocalTrain_X_ExpressTrain(ComplexTransport):
    ComplexTransport.stations = LocalTrain.stations | ExpressTrain.stations
    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end)
        self.local_train = LocalTrain("", "", "")
        self.express_train = ExpressTrain("", "", "")

    def _create(self):

        LocalTrain_transfer_points = ['七堵', '中壢', '光復', '南港', '吉安', '嘉義', '壽豐', '大甲', '宜蘭', '富里', '屏東', '彰化', '後龍', '志學', '新城', '新左營', '新竹', '松山', '板橋', '枋寮', '桃園', '樹林', '池上', '沙鹿', '清水', '潮州', '玉里', '瑞穗', '知本', '竹南', '羅東', '臺中', '臺北', '臺南', '臺東', '花蓮', '苑裡', '苗栗', '豐原', '通霄', '關山', '高雄', '鳳山', '鳳林', '鹿野']
        ExpressTrain_transfer_points = ['七堵', '中壢', '光復', '南港', '吉安', '嘉義', '壽豐', '大甲', '宜蘭', '富里', '屏東', '彰化', '後龍', '志學', '新城', '新左營', '新竹', '松山', '板橋', '枋寮', '桃園', '樹林', '池上', '沙鹿', '清水', '潮州', '玉里', '瑞穗', '知本', '竹南', '羅東', '臺中', '臺北', '臺南', '臺東', '花蓮', '苑裡', '苗栗', '豐原', '通霄', '關山', '高雄', '鳳山', '鳳林', '鹿野']

        self.paths += super()._switch_by_transfer_points(departure_time=self.departure_time,
                                                         departure_place=self.start,
                                                         arrival_place=self.end,
                                                         transportation_a=self.local_train,
                                                         transportation_b=self.express_train,
                                                         transfer_points_a=LocalTrain_transfer_points,
                                                         transfer_points_b=ExpressTrain_transfer_points)

        self.paths += super()._insert_transportation(departure_time=self.departure_time,
                                                     departure_place=self.start,
                                                     arrival_place=self.end,
                                                     transportation_src=self.local_train,
                                                     transportation_inner=self.express_train,
                                                     transfer_points_src=LocalTrain_transfer_points,
                                                     transfer_points_inner=ExpressTrain_transfer_points)


if __name__ == "__main__":
    # 將四種對號列車的所有停靠站手動彙整到一個集合中
    express_stations = {
        # 太魯閣號
        "樹林", "板橋", "臺北", "松山", "南港", "七堵",
        "宜蘭", "羅東", "新城", "花蓮", "吉安", "志學",
        "壽豐", "鳳林", "光復", "瑞穗", "玉里", "富里",
        "池上", "關山", "鹿野", "臺東", "知本",
        # 普悠瑪號
        "桃園", "中壢", "新竹", "竹南", "苗栗", "豐原",
        "臺中", "彰化", "嘉義", "臺南", "新左營",
        "高雄", "鳳山", "屏東", "潮州", "枋寮",
        # 自強號（海線停靠站）
        "大甲", "沙鹿", "後龍", "通霄", "苑裡", "清水", "大肚",
        # 莒光號（含所有三等站以上，與上面列車高度重疊，故不再重複列出）
    }

    # 定義非對號列車停靠站：此處假設為所有現役臺鐵車站
    non_express_stations = {
        # （範例，實際可由官方資料擷取）
        "基隆", "七堵", "南港", "松山", "臺北", "板橋", "樹林",
        "桃園", "中壢", "新竹", "竹南", "苗栗", "豐原",
        "臺中", "後龍", "通霄", "苑裡", "大甲", "清水", "沙鹿",
        "彰化", "員林", "斗六", "嘉義", "新營", "臺南", "新左營",
        "高雄", "鳳山", "屏東", "潮州", "枋寮", "宜蘭", "羅東",
        "新城", "花蓮", "吉安", "志學", "壽豐", "鳳林", "光復",
        "瑞穗", "玉里", "富里", "池上", "關山", "鹿野", "臺東",
        "知本"
    }

    # 計算交集：即同時有對號與非對號列車停靠之站點
    common_stations = express_stations & non_express_stations

    # 排序並列印結果
    print("同時承擔對號與非對號列車的站點：")
    for station in sorted(common_stations):
        print(f"'{station}', ", end="")
    # ['七堵', '中壢', '光復', '南港', '吉安', '嘉義', '壽豐', '大甲', '宜蘭', '富里', '屏東', '彰化', '後龍', '志學', '新城', '新左營', '新竹', '松山', '板橋', '枋寮', '桃園', '樹林', '池上', '沙鹿', '清水', '潮州', '玉里', '瑞穗', '知本', '竹南', '羅東', '臺中', '臺北', '臺南', '臺東', '花蓮', '苑裡', '苗栗', '豐原', '通霄', '關山', '高雄', '鳳山', '鳳林', '鹿野']
