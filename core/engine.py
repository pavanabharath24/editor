#!/usr/bin/env python3
"""
Cash & Crown / Document Video Engine - Core Motion Graphics Compositor
Generates pure-black aesthetic documentary & video essay scenes:
- Minimalist matte black (#000000 / #0a0a0a) canvas with subtle film grain
- High-contrast subject cutouts with smooth floating Ken Burns pan/zoom and soft drop shadows
- Top-left chapter/progress counter badge ([01] TITLE)
- Clean modern typography with Gold (#D4AF37) / Cyan (#38BDF8) keyword highlights
- Stat callout cards ($8 Billion, 13 Years, 185M Copies)
- Split comparison & quote layout cards
- Smooth 60fps renders with audio sync (or silent with visual pacing)
"""

import os
import math
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import cv2

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
DEFAULT_FONT_BOLD = os.path.join(FONT_DIR, "Montserrat-Bold.otf")
DEFAULT_FONT_BLACK = os.path.join(FONT_DIR, "Montserrat-Black.otf")
DEFAULT_FONT_REGULAR = os.path.join(FONT_DIR, "Montserrat-Regular.otf")

if not os.path.exists(DEFAULT_FONT_BOLD):
    DEFAULT_FONT_BOLD = "/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Bold.otf"
    DEFAULT_FONT_BLACK = "/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Black.otf"
    DEFAULT_FONT_REGULAR = "/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Regular.otf"


class VideoStyle:
    BG_COLOR = (8, 8, 8)               # Deep matte black
    ACCENT_GOLD = (212, 175, 55)       # Luxury Cash & Crown Gold
    ACCENT_CYAN = (56, 189, 248)       # Electric Cyan / Modern Accent
    ACCENT_WHITE = (248, 250, 252)     # Crisp White Text
    MUTED_GRAY = (148, 163, 184)       # Subtitle / Details Gray
    BADGE_BG = (24, 24, 27)            # Dark Card Background
    BADGE_BORDER = (45, 45, 52)        # Subtle Border
    HIGHLIGHT_TAG = (234, 179, 8)       # Yellow/Gold tag


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def ease_out_cubic(x):
    return 1.0 - math.pow(1.0 - x, 3)


def draw_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


class SceneRenderer:
    def __init__(self, width=1920, height=1080, fps=60):
        self.width = width
        self.height = height
        self.fps = fps

    def render_chapter_badge(self, img, chapter_num, chapter_title, progress=1.0):
        """
        Renders signature top-left chapter indicator:
        [01] THE RISE OF ROCKSTAR
        """
        draw = ImageDraw.Draw(img)
        font_num = get_font(DEFAULT_FONT_BOLD, 22)
        font_title = get_font(DEFAULT_FONT_BOLD, 20)

        num_str = f"[{chapter_num:02d}]"
        title_str = chapter_title.upper()

        x, y = 80, 60
        draw.text((x, y), num_str, font=font_num, fill=VideoStyle.ACCENT_GOLD)
        
        bbox = font_num.getbbox(num_str)
        offset_x = x + (bbox[2] - bbox[0]) + 15
        draw.text((offset_x, y + 2), title_str, font=font_title, fill=VideoStyle.MUTED_GRAY)

    def render_kinetic_text(self, img, text_segments, y_pos=None, font_size=58, align="center"):
        """
        Renders multi-colored kinetic text where specific words are colored Gold/Cyan/White.
        text_segments: list of (word/phrase, color_tuple)
        """
        draw = ImageDraw.Draw(img)
        font = get_font(DEFAULT_FONT_BLACK, font_size)

        total_width = 0
        height = 0
        measured = []
        for text, color in text_segments:
            bbox = font.getbbox(text)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            measured.append((text, color, w, h))
            total_width += w
            height = max(height, h)

        if y_pos is None:
            y = (self.height - height) // 2 + 180
        else:
            y = y_pos

        if align == "center":
            start_x = (self.width - total_width) // 2
        else:
            start_x = 80

        curr_x = start_x
        for text, color, w, h in measured:
            draw.text((curr_x, y), text, font=font, fill=color)
            curr_x += w

    def render_stat_card(self, img, stat_value, stat_label, subtext="", card_x=None, card_y=None, card_w=640, card_h=340, alpha=1.0):
        """
        Renders clean documentary metric card:
        e.g. $8.5 BILLION | Global Grand Theft Auto Revenue
        """
        if card_x is None:
            card_x = (self.width - card_w) // 2
        if card_y is None:
            card_y = (self.height - card_h) // 2 - 40

        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        bg_color = (*VideoStyle.BADGE_BG, int(230 * alpha))
        border_color = (*VideoStyle.BADGE_BORDER, int(255 * alpha))
        draw_rounded_rectangle(draw, (card_x, card_y, card_x + card_w, card_y + card_h), radius=24, fill=bg_color, outline=border_color, width=2)

        font_stat = get_font(DEFAULT_FONT_BLACK, 76)
        stat_bbox = font_stat.getbbox(stat_value)
        stat_w = stat_bbox[2] - stat_bbox[0]
        stat_x = card_x + (card_w - stat_w) // 2
        draw.text((stat_x, card_y + 45), stat_value, font=font_stat, fill=(*VideoStyle.ACCENT_GOLD, int(255 * alpha)))

        font_label = get_font(DEFAULT_FONT_BOLD, 26)
        label_bbox = font_label.getbbox(stat_label)
        label_w = label_bbox[2] - label_bbox[0]
        label_x = card_x + (card_w - label_w) // 2
        draw.text((label_x, card_y + 160), stat_label, font=font_label, fill=(*VideoStyle.ACCENT_WHITE, int(255 * alpha)))

        if subtext:
            font_sub = get_font(DEFAULT_FONT_REGULAR, 18)
            sub_bbox = font_sub.getbbox(subtext)
            sub_w = sub_bbox[2] - sub_bbox[0]
            sub_x = card_x + (card_w - sub_w) // 2
            draw.text((sub_x, card_y + 215), subtext, font=font_sub, fill=(*VideoStyle.MUTED_GRAY, int(200 * alpha)))

        img.paste(Image.alpha_composite(img.convert("RGBA"), overlay), (0, 0))

    def composite_cutout(self, img, cutout_path, scale=1.0, pan_x=0, pan_y=0, drop_shadow=True):
        if not os.path.exists(cutout_path):
            return

        cutout = Image.open(cutout_path).convert("RGBA")
        new_w = int(cutout.width * scale)
        new_h = int(cutout.height * scale)
        cutout = cutout.resize((new_w, new_h), Image.Resampling.LANCZOS)

        pos_x = (self.width - new_w) // 2 + int(pan_x)
        pos_y = (self.height - new_h) // 2 + int(pan_y)

        if drop_shadow:
            shadow = Image.new("RGBA", (new_w + 60, new_h + 60), (0, 0, 0, 0))
            shadow_mask = cutout.split()[3].resize((new_w, new_h))
            shadow_core = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 180))
            shadow.paste(shadow_core, (30, 30), mask=shadow_mask)
            shadow = shadow.filter(ImageFilter.GaussianBlur(25))
            img.paste(shadow, (pos_x - 30, pos_y - 20), mask=shadow)

        img.paste(cutout, (pos_x, pos_y), mask=cutout)


def create_blank_canvas(width=1920, height=1080, grain=True):
    base = Image.new("RGB", (width, height), VideoStyle.BG_COLOR)
    if grain:
        noise = np.random.normal(0, 3.0, (height, width)).astype(np.int16)
        arr = np.array(base, dtype=np.int16)
        arr = np.clip(arr + noise[:, :, np.newaxis], 0, 255).astype(np.uint8)
        base = Image.fromarray(arr)
    return base

def render_pip_video(canvas, video_frame, logo_path=None, size=(460, 260), pos=(1380, 70), border_color=(212, 175, 55)):
    """
    Renders picture-in-picture video window in the upper-right corner with:
    - Rounded corners and sleek glowing border
    - Associated game franchise logo badge in corner of the PIP
    """
    w, h = size
    x, y = pos

    # Resize video frame to PIP window
    pip_img = Image.fromarray(video_frame).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)

    # Rounded mask
    mask = Image.new("L", (w, h), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, w, h), radius=16, fill=255)

    # Border overlay
    border = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    draw_b = ImageDraw.Draw(border)
    draw_b.rounded_rectangle((0, 0, w + 7, h + 7), radius=18, fill=None, outline=(*border_color, 255), width=3)

    # Paste border and PIP
    canvas.paste(border, (x - 4, y - 4), mask=border)
    canvas.paste(pip_img, (x, y), mask=mask)

    # Optional game logo badge at the bottom-right or top-left of PIP
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_w = int(w * 0.35)
        logo_h = int(logo.height * (logo_w / float(logo.width)))
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        # Position at bottom right of PIP
        canvas.paste(logo, (x + w - logo_w - 12, y + h - logo_h - 12), mask=logo)

def render_center_retro_clip(canvas, video_frame, logo_path=None, size=(960, 720), pos=None, border_color=(212, 175, 55)):
    """
    Renders 4:3 aspect ratio gameplay clip in the center of the 16:9 canvas with:
    - Elegant rounded border
    - Associated game logo floating on the top-left corner of the 4:3 clip (overlapping the border)
    """
    cw, ch = size
    if pos is None:
        # Perfectly centered horizontally, slightly raised to give room for bottom captions
        cx = (canvas.width - cw) // 2
        cy = (canvas.height - ch) // 2 - 50
    else:
        cx, cy = pos

    # Resize frame to 4:3
    clip_img = Image.fromarray(video_frame).convert("RGBA").resize((cw, ch), Image.Resampling.LANCZOS)

    # Rounded clip mask
    mask = Image.new("L", (cw, ch), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, cw, ch), radius=20, fill=255)

    # Elegant outer border
    border = Image.new("RGBA", (cw + 12, ch + 12), (0, 0, 0, 0))
    draw_b = ImageDraw.Draw(border)
    draw_b.rounded_rectangle((0, 0, cw + 11, ch + 11), radius=24, fill=None, outline=(*border_color, 255), width=4)

    # Paste border and video
    canvas.paste(border, (cx - 6, cy - 6), mask=border)
    canvas.paste(clip_img, (cx, cy), mask=mask)

    # Game logo on the top-left corner border of the 4:3 clip
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_w = 260
        logo_h = int(logo.height * (logo_w / float(logo.width)))
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Position logo sitting across top-left corner
        lx = cx - 25
        ly = cy - (logo_h // 2) - 10
        canvas.paste(logo, (lx, ly), mask=logo)
