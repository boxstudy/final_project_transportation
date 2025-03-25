from transportation import Transportation, get_db_connection
from datetime import datetime, timedelta


class Bus(Transportation):
    def __init__(self, departure_time: str, start: str, end: str, folder: str):
        super().__init__(departure_time, start, end, "Bus/")
        self.conn = get_db_connection(folder)
        self.cursor = self.conn.cursor()

    def create_path(self):
        if self.start == "東華大學":
            file = "公車(往花蓮火車站)"
        else:
            file = "公車(往東華大學)"
        self.paths = [[{"type": "Bus", "file": file, "departure_place": self.start,
                        "arrival_place": self.end}]]

    def create_time(self):
        # 取得所有公車時刻
        self.cursor.execute("SELECT 301 FROM bus")
        bus_times = [row[0] for row in self.cursor.fetchall()]  # 取得時間列表

        # 轉換時間格式，方便比較
        def to_time(time_str):
            return datetime.strptime(time_str, "%H:%M")

        departure_dt = to_time(self.departure_time)

        # 找到所有比 departure_time 晚的時間
        later_times = [to_time(time) for time in bus_times if to_time(time) > departure_dt]

        # 找出最接近的時間
        if later_times:
            next_bus_time = min(later_times)  # 取最早的那班車

            # 取得今天的日期
            today_date = datetime.today().strftime("%Y-%m-%d")

            # 格式化出發時間與抵達時間（假設車程為 60 分鐘）
            formatted_departure_time = f"{today_date} {next_bus_time.strftime('%H:%M')}"
            arrival_time = next_bus_time + timedelta(minutes=60)
            formatted_arrival_time = f"{today_date} {arrival_time.strftime('%H:%M')}"

            # 更新路徑資訊
            self.paths[0][0].update(
                {"departure_time": formatted_departure_time, "arrival_time": formatted_arrival_time})

        else:
            return None  # 沒有更晚的車班

    def create_date(self):
        self.paths[0][0].update({"cost": 51})
        return None
