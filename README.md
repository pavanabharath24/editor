# Editor - Cash & Crown Documentary Video Engine

A specialized, modular motion graphics and video compositor engine designed for faceless financial documentaries, empire stories, and video essays matching the minimalist aesthetic of **assetmaxxing** and **Raiden Arc**.

---

## 🎨 Visual Aesthetic & Standards
- **Canvas**: Matte Black (`#080808` / `#000000`) with subtle analog film grain.
- **Color Hierarchy**:
  - **Gold (`#D4AF37`)**: Key metrics, wealth markers, focal hooks, and chapter numerals.
  - **Cyan (`#38BDF8`)**: Secondary emphasis, modern contrast, and transitions.
  - **White (`#F8FAFC`)**: High-contrast, clean sans-serif typography (Montserrat).
  - **Muted Gray (`#94A3B8`)**: Source citations, dates, subtext, and context.
- **Components**:
  - `ChapterBadge`: Signature top-left indicator (`[01] THE RISE`).
  - `StatCard`: High-impact metric callouts with rounded dark cards and subtle borders.
  - `KineticText`: Multi-colored emphasis captions.
  - `CutoutZoom`: Floating Ken Burns pan/zoom on cutouts with soft drop-shadows.

---

## 🚀 Quickstart

### 1. Requirements
- Python 3.10+
- FFmpeg
- Dependencies: `pillow`, `opencv-python`, `numpy`

```bash
pip install pillow opencv-python numpy
```

### 2. Render a Project Locally
```bash
python3 core/render_video.py --project projects/cash_and_crown/day1_rockstar --output output/day1_rockstar.mp4 --fps 60
```

### 3. Cloud Rendering with Kaggle
For fast rendering of long documentaries using cloud GPUs (NVIDIA T4):
```bash
cd kaggle
kaggle kernels push
```

---

## 📂 Project Structure
```
editor/
├── core/
│   ├── engine.py              # Motion graphics compositor & component library
│   └── render_video.py        # Timeline compiler & FFmpeg video pipeline
├── assets/
│   └── fonts/                 # Typography (Montserrat Bold, Black, Regular)
├── projects/
│   └── cash_and_crown/
│       └── day1_rockstar/     # Timeline definition and scene assets
└── kaggle/
    ├── kernel-metadata.json   # Cloud GPU configuration
    └── render_worker.py       # Cloud batch rendering worker
```
