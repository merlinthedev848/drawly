import os
import json
from flask import Flask, render_template, jsonify, send_from_directory, request
from data_loader import load_lotto_data
from stats_engine import (
    compute_ball_frequencies, 
    compute_gap_statistics, 
    compute_cooccurrence_matrix, 
    perform_chi_square_test,
    compute_number_likelihoods,
    TOTAL_BALLS,
    THEO_DRAW_PROB
)
from generator import generate_logical_tickets

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
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"error": "Data not found"}), 404

@app.route("/api/generate", methods=["POST"])
def api_generate():
    req = request.get_json() or {}
    model = req.get("model", "harmonic")
    num_tickets = req.get("num_tickets", 5)
    weights = req.get("weights", {'base': 0.25, 'hot': 0.35, 'cold': 0.30, 'pair': 0.10})
    odd_even_filter = req.get("odd_even_filter", True)
    sum_filter = req.get("sum_filter", True)

    tickets = generate_logical_tickets(
        num_tickets=num_tickets,
        model=model,
        weights=weights,
        odd_even_filter=odd_even_filter,
        sum_filter=sum_filter
    )
    return jsonify({"tickets": tickets})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
