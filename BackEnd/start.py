import sys
from pprint import pprint

import re
from flask import Flask
from transportation_path import TransportationPath

app = Flask(__name__)
path = TransportationPath()

def validate_time_format(time):
    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"  # 年-月-日 时:分
    if not re.match(pattern, time):
        raise ValueError(f"Time format is incorrect: {time}. Expected format is yr-month-day hr:min.")

@app.route('/data/recommend<time>_<from_place>_<to_place>', methods=['GET'])
# 舉例，下面回傳了三個從高雄到臺北的方案，資料格式為：
# [[{'arrival_place': '臺北',
#    'arrival_time': '2024-08-26 11:42',
#    'cost': 843,
#    'departure_place': '高雄',
#    'departure_time': '2024-08-26 08:00',
#    'transportation_name': '普悠瑪_162',
#    'type': 'Express_Train'}],
#
#  [{'arrival_place': '臺北',
#    'arrival_time': '2024-08-26 17:16',
#    'cost': 650,
#    'departure_place': '高雄',
#    'departure_time': '2024-08-26 11:14',
#    'transportation_name': '莒光_516',
#    'type': 'Express_Train'}],
#
#  [{'arrival_place': '新左營',
#    'arrival_time': '2024-08-26 07:52',
#    'cost': 23,
#    'departure_place': '高雄',
#    'departure_time': '2024-08-26 07:41',
#    'transportation_name': '自強3000_302',
#    'type': 'Express_Train'},
#   {'arrival_place': '板橋',
#    'arrival_time': '2024-08-26 09:21',
#    'cost': '730',
#    'departure_place': '左營',
#    'departure_time': '2024-08-26 07:55',
#    'train_number': '108',
#    'type': 'HighSpeedRail'},
#   {'arrival_place': '臺北',
#    'arrival_time': '2024-08-26 08:40',
#    'cost': 23,
#    'departure_place': '板橋',
#    'departure_time': '2024-08-26 08:29',
#    'transportation_name': '自強3000_472',
#    'type': 'Express_Train'}]]
def data_recommend(time, from_place, to_place):
    val = []
    try:
        validate_time_format(time)
        val = path.get(time, from_place, to_place)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    return val

if __name__ == '__main__':
    val = data_recommend("2024-08-26 07:38", "高雄", "臺北")
    pprint(val)

    app.run(threaded=True, port=8888, host='0.0.0.0')
