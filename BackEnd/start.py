import sys
from pprint import pprint

import re
from flask import Flask, jsonify
from transportation_path import TransportationPath

app = Flask(__name__)
path = TransportationPath()

def validate_time_format(time):
    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"  # 年-月-日 时:分
    if not re.match(pattern, time):
        raise ValueError(f"Time format is incorrect: {time}. Expected format is yr/month/day-hr:min.")

@app.route('/data/recommend<time>_<from_place>_<to_place>', methods=['GET'])
def data_recommend(time, from_place, to_place):
    val = [[time, from_place, to_place]]
    try:
        validate_time_format(time)
        val = path.get(time, from_place, to_place)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    return val

if __name__ == '__main__':
    val = data_recommend("2024/03/20-12:20", "臺北", "基隆")
    print(val)

    app.run(threaded=True, port=8888, host='0.0.0.0')
