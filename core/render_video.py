#!/usr/bin/env python3
"""
Cash & Crown / Document Video Engine - Video Timeline Builder & Renderer
Reads scene timeline definition JSON and generates full 60fps MP4 video.
Features live progress tracking file (.progress.json) for dashboard updates.
"""

import os
import sys
import json
import math
import argparse
import subprocess
import cv2
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine import SceneRenderer, VideoStyle, create_blank_canvas, ease_out_cubic, smoothstep


def parse_color(color_name):
    lookup = {
        "gold": VideoStyle.ACCENT_GOLD,
        "cyan": VideoStyle.ACCENT_CYAN,
        "white": VideoStyle.ACCENT_WHITE,
        "gray": VideoStyle.MUTED_GRAY,
        "yellow": VideoStyle.HIGHLIGHT_TAG
    }
    return lookup.get(color_name.lower(), VideoStyle.ACCENT_WHITE)


def get_best_encoder():
    try:
        res = subprocess.run(["ffmpeg", "-encoders"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out = res.stdout + res.stderr
        if "h264_nvenc" in out:
            test_res = subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "nullsrc=s=64x64:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if test_res.returncode == 0:
                return "h264_nvenc"
        if "libx264" in out:
            return "libx264"
        if "libopenh264" in out:
            return "libopenh264"
    except Exception:
        pass
    return "libopenh264"


def update_progress(progress_file, status, percent, current_scene, total_scenes, current_frame, total_frames, eta_seconds=0):
    try:
        data = {
            "status": status,
            "percent": round(percent, 1),
            "current_scene": current_scene,
            "total_scenes": total_scenes,
            "current_frame": current_frame,
            "total_frames": total_frames,
            "eta_seconds": int(eta_seconds)
        }
        with open(progress_file, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def render_timeline(project_dir, output_path, resolution=(1920, 1080), fps=30):
    timeline_file = os.path.join(project_dir, "timeline.json")
    if not os.path.exists(timeline_file):
        raise FileNotFoundError(f"Timeline not found: {timeline_file}")

    progress_file = os.path.join(project_dir, ".progress.json")
    update_progress(progress_file, "Initializing", 0, 0, 0, 0, 0)

    with open(timeline_file, "r") as f:
        data = json.load(f)

    title = data.get("title", "Cash & Crown Documentary")
    scenes = data.get("scenes", [])
    width, height = resolution
    renderer = SceneRenderer(width=width, height=height, fps=fps)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    temp_raw_video = output_path + ".temp.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_raw_video, fourcc, fps, (width, height))

    total_duration = sum(s.get("duration", 4.0) for s in scenes)
    total_frames = int(total_duration * fps)

    print(f"[+] Starting Render: {title}")
    print(f"[+] Output: {output_path} | Resolution: {width}x{height} @ {fps}fps")
    print(f"[+] Duration: {total_duration:.1f}s | Total Frames: {total_frames}")

    frames_rendered = 0
    start_time = cv2.getTickCount()

    for scene_idx, scene in enumerate(scenes):
        duration = scene.get("duration", 4.0)
        scene_frames = int(duration * fps)
        chapter_num = scene.get("chapter_num", 1)
        chapter_title = scene.get("chapter_title", "Cash & Crown")
        scene_type = scene.get("type", "stat")

        print(f"    -> Rendering Scene {scene_idx+1}/{len(scenes)}: [{scene_type}] {chapter_title} ({duration}s, {scene_frames} frames)")

        text_segments = []
        for seg in scene.get("text", []):
            word = seg.get("word", "")
            color = parse_color(seg.get("color", "white"))
            text_segments.append((word, color))

        stat_value = scene.get("stat_value", "")
        stat_label = scene.get("stat_label", "")
        stat_sub = scene.get("stat_subtext", "")

        cutout_rel = scene.get("cutout_image", "")
        cutout_path = os.path.join(project_dir, cutout_rel) if cutout_rel else ""

        for frame_idx in range(scene_frames):
            t = frame_idx / float(max(1, scene_frames - 1))
            
            canvas = create_blank_canvas(width, height, grain=True)
            renderer.render_chapter_badge(canvas, chapter_num, chapter_title)

            if scene_type == "stat":
                scale_anim = 0.96 + 0.04 * ease_out_cubic(min(1.0, t * 2.5))
                card_alpha = min(1.0, t * 3.0)
                renderer.render_stat_card(canvas, stat_value, stat_label, subtext=stat_sub, alpha=card_alpha)

            elif scene_type == "cutout" and os.path.exists(cutout_path):
                zoom = 1.0 + 0.08 * t
                pan_y = -15 * t
                renderer.composite_cutout(canvas, cutout_path, scale=zoom, pan_y=pan_y)

            if text_segments:
                y_offset = int(180 - 15 * ease_out_cubic(min(1.0, t * 2.0)))
                renderer.render_kinetic_text(canvas, text_segments, y_pos=(height // 2 + y_offset), font_size=52)

            frame_np = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
            out.write(frame_np)
            frames_rendered += 1

            if frames_rendered % 15 == 0 or frames_rendered == total_frames:
                pct = (frames_rendered / float(total_frames)) * 95.0
                elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                fps_rate = frames_rendered / max(0.1, elapsed)
                eta = (total_frames - frames_rendered) / max(0.1, fps_rate)
                update_progress(progress_file, "Rendering Frames", pct, scene_idx + 1, len(scenes), frames_rendered, total_frames, eta)

    out.release()

    encoder = get_best_encoder()
    print(f"[+] Finalizing compression using {encoder}...")
    update_progress(progress_file, "Finalizing MP4 Compression", 97.0, len(scenes), len(scenes), total_frames, total_frames, 5)

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", temp_raw_video,
        "-c:v", encoder,
        "-pix_fmt", "yuv420p", output_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    if os.path.exists(temp_raw_video):
        os.remove(temp_raw_video)

    update_progress(progress_file, "Completed", 100.0, len(scenes), len(scenes), total_frames, total_frames, 0)
    print(f"[✓] Render Complete: {output_path} ({frames_rendered} frames)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Cash & Crown Video")
    parser.add_argument("--project", required=True, help="Path to project directory with timeline.json")
    parser.add_argument("--output", required=True, help="Output MP4 file path")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default 30)")
    args = parser.parse_args()

    render_timeline(args.project, args.output, fps=args.fps)
