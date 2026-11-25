#!/usr/bin/env python3
"""
Cash & Crown - Visual Diagram & Infographic Generators
Generates high-contrast animated diagrams matching reference documentary style:
1. Donut Chart (78% Recurrent Spending vs 22% Base Sales)
2. Revenue Bar Chart Growth ($800M Day One -> $1B Three Days)
3. 3-Column Risk Matrix (Cancelled -> Controversy -> Bugs)
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine import VideoStyle, get_font, DEFAULT_FONT_BLACK, DEFAULT_FONT_BOLD, DEFAULT_FONT_REGULAR, draw_rounded_rectangle

def create_donut_chart(percent=78, label="RECURRENT SPENDING", sublabel="Shark Cards, GTA+ & DLC", size=(1100, 520), progress=1.0):
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_rectangle(draw, (0, 0, w, h), radius=20, fill=(*VideoStyle.BADGE_BG, 240), outline=(*VideoStyle.BADGE_BORDER, 255), width=2)

    cx, cy = 250, h // 2
    radius = 150
    thickness = 34

    draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), start=0, end=360, fill=(45, 45, 55), width=thickness)

    sweep = int(360 * (percent / 100.0) * min(1.0, progress))
    if sweep > 0:
        draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), start=-90, end=-90 + sweep, fill=VideoStyle.ACCENT_GOLD, width=thickness)

    font_pct = get_font(DEFAULT_FONT_BLACK, 68)
    pct_text = f"{int(percent * min(1.0, progress))}%"
    bbox = font_pct.getbbox(pct_text)
    draw.text((cx - (bbox[2] - bbox[0]) // 2, cy - (bbox[3] - bbox[1]) // 2 - 10), pct_text, font=font_pct, fill=VideoStyle.ACCENT_GOLD)

    tx = 470
    font_title = get_font(DEFAULT_FONT_BLACK, 36)
    draw.text((tx, cy - 80), label, font=font_title, fill=VideoStyle.ACCENT_WHITE)

    font_sub = get_font(DEFAULT_FONT_BOLD, 22)
    draw.text((tx, cy - 25), sublabel, font=font_sub, fill=VideoStyle.ACCENT_CYAN)

    font_desc = get_font(DEFAULT_FONT_REGULAR, 18)
    draw.text((tx, cy + 25), "Take-Two Interactive FY2026 Net Bookings", font=font_desc, fill=VideoStyle.MUTED_GRAY)
    draw.text((tx, cy + 55), "Company-Wide Ecosystem Revenue Model", font=font_desc, fill=VideoStyle.MUTED_GRAY)

    return img


def create_growth_bars(day1=800, day3=1000, size=(1000, 520), progress=1.0):
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_rectangle(draw, (0, 0, w, h), radius=20, fill=(*VideoStyle.BADGE_BG, 240), outline=(*VideoStyle.BADGE_BORDER, 255), width=2)

    font_header = get_font(DEFAULT_FONT_BLACK, 32)
    draw.text((80, 45), "GLOBAL GTA V LAUNCH REVENUE (2013)", font=font_header, fill=VideoStyle.ACCENT_WHITE)

    bar1_w = 280
    max_h = 240
    b1_h = int((day1 / 1000.0) * max_h * min(1.0, progress))
    b1_x = 160
    b1_y = 380 - b1_h

    draw_rounded_rectangle(draw, (b1_x, b1_y, b1_x + bar1_w, 380), radius=12, fill=VideoStyle.ACCENT_GOLD)

    font_val = get_font(DEFAULT_FONT_BLACK, 40)
    v1_str = f"${int(day1 * min(1.0, progress))}M"
    bbox1 = font_val.getbbox(v1_str)
    draw.text((b1_x + (bar1_w - (bbox1[2] - bbox1[0])) // 2, b1_y - 50), v1_str, font=font_val, fill=VideoStyle.ACCENT_GOLD)

    font_lbl = get_font(DEFAULT_FONT_BOLD, 22)
    draw.text((b1_x + 85, 405), "DAY ONE", font=font_lbl, fill=VideoStyle.ACCENT_WHITE)

    bar2_w = 280
    b2_h = int((day3 / 1000.0) * max_h * min(1.0, progress))
    b2_x = 560
    b2_y = 380 - b2_h

    draw_rounded_rectangle(draw, (b2_x, b2_y, b2_x + bar2_w, 380), radius=12, fill=VideoStyle.ACCENT_CYAN)

    v2_str = f"${int(day3 * min(1.0, progress))/1000.0:.1f}B" if progress > 0.5 else "$0B"
    bbox2 = font_val.getbbox(v2_str)
    draw.text((b2_x + (bar2_w - (bbox2[2] - bbox2[0])) // 2, b2_y - 50), v2_str, font=font_val, fill=VideoStyle.ACCENT_CYAN)

    draw.text((b2_x + 70, 405), "FIRST 3 DAYS", font=font_lbl, fill=VideoStyle.ACCENT_WHITE)

    return img


def create_risk_matrix(size=(1080, 520), progress=1.0):
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_rectangle(draw, (0, 0, w, h), radius=20, fill=(*VideoStyle.BADGE_BG, 240), outline=(*VideoStyle.BADGE_BORDER, 255), width=2)

    font_title = get_font(DEFAULT_FONT_BLACK, 34)
    draw.text((60, 45), "THREE CATEGORIES OF RISK", font=font_title, fill=VideoStyle.ACCENT_GOLD)

    cols = [
        ("01. CANCELLED", "Agent (2009)", "Wasted Years of Dev", VideoStyle.ACCENT_CYAN),
        ("02. CONTROVERSY", "Manhunt & Bully", "Public Trust & Debates", VideoStyle.HIGHLIGHT_TAG),
        ("03. TECHNICAL", "Trilogy Remaster", "Reputation Damage", (239, 68, 68))
    ]

    card_w = 300
    for i, (head, sub1, sub2, col) in enumerate(cols):
        cx = 50 + i * 340
        cy = 130
        draw_rounded_rectangle(draw, (cx, cy, cx + card_w, cy + 320), radius=16, fill=(30, 30, 36), outline=col, width=2)

        font_h = get_font(DEFAULT_FONT_BOLD, 22)
        draw.text((cx + 20, cy + 30), head, font=font_h, fill=col)

        font_s1 = get_font(DEFAULT_FONT_BLACK, 26)
        draw.text((cx + 20, cy + 90), sub1, font=font_s1, fill=VideoStyle.ACCENT_WHITE)

        font_s2 = get_font(DEFAULT_FONT_REGULAR, 18)
        draw.text((cx + 20, cy + 180), sub2, font=font_s2, fill=VideoStyle.MUTED_GRAY)

    return img
