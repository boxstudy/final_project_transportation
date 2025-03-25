import copy

from transportation import Transportation, get_db_connection
from datetime import datetime, timedelta


class Bus(Transportation):
    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end, "Bus/")

    def __create_path(self):
        if self.start == "東華大學":
            file = "公車(往花蓮火車站).db"
        else:
            file = "公車(往東華大學).db"
        self.paths = [[{"type": "Bus", "file": file, "departure_place": self.start,
                        "arrival_place": self.end}]]

    def __create_time(self):
        num = 1  # number of bus
        for i in range(num - 1):
            self.paths.append(copy.deepcopy(self.paths[0]))

        # 取得所有公車時刻
        with get_db_connection(self.data_path + self.paths[0][0]["file"]) as conn, conn.cursor() as cursor:
            cursor.execute("SELECT 301 FROM bus")
            bus_times = [row[0] for row in cursor.fetchall()]  # 取得時間列表

        # 找到所有比 departure_time 晚的時間
        later_times = [time for time in bus_times if time > self.departure_time]
        later_times.sort()


        # 找出最接近的時間
        for i in range(num):
            if len(later_times) > i:
                departure_time = later_times[i]

                # 取得日期
                date = datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")

                # 格式化出發時間與抵達時間（假設車程為 60 分鐘）
                formatted_departure_time = f"{date} {departure_time}"
                arrival_time = datetime.strptime(departure_time, "%H:%M") + timedelta(minutes=60)
                formatted_arrival_time = f"{date} {arrival_time.strftime("%Y-%m-%d %H:%M")}"

                # 更新路徑資訊
                self.paths[i][0].update(
                    {"departure_time": formatted_departure_time, "arrival_time": formatted_arrival_time})


    def __create_cost(self):
        for i in range(len(self.paths)):
            self.paths[i][0].update({"cost": 51})
