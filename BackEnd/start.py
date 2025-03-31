import json
import re
import sys
import traceback
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, abort
from gevent import pywsgi

from high_speed_rail import HighSpeedRail
from transportation_path import TransportationPath

app = Flask(__name__)
path = TransportationPath()

def validate_time_format(time):
    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"
    if not re.match(pattern, time):
        raise ValueError(f"Time format is incorrect: {time}. Expected format is yyyy-mm-dd hh:mm")



@app.route('/data/change/<time>_<from_place>_<to_place>', methods=['GET'])
def data_change(time, from_place, to_place):
    try:
        validate_time_format(time)
        if not from_place:
            raise ValueError("from_place input is empty")
        if  not to_place:
            raise ValueError("to_place input is empty")

        type = request.args.get('type', '')

        match type:
            case 'HighSpeedRail':
                discount = request.args.get('discount', '')
                reserved = request.args.get('reserved', '')
                if not discount.isdigit() or not reserved.isdigit():
                    raise ValueError("discount or reserved 錯誤")
                time = (datetime.strptime(time, '%Y-%m-%d %H:%M') - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
                val = HighSpeedRail(time, from_place, to_place, bool(discount), bool(reserved)).create()
                if not val:
                    raise ValueError("查無資料")
                val = val[0]
                if val["departure_time"] != time:
                    raise ValueError("查詢時間與請求時間不符")

            case _:
                raise ValueError("type unknown")

        return jsonify(val)

    except Exception as e:
        abort(400, str(e))

@app.route('/data/recommend_division<time>_<from_place>_<to_place>', methods=['GET'])
def data_recommend_division(time, from_place, to_place):
    try:
        validate_time_format(time)

        if not from_place:
            raise ValueError("from_place input is empty")
        if  not to_place:
            raise ValueError("to_place input is empty")

        want_type = request.args.get('want_type', '-1')
        ignore_type = request.args.get('ignore_type', '0')
        if not want_type.isdigit():
            raise ValueError("want_type error")
        if not ignore_type.isdigit():
            raise ValueError("ignore_type error")

        high_speed_rail_discount = request.args.get('HighSpeedRail_discount', '0')
        high_speed_rail_reserved = request.args.get('HighSpeedRail_reserved', '1')
        if not high_speed_rail_discount.isdigit():
            raise ValueError("HighSpeedRail_discount error")
        if not high_speed_rail_reserved.isdigit():
            raise ValueError("HighSpeedRail_reserved error")


    except Exception as e:
        abort(400, str(e))

    try:
        data = path.get_division(start_date=time,
                                 departure_place=from_place,
                                 arrive_place=to_place,
                                 mask=int(want_type) & ~int(ignore_type),
                                 high_speed_rail_discount=bool(high_speed_rail_discount),
                                 high_speed_rail_reserved=bool(high_speed_rail_reserved))
        if not data:
            return jsonify({"status": "failure", "data": data})
        return jsonify({"status": "success", "data": data})

    except Exception as e:
        abort(500, str(e))


@app.route('/data/recommend<time>_<from_place>_<to_place>', methods=['GET'])
def data_recommend(time, from_place, to_place):
    try:
        # Log 請求資訊
        print(f"\n📥 收到請求: {time}, 從 {from_place} 到 {to_place}")

        # 檢查時間格式
        validate_time_format(time)

        # 查詢資料
        val = path.get(time, from_place, to_place)

        # 印出查詢結果
        print("✅ 查詢成功，回傳資料筆數:", len(val))
        print(json.dumps(val, indent=2, ensure_ascii=False))
        return jsonify(val)

    except Exception as e:
        # 印出錯誤訊息與 traceback
        print("❌ 發生錯誤：", e, file=sys.stderr)
        traceback.print_exc() # ??? 需要這行嗎？

        return jsonify({
            "error": str(e),
            "from": from_place,
            "to": to_place,
            "time": time
        }), 400, {'Content-Type': 'application/json'}

@app.route('/exit', methods=['GET'])
def exit():
    user = request.args.get('user', '')
    if user != 'admin':
        return jsonify({"status": "failure"}), 401, {'Content-Type': 'application/json'}

    password = request.args.get('password', '')
    if password != '<PASSWORD>':
        return jsonify({"status": "failure"}), 403, {'Content-Type': 'application/json'}

    print("系統關閉")
    server.stop()
    return jsonify({"status": "success"}), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8888), app)
    server.serve_forever()
