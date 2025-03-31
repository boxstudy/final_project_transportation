import sys
import traceback
import re
from flask import Flask, jsonify, request, abort
from transportation_path import TransportationPath
from high_speed_rail import HighSpeedRail
import json

app = Flask(__name__)
path = TransportationPath()

def validate_time_format(time):
    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"
    if not re.match(pattern, time):
        raise ValueError(f"Time format is incorrect: {time}. Expected format is yyyy-mm-dd hh:mm")

@app.route('/data/change/high_speed_rail/<time>_<from_place>_<to_place>_<discount>_<reserved>', methods=['GET'])
def change_high_speed_rail(time, from_place, to_place, discount, reserved):
    try:
        # Log 請求資訊
        print(f"收到請求: {time}, 從 {from_place} 到 {to_place}, 優惠 {discount}, 預約 {reserved}")

        # 檢查時間格式
        validate_time_format(time)

        # 查詢資料
        val = HighSpeedRail(time, from_place, to_place, discount, reserved).create()
        if not val:
            raise ValueError("查無資料")
        val = val[0]
        if val["departure_time"] != time:
            raise ValueError("查詢時間與請求時間不符")

        # 印出查詢結果
        print("查詢成功，回傳資料筆數:", len(val))
        return jsonify(val)

    except Exception as e:
        print("發生錯誤：", e, file=sys.stderr)
        abort(400, str(e))


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

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=8888, host='0.0.0.0')
