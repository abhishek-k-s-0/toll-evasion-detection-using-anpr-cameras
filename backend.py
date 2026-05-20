from flask import Flask, render_template, jsonify, Response
from pymongo import MongoClient
import os
import csv
import io
from datetime import datetime

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

client = MongoClient("mongodb://localhost:27017/")
db = client['TollAuditSystem'] 
collection = db['violations']

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/api/evaders')
def get_evaders():
    """Fetches and formats data for the frontend."""
    raw_data = list(collection.find({}, {'_id': 0}).sort("time", -1))
    
    formatted_data = []
    for row in raw_data:
        time_val = row.get("time")
        timestamp = time_val.strftime("%Y-%m-%d %H:%M:%S") if isinstance(time_val, datetime) else str(time_val)

        formatted_data.append({
            "timestamp": timestamp,
            "plate": row.get("plate", "Unknown"),
            "block_hash": row.get("blockchain_proof", "N/A")
        })
    return jsonify(formatted_data)

@app.route('/download/csv')
def download_csv():
    """Generates a downloadable CSV report from MongoDB data."""
    data = list(collection.find({}, {'_id': 0}).sort("time", -1))
    
    def generate():
        # CSV Header
        yield "Timestamp,Plate Number,Status,Blockchain Hash\n"
        for row in data:
            time_val = row.get("time")
            ts = time_val.strftime("%Y-%m-%d %H:%M:%S") if isinstance(time_val, datetime) else str(time_val)
            plate = row.get("plate")
            proof = row.get("blockchain_proof")
            # Format row for CSV
            yield f"{ts},{plate},VIOLATION,{proof}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=toll_audit_report.csv"}
    )

if __name__ == '__main__':
    print(">>> Toll Audit Dashboard LIVE at http://127.0.0.1:5000")
    app.run(port=5000, debug=True)