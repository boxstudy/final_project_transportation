import copy

from transportation import Transportation, get_db_connection, DATA_PATH, TransportationError
from datetime import datetime, timedelta


class Bus(Transportation):
    data_path = DATA_PATH + "Bus/"

    def __init__(self, departure_time: str, start: str, end: str):
        super().__init__(departure_time, start, end)



    def _create_path(self):
        station = ["東華大學", "花蓮"]
        if self.start not in station:
            raise TransportationError(f"Invalid start place {self.start}")
        if self.end not in station:
            raise TransportationError(f"Invalid end place {self.end}")

        if self.start == "東華大學":
            file = "公車(往花蓮火車站).db"
        else:
            file = "公車(往東華大學).db"

        self.paths = [[{"type": "Bus", "file": file, "departure_place": self.start,
                        "arrival_place": self.end}]]

    def _create_time(self):
        num = 4  # number of bus
        for i in range(num - 1):
            self.paths.append(copy.deepcopy(self.paths[0]))

        # 取得所有公車時刻
        conn = get_db_connection(self.data_path + self.paths[0][0]["file"])
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT {"花蓮301"} FROM bus")
            bus_times = [row[0] for row in cursor.fetchall()]  # 取得時間列表
        finally:
            cursor.close()
            conn.close()

        # 找到所有比 departure_time 晚的時間
        dt = datetime.strptime(self.departure_time, "%Y-%m-%d %H:%M").strftime("%H:%M")
        later_times = [time for time in bus_times if time > dt]
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
                formatted_arrival_time = f"{date} {arrival_time.strftime("%H:%M")}"

                # 更新路徑資訊
                self.paths[i][0].update(
                    {"departure_time": formatted_departure_time, "arrival_time": formatted_arrival_time})

    def _create_cost(self):
        for i in range(len(self.paths)):
            self.paths[i][0].update({"cost": 51})



if __name__ == "__main__":
    bus = Bus("2022-03-15 10:00", "東華大學", "花蓮")
    bus.create()
    print(bus.paths)