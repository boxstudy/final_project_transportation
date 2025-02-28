from flask import Flask
from transportation_path import TransportationPath

app = Flask(__name__)
path = TransportationPath()

@app.route('/data/recommend_list', methods=['GET'])
def data_recommend_list():
    return path.get("2024/5/4-10:00", "潮州", "基隆")

if __name__ == '__main__':
    v = path.get("2024/5/4-10:00", "潮州", "基隆")
    print(v)
    app.run(threaded=True, port=8888, debug=True)

