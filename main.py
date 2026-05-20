import os
import cv2
import easyocr
import re
import difflib
import numpy as np
import csv
from collections import Counter
from datetime import datetime
from pymongo import MongoClient
from web3 import Web3

# config
VIDEOS_FOLDER = r"C:\Users\Abhis\OneDrive\Documents\research\videos"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(SCRIPT_DIR, "research_toll_report.csv")

# mongoDB & blockchain config
MONGO_URI = "mongodb://localhost:27017/"
BLOCKCHAIN_RPC = "http://127.0.0.1:7545"
MY_ADDRESS = "0xeb5aF61992Cc9BE738A197757327de93E57e2F6D" 
PRIVATE_KEY = "0xb898cdf0552dbfc9412111e8dd8ed88d45383617f34c85a09734ca03fcd5dfea"

FRAME_SKIP = 3
MIN_DETECTIONS_REQUIRED = 2 
DASHBOARD_WIDTH = 1000
DASHBOARD_HEIGHT = 600

# initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=True)

def log_violation_to_systems(evaders_list):
    """Links Blockchain and MongoDB without changing OCR code."""
    try:
        # mongodb & blockchain connection
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC))
        client = MongoClient(MONGO_URI)
        db = client["TollAuditSystem"]
        
        print(f"\n[SYSTEM] Syncing {len(evaders_list)} violations...")

        for plate in evaders_list:
            tx_id = "BLOCKCHAIN_OFFLINE"
            
            # connection to blockchain
            if w3.is_connected():
                try:
                    tx = {
                        'to': w3.eth.accounts[1],
                        'from': w3.eth.accounts[0],
                        'value': w3.to_wei(0, 'ether'),
                        'data': w3.to_hex(text=f"Toll_Violation:{plate}"),
                        'gas': 2000000,
                        'gasPrice': w3.to_wei('50', 'gwei'),
                        'nonce': w3.eth.get_transaction_count(w3.eth.accounts[0])
                    }
                    tx_hash = w3.eth.send_transaction(tx)
                    tx_id = w3.to_hex(tx_hash)
                    print(f"[BC] Secured: {plate} | TX: {tx_id[:15]}...")
                except Exception as e:
                    print(f"[BC ERROR] Transaction failed: {e}")

            # connection to mongodb with the blockchain
            db.violations.insert_one({
                "plate": plate,
                "type": "Evasion",
                "time": datetime.now(),
                "blockchain_proof": tx_id # The link!
            })
        
        print("[DB] MongoDB records updated with blockchain hashes.")

    except Exception as e:q
        print(f"[CRITICAL ERROR] Systems sync failed: {e}")

def final_indian_logic(text):
    text = re.sub(r'[^A-Z0-9]', '', text.upper())
    if len(text) > 10: text = text[:10]
    if len(text) < 7: return None
    chars = list(text)
    to_digit = {'O': '0', 'Q': '0', 'D': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6', 'T': '7'}
    to_alpha = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B', '6': 'G', '7': 'T'}
    try:
        for i in range(0, 2):
            if chars[i] in to_alpha: chars[i] = to_alpha[chars[i]]
        for i in range(2, 4):
            if chars[i] in to_digit: chars[i] = to_digit[chars[i]]
        for i in range(len(chars)-4, len(chars)):
            if chars[i] in to_digit: chars[i] = to_digit[chars[i]]
    except: pass
    return "".join(chars)

def process_video(video_path, label):
    if not video_path: return set()
    cap = cv2.VideoCapture(video_path)
    all_raw_hits = [] 
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % FRAME_SKIP == 0:
            roi = frame[int(frame.shape[0]*0.4):, :]
            results = reader.readtext(roi, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            for (_, text, conf) in results:
                if conf > 0.45:
                    corrected = final_indian_logic(text)
                    if corrected: all_raw_hits.append(corrected)
        
        # ui visualization
        cv2.imshow("Toll Processing", cv2.resize(frame, (640, 360)))
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    counts = Counter(all_raw_hits)
    freq_filtered = [p for p, c in counts.items() if c >= MIN_DETECTIONS_REQUIRED]
    unique_final = []
    for p in sorted(freq_filtered, key=len, reverse=True):
        if not any(difflib.SequenceMatcher(None, p, ex).ratio() > 0.85 for ex in unique_final):
            unique_final.append(p)
    return set(unique_final)

if __name__ == "__main__":
    vids = {k: None for k in ["entry", "booth", "exit"]}
    for f in os.listdir(VIDEOS_FOLDER):
        for k in vids:
            if k in f.lower() and f.endswith(('.mp4', '.avi')):
                vids[k] = os.path.join(VIDEOS_FOLDER, f)

    if None in vids.values():
        print("[ERROR] Missing required video files.")
    else:
        results = {stage: process_video(path, stage.upper()) for stage, path in vids.items()}
        cv2.destroyAllWindows()

        evaders = []
        for p in results['entry']:
            was_at_exit = any(difflib.SequenceMatcher(None, p, ex).ratio() > 0.82 for ex in results['exit'])
            paid_at_booth = any(difflib.SequenceMatcher(None, p, b).ratio() > 0.82 for b in results['booth'])
            if was_at_exit and not paid_at_booth:
                evaders.append(p)

        with open(REPORT_PATH, mode='w', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(["Timestamp", "Plate_Number", "Status"])
            for p in results['entry']:
                status = "VIOLATION" if p in evaders else "CLEAN"
                csv_writer.writerow([datetime.now().isoformat(), p, status])

        log_violation_to_systems(evaders)

        print(f"\n[FINISH] Total Evaders Processed: {len(evaders)}")