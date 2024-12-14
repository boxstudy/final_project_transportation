from flask import Flask

app = Flask(__name__)

@app.route('/data/recommend_list', methods=['GET'])
def data_recommend_list():
    return ''# todo

if __name__ == '__main__':
    app.run(threaded=True)