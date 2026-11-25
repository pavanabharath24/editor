#!/usr/bin/env python3
import os
import subprocess

CLIPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "projects", "cash_and_crown", "day1_rockstar", "assets", "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)

NODE_PATH = "/home/pavana/.nvm/versions/node/v24.13.1/bin/node"

GAME_SOURCES = [
    {
        "name": "gta_vice_city_clean.mp4",
        "url": "https://www.youtube.com/watch?v=wQp7gXQkI20",
        "start": "00:01:30",
        "duration": "10"
    },
    {
        "name": "gta_san_andreas_clean.mp4",
        "url": "https://www.youtube.com/watch?v=mZfxD03w1Lg",
        "start": "00:02:00",
        "duration": "10"
    },
    {
        "name": "gta5_clean.mp4",
        "url": "https://www.youtube.com/watch?v=N-xHcvUG3WI",
        "start": "00:01:00",
        "duration": "10"
    }
]

for item in GAME_SOURCES:
    outpath = os.path.join(CLIPS_DIR, item["name"])
    if os.path.exists(outpath) and os.path.getsize(outpath) > 50000:
        print(f"[✓] {item['name']} already exists")
        continue

    print(f"[*] Downloading {item['name']} using node js-runtime...")
    cmd = [
        "/home/pavana/.local/bin/yt-dlp",
        "--js-runtimes", f"node:{NODE_PATH}",
        "-f", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best",
        "--download-sections", f"*{item['start']}-00:{int(item['start'].split(':')[1])+1}:00",
        "--force-keyframes-at-cuts",
        "-o", outpath,
        item["url"]
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if os.path.exists(outpath):
        print(f"[✓] Downloaded: {item['name']} ({os.path.getsize(outpath)} bytes)")
    else:
        print(f"[!] Failed {item['name']}: {res.stderr[:200]}")
