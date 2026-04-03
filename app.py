"""
打卡应用后端 — Flask REST API
运行方式: pip install flask flask-cors && python app.py
访问地址: http://localhost:1130
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import date, datetime, timedelta
import json
import os

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # 允许前端跨域调用

DATA_FILE = "checkin_data.json"


# ─────────────────────────────────────────────
# 数据读写
# ─────────────────────────────────────────────

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"records": {}}


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
# 核心逻辑：连续打卡天数计算
# ─────────────────────────────────────────────

def calc_streak(records: dict, target_date: date = None) -> int:
    """
    从 target_date 向前遍历，统计连续 checked=True 的天数。
    target_date 默认为今天。
    """
    if target_date is None:
        target_date = date.today()

    streak = 0
    current = target_date
    while True:
        rec = records.get(current.isoformat())
        if rec and rec.get("checked") is True:
            streak += 1
            current -= timedelta(days=1)
        else:
            break
    return streak


def enrich_record(date_str: str, record: dict, records: dict) -> dict:
    """给单条记录附上 streak 字段，用于前端展示。"""
    d = date.fromisoformat(date_str)
    return {**record, "date": date_str, "streak": calc_streak(records, d)}


# ─────────────────────────────────────────────
# API 端点
# ─────────────────────────────────────────────

@app.route("/api/status")
def get_status():
    """
    返回今日状态 + 当前连续天数。
    前端打开页面时首先调用此接口。
    """
    data = load_data()
    today_str = date.today().isoformat()
    today_rec = data["records"].get(today_str)
    streak = calc_streak(data["records"])

    return jsonify({
        "today":       today_str,
        "streak":      streak,
        "day_label":   f"day{streak}",
        "today_record": today_rec,   # null 表示今天还未操作
    })


@app.route("/api/records")
def get_records():
    """
    返回全部历史记录，每条附上 streak。
    支持可选查询参数:
        ?start=YYYY-MM-DD&end=YYYY-MM-DD  — 过滤日期范围
    """
    data = load_data()
    start = request.args.get("start")
    end   = request.args.get("end")

    result = {}
    for date_str, rec in sorted(data["records"].items(), reverse=True):
        if start and date_str < start:
            continue
        if end and date_str > end:
            continue
        result[date_str] = enrich_record(date_str, rec, data["records"])

    return jsonify(result)


@app.route("/api/checkin", methods=["POST"])
def checkin():
    """
    为【今天】打卡。若今天已打卡则覆盖（幂等）。
    Body (JSON, 可选): { "note": "..." }
    """
    data = load_data()
    today_str = date.today().isoformat()
    body = request.get_json(silent=True) or {}

    existing = data["records"].get(today_str, {})
    data["records"][today_str] = {
        "checked":    True,
        "note":       body.get("note", existing.get("note", "")),
        "timestamp":  existing.get("timestamp") or datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat() if existing else None,
    }
    save_data(data)

    streak = calc_streak(data["records"])
    return jsonify({"success": True, "streak": streak, "day_label": f"day{streak}"})


@app.route("/api/skip", methods=["POST"])
def skip():
    """
    主动标记今天【不打卡】，连续天数清零。
    Body (JSON, 可选): { "note": "..." }
    """
    data = load_data()
    today_str = date.today().isoformat()
    body = request.get_json(silent=True) or {}

    existing = data["records"].get(today_str, {})
    data["records"][today_str] = {
        "checked":    False,
        "note":       body.get("note", existing.get("note", "")),
        "timestamp":  existing.get("timestamp") or datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat() if existing else None,
    }
    save_data(data)

    return jsonify({"success": True, "streak": 0, "day_label": "day0"})


@app.route("/api/records/<date_str>", methods=["PUT"])
def update_record(date_str):
    """
    编辑任意一天的记录（用于纠错）。
    Body (JSON): { "checked": true/false, "note": "..." }
    编辑后重新计算当天 streak 并返回。
    """
    # 校验日期格式
    try:
        date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "日期格式无效，请使用 YYYY-MM-DD"}), 400

    data = load_data()
    body = request.get_json(silent=True) or {}

    if "checked" not in body:
        return jsonify({"error": "缺少 checked 字段"}), 400

    existing = data["records"].get(date_str, {})
    data["records"][date_str] = {
        "checked":    bool(body["checked"]),
        "note":       body.get("note", existing.get("note", "")),
        "timestamp":  existing.get("timestamp") or datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    save_data(data)

    d = date.fromisoformat(date_str)
    streak = calc_streak(data["records"], d)
    return jsonify({
        "success":   True,
        "date":      date_str,
        "streak":    streak,
        "day_label": f"day{streak}",
    })


@app.route("/api/records/<date_str>", methods=["DELETE"])
def delete_record(date_str):
    """
    删除某天的记录（视为"缺卡"，会影响连续天数计算）。
    """
    data = load_data()
    if date_str in data["records"]:
        del data["records"][date_str]
        save_data(data)
    return jsonify({"success": True})


@app.route("/api/export")
def export_data():
    """
    导出完整 JSON 数据，可直接下载保存。
    """
    data = load_data()
    return jsonify(data)


@app.route("/api/import", methods=["POST"])
def import_data():
    """
    导入外部 JSON 数据。
    Body (JSON):
      {
        "records": { ... },
        "mode": "merge"   // "merge"（默认，新数据覆盖同日旧数据）
                          // "replace"（清除所有旧数据后导入）
      }
    """
    body = request.get_json(silent=True)
    if not body or "records" not in body:
        return jsonify({"error": "数据格式无效，需要包含 records 字段"}), 400

    mode = body.get("mode", "merge")

    if mode == "replace":
        new_data = {"records": body["records"]}
    else:
        data = load_data()
        data["records"].update(body["records"])
        new_data = data

    save_data(new_data)
    return jsonify({"success": True, "count": len(body["records"]), "mode": mode})


# ─────────────────────────────────────────────
# 前端静态文件托管（把 index.html 放 static/ 下即可）
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("打卡服务启动: http://localhost:1130")
    app.run(debug=True, port=1130)
