from flask import Flask
from transportation_path import TransportationPath

app = Flask(__name__)
path = TransportationPath()

@app.route('/data/recommend<from_place>-<to_place>', methods=['GET'])
def data_recommend(from_place, to_place):
    val = path.get("2024/5/4-10:00", from_place, to_place)
    return val

if __name__ == '__main__':

    v = path.get("2024/5/4-10:00", "潮州", "基隆")
    print(v)

    app.run(threaded=True, port=8888, debug=True, host='0.0.0.0')
