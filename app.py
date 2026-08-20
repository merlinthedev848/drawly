import os
import json
from flask import Flask, render_template, jsonify, send_from_directory, request
from data_loader import load_lotto_data
from stats_engine import (
    compute_ball_frequencies, 
    compute_gap_statistics, 
    compute_cooccurrence_matrix, 
    perform_chi_square_test,
    compute_number_likelihoods
)
from generator import generate_logical_tickets
from auto_updater import run_auto_update_pipeline

app = Flask(__name__, static_folder="static", template_folder="templates")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "lotto_data.json")

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/lotto_data.json")
def get_static_json():
    if os.path.exists(JSON_FILE):
        return send_from_directory(BASE_DIR, "lotto_data.json")
    return jsonify({"error": "Data file not found"}), 404

@app.route("/api/stats")
def api_stats():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"error": "Data not found"}), 404

@app.route("/api/auto-update", methods=["POST", "GET"])
def api_auto_update():
    try:
        res = run_auto_update_pipeline()
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/generate", methods=["POST"])
def api_generate():
    req = request.get_json() or {}
    model = req.get("model", "harmonic")
    num_tickets = req.get("num_tickets", 5)
    game_type = req.get("game_type", "uk")

    tickets = generate_logical_tickets(
        num_tickets=num_tickets,
        model=model,
        game_type=game_type
    )
    return jsonify({"tickets": tickets})

if __name__ == "__main__":
    # Auto update dataset on server launch
    try:
        run_auto_update_pipeline()
    except Exception as err:
        print("Auto-update launch check:", err)

    app.run(host="0.0.0.0", port=5000, debug=True)
