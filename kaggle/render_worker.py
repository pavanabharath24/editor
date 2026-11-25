#!/usr/bin/env python3
"""
Cash & Crown Kaggle Cloud GPU Batch Renderer
Renders full 5-minute 1080p 60fps documentary scenes using Kaggle Cloud GPU / Multi-core vCPU.
"""

import os
import sys
import subprocess

def main():
    print("[+] Starting Cash & Crown Kaggle Cloud Render Worker (Full 5-Min Video)")
    
    # 1. Clone repository
    work_dir = "/kaggle/working/editor"
    if os.path.exists(work_dir):
        subprocess.run(["git", "pull"], cwd=work_dir, check=False)
    else:
        subprocess.run(["git", "clone", "https://github.com/pavanabharath24/editor.git", work_dir], check=True)

    # 2. Install dependencies
    subprocess.run(["pip", "install", "-q", "pillow", "opencv-python-headless", "numpy"], check=True)

    # 3. Execute full 5-minute video render
    project_dir = os.path.join(work_dir, "projects", "cash_and_crown", "day1_rockstar")
    output_video = "/kaggle/working/day1_rockstar_5min.mp4"
    render_script = os.path.join(work_dir, "core", "render_video.py")
    
    cmd = [
        sys.executable, render_script,
        "--project", project_dir,
        "--output", output_video,
        "--fps", "30"
    ]
    print(f"[+] Launching Render: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"[✓] Successfully generated full video: {output_video}")

if __name__ == "__main__":
    main()

