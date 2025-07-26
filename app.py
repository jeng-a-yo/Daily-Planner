# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from daily_planner.constants import TODAY_FILE, FOOD_DB_FILE
import json
import os
from subprocess import run
from datetime import datetime
import pytz
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

app = Flask(__name__)

DATA_DIR = "./"  # Adjust path if needed


def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def home():
    day_file = TODAY_FILE
    data = load_json(day_file)
    return render_template("index.html", data=data)


@app.route("/search_food")
def search_food():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"foods": []})
    
    try:
        food_db = load_json(FOOD_DB_FILE)
        matches = []
        for name, data in food_db.items():
            if query in name.lower():
                matches.append({
                    "name": name,
                    "protein": data.get("protein", 0),
                    "fat": data.get("fat", 0),
                    "carbon": data.get("carbon", 0)
                })
        return jsonify({"foods": matches[:10]})  # Limit to 10 results
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/update_task", methods=["POST"])
def update_task():
    date = request.form.get('date')
    if date:
        day_file = os.path.join("logs", f"{date}.json")
    else:
        day_file = TODAY_FILE
    data = load_json(day_file)
    part = request.form['part']
    index = int(request.form['index'])
    new_value = request.form['done'] == 'true'
    # Try all case variants
    if part in data['done']:
        data['done'][part][index] = new_value
    elif part.capitalize() in data['done']:
        data['done'][part.capitalize()][index] = new_value
    elif part.lower() in data['done']:
        data['done'][part.lower()][index] = new_value
    save_json(day_file, data)
    return jsonify({"success": True})


@app.route("/update_goal", methods=["POST"])
def update_goal():
    date = request.form.get('date')
    if date:
        day_file = os.path.join("logs", f"{date}.json")
    else:
        day_file = TODAY_FILE
    data = load_json(day_file)
    section = request.form['section']
    index = int(request.form['index'])
    new_value = request.form['done'] == 'true'
    # Try all case variants
    if section in data['goals']:
        data['goals'][section][index]['done'] = new_value
    elif section.capitalize() in data['goals']:
        data['goals'][section.capitalize()][index]['done'] = new_value
    elif section.lower() in data['goals']:
        data['goals'][section.lower()][index]['done'] = new_value
    save_json(day_file, data)
    return jsonify({"success": True})


@app.route("/add_task", methods=["POST"])
def add_task():
    day_file = TODAY_FILE
    data = load_json(day_file)
    section = request.form['section']
    text = request.form['text']
    data['tasks'][section].append(text)
    data['done'][section].append(False)
    save_json(day_file, data)
    return jsonify({"success": True})


@app.route("/add_goal", methods=["POST"])
def add_goal():
    day_file = TODAY_FILE
    data = load_json(day_file)
    section = request.form['section']
    text = request.form['text']
    data['goals'][section].append({"text": text, "done": False})
    save_json(day_file, data)
    return jsonify({"success": True})


@app.route("/add_food", methods=["POST"])
def add_food():
    day_file = TODAY_FILE
    data = load_json(day_file)
    meal = request.form['meal']
    name = request.form['name']
    weight = float(request.form['weight'])
    data['food'][meal].append({"name": name, "weight": weight})
    save_json(day_file, data)
    return jsonify({"success": True})


@app.route("/add_water", methods=["POST"])
def add_water():
    day_file = TODAY_FILE
    data = load_json(day_file)
    amount = int(request.form['amount'])
    if 'water' not in data:
        data['water'] = 0
    data['water'] += amount
    save_json(day_file, data)
    return jsonify({"success": True, "total": data['water']})


@app.route("/reload_today")
def reload_today():
    today_str = datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d')
    filename = os.path.join("logs", f"{today_str}.json")
    if not os.path.exists(filename):
        run(["uv", "run", "main.py", "init"], check=True)
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/get_day")
def get_day():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "No date provided"})
    filename = os.path.join("logs", f"{date}.json")
    today_str = datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d')
    if date == today_str and not os.path.exists(filename):
        run(["uv", "run", "main.py", "init"], check=True)
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/get_today_str")
def get_today_str():
    today_str = datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d')
    return jsonify({"today": today_str})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
