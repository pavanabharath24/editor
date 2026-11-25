#!/usr/bin/env python3
"""
Cash & Crown Studio - Live Production Dashboard & Web Server
Provides real-time render progress, live preview playback, timeline inspection,
and local/Kaggle rendering execution.
"""

import os
import sys
import json
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_file, request
from flask_cors import CORS

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(APP_DIR, "..")
sys.path.append(PROJECT_ROOT)

app = Flask(__name__, template_folder=os.path.join(APP_DIR, "templates"), static_folder=os.path.join(APP_DIR, "static"))
CORS(app)

DAY1_PROJECT_DIR = os.path.join(PROJECT_ROOT, "projects", "cash_and_crown", "day1_rockstar")
VIDEO_OUTPUT = os.path.join(DAY1_PROJECT_DIR, "output", "day1_rockstar_full.mp4")
TEST_PREVIEW = os.path.join(DAY1_PROJECT_DIR, "test_preview.mp4")
PROGRESS_FILE = os.path.join(DAY1_PROJECT_DIR, ".progress.json")
QUICK_DIR = os.path.join(PROJECT_ROOT, "projects", "cash_and_crown", "quick_showcase")
QUICK_VIDEO = os.path.join(QUICK_DIR, "showcase.mp4")
QUICK_PROGRESS = os.path.join(QUICK_DIR, ".progress.json")

render_lock = threading.Lock()
is_rendering = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/timeline")
def get_timeline():
    timeline_path = os.path.join(DAY1_PROJECT_DIR, "timeline.json")
    if os.path.exists(timeline_path):
        with open(timeline_path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"scenes": []})


@app.route("/api/status")
def get_status():
    global is_rendering
    progress_data = {}
    
    # Read the most recent progress file
    files_to_check = [PROGRESS_FILE, QUICK_PROGRESS]
    latest_file = None
    latest_mtime = 0
    for p in files_to_check:
        if os.path.exists(p):
            mtime = os.path.getmtime(p)
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_file = p
                
    if latest_file:
        try:
            with open(latest_file, "r") as f:
                progress_data = json.load(f)
        except Exception:
            pass

    has_video = os.path.exists(VIDEO_OUTPUT) or os.path.exists(TEST_PREVIEW) or os.path.exists(QUICK_VIDEO)
    return jsonify({
        "rendering": is_rendering,
        "video_ready": has_video,
        "progress": progress_data
    })


@app.route("/api/video")
def get_video():
    # Return most recently updated video file
    videos = [VIDEO_OUTPUT, TEST_PREVIEW, QUICK_VIDEO]
    existing = [v for v in videos if os.path.exists(v)]
    if existing:
        target = max(existing, key=os.path.getmtime)
        return send_file(target, mimetype="video/mp4")
    return "Video not found", 404


def run_render_worker():
    global is_rendering
    try:
        render_script = os.path.join(PROJECT_ROOT, "core", "render_video.py")
        cmd = [
            sys.executable, render_script,
            "--project", DAY1_PROJECT_DIR,
            "--output", VIDEO_OUTPUT,
            "--fps", "30"
        ]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"[!] Render error: {e}")
    finally:
        with render_lock:
            is_rendering = False


@app.route("/api/render", methods=["POST"])
def trigger_render():
    global is_rendering
    with render_lock:
        if is_rendering:
            return jsonify({"status": "already_running"}), 400
        is_rendering = True

    thread = threading.Thread(target=run_render_worker, daemon=True)
    thread.start()
    return jsonify({"status": "started"})


@app.route("/api/kaggle/push", methods=["POST"])
def trigger_kaggle():
    try:
        kaggle_dir = os.path.join(PROJECT_ROOT, "kaggle")
        res = subprocess.run(["kaggle", "kernels", "push"], cwd=kaggle_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return jsonify({
            "status": "success" if res.returncode == 0 else "error",
            "message": res.stdout + res.stderr
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = 5050
    print(f"[+] Starting Cash & Crown Studio Dashboard on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
