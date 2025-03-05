from pprint import pprint

from flask import Flask
from transportation_path import TransportationPath

app = Flask(__name__)
path = TransportationPath()

# 注意 time 格式: yr/month/day-hr:min
@app.route('/data/recommend<time>_<from_place>_<to_place>', methods=['GET'])
def data_recommend(time, from_place, to_place):
    val = path.get(time, from_place, to_place)
    return val

if __name__ == '__main__':

    app.run(threaded=True, port=8888, debug=True, host='0.0.0.0')
