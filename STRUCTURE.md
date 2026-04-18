```
SmartGrasp/  (Root Directory)
│
├── 📚 README.md                          ← Start here!
├── 📄 requirements.txt                   ← pip install -r requirements.txt
│
│
├── 🔧 core/                              ← Core detection & server modules
│   ├── smartgrasp.py                    (Cup detection algorithm)
│   └── server.py                        (Flask REST API, localhost:5000)
│
├── 🛠️  tools/                             ← Training & analysis tools
│   ├── train.py                         (Master launcher menu) ← RUN THIS!
│   ├── web_scraper.py                   (Download images from Unsplash/Pexels)
│   ├── annotator.py                     (Interactive image labeling)
│   └── dataset_manager.py               (Evaluate robot accuracy)
│
├── 🌐 web/                               ← Web interface
│   └── templates/
│       └── upload.html                  (Flask UI: file & URL upload)
│
├── 📊 dataset/                           ← Training data
│   ├── raw_images/                      (Downloaded cup photos)
│   │   ├── unsplash_*.jpg              (Images from web scraper)
│   │   └── pexels_*.jpg                (Images from web scraper)
│   │
│   └── annotations/                     (Ground truth labels)
│       ├── manifest.json                (Index of all annotations)
│       ├── unsplash_abc123.json        (Individual image annotations)
│       └── evaluation_results.xlsx      (Robot accuracy metrics)
│
├── 📈 data/                              ← Analysis outputs
│   └── preprocessing_debug/             (Debug visualization images)
│       ├── 01_original.jpg
│       ├── 02_threshold_127.jpg
│       ├── 03_morphological_open.jpg
│       ├── 04_morphological_close.jpg
│       ├── 05_distance_transform.jpg
│       ├── 06_all_contours.jpg
│       ├── 07_large_contours.jpg
│       └── 08_annotated_boxes.jpg
│
├── 📸 results/                           ← Processing output images
│   └── screenshots/                     (Visualization images)
│       └── 20260418_120530_image/
│           ├── grasp_visualization.jpg  (Final annotated image)
│           └── analysis.json            (Detection results JSON)
│
├── 📁 uploads/                           ← Temporary uploaded files
│   └── (temporary image files)
│
├── 📖 docs/                              ← Documentation
│   └── TRAINING_WORKFLOW.md             (Complete training guide)
│
└── .venv/                                ← Python virtual environment
    ├── Scripts/
    │   ├── python.exe
    │   └── activate.bat
    └── Lib/
        └── site-packages/               (Installed packages)
```

---

## 🚀 QUICK START GUIDE

### First Time Setup

```bash
# 1. Create virtual environment
cd SmartGrasp
python -m venv .venv
.venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch web server
cd core
python server.py
# Visit: http://127.0.0.1:5000
```

### Use the Web Interface

```
1. Open http://127.0.0.1:5000 in browser
2. Choose: File Upload OR URL Upload
3. Get results with:
   - 🟢 Green box = Cup
   - 🔵 Blue box = Handle
   - 🔴 Red crosshair = Gripper position
```

### Train on Custom Data

```bash
# Run interactive menu
cd tools
python train.py

# Menu options:
# [1] Download cup images (web scraping)
# [2] Manually annotate images (ground truth)
# [3] Evaluate robot accuracy (IoU metrics)
# [4] View workflow help
# [5] Check dataset progress
```

---

## 📋 FILE DESCRIPTIONS

### Core Modules (core/)

**smartgrasp.py**
- Main detection algorithm
- `BatchSmartGrasp` class - handles image processing
- Methods:
  - `process_image()` - Process single image
  - `analyze_object()` - Detect cup & handle
  - `detect_handle_fallback()` - OpenCV-based detection
  - `precise_grasp()` - Calculate gripper position
  - `visualize_precise()` - Draw boxes and crosshair
  - `batch_process()` - Process folder of images

**server.py**
- Flask REST API server
- Routes:
  - `GET /` - Web interface
  - `POST /upload` - File upload
  - `POST /upload-url` - URL upload
  - `GET /results` - Get recent results
- Configuration:
  - Host: 127.0.0.1
  - Port: 5000
  - Max file size: 50MB

### Tools (tools/)

**train.py**
- Interactive menu launcher
- Run all tools from one place
- Shows dataset status
- Main entry point for training workflow
- **START HERE for training**

**web_scraper.py**
- Downloads cup images from:
  - Unsplash (high quality)
  - Pexels (free images)
- Creates: `dataset/raw_images/`
- Usage: `python web_scraper.py`

**annotator.py**
- Interactive image labeling tool
- GUI for marking cup & handle regions
- Creates: `dataset/annotations/*.json`
- Usage: `python annotator.py`

**dataset_manager.py**
- Evaluates robot on labeled dataset
- Calculates IoU (Intersection over Union) scores
- Creates: `evaluation_results.xlsx`
- Usage: `python dataset_manager.py`

### Documentation (docs/)

**TRAINING_WORKFLOW.md**
- Complete step-by-step training guide
- How to download images
- How to annotate images
- How to evaluate accuracy
- How to improve detection
- Troubleshooting tips

---

## 🎯 TYPICAL WORKFLOW

```
START HERE
    ↓
1. Run: python tools/train.py
    ↓
2. [1] Download images (~30 cups)
    ↓ (Automatic - takes ~3 min)
3. [2] Annotate images (mark cup & handle)
    ↓ (Manual - ~10 minutes)
4. [3] Evaluate robot (IoU accuracy)
    ↓ (Automatic - ~2 min)
5. Review: evaluation_results.xlsx
    ↓
6. If IoU > 0.85: ✅ DONE
   If IoU < 0.85: → Edit smartgrasp.py thresholds
                     → Go back to step [3]
    ↓
7. Deploy: Run server.py and use web interface
```

---

## 💾 DATA FLOW

```
Web Scraper
    ↓
Raw Images (JPEG)
    ↓
Annotation Tool (GUI)
    ↓
Ground Truth Labels (JSON)
    ↓
Dataset Manager
    ↓
Evaluation Results (XLSX)
    ↓
Metrics (IoU, Accuracy)
    ↓
[Improve Detection?]
    ↓ No → Deploy to Production
    ↓ Yes → Edit smartgrasp.py → Re-evaluate
```

---

## 🔑 KEY DIRECTORIES

| Directory | Purpose | Contains |
|-----------|---------|----------|
| `core/` | Detection engine | smartgrasp.py, server.py |
| `tools/` | Training tools | train.py, annotator.py, web_scraper.py |
| `web/` | Web interface | upload.html template |
| `dataset/raw_images/` | Downloaded images | JPEG files from internet |
| `dataset/annotations/` | Ground truth labels | JSON files + manifest.json |
| `results/` | Processing outputs | Annotated images + JSON |
| `docs/` | Documentation | TRAINING_WORKFLOW.md |
| `uploads/` | Temporary files | User uploaded images |

---

## 📌 IMPORTANT FILES

**To modify detection parameters:**
- Edit: `core/smartgrasp.py`
- Line 85: Binary threshold (default: 127)
- Line 89: Morphological kernel (default: 5×5)
- Line 158: Handle size ratio (default: 0.05-0.7)

**To see accuracy results:**
- File: `dataset/annotations/evaluation_results.xlsx`
- Open in Excel and sort by `iou` column

**To start training:**
- Run: `cd tools && python train.py`
- Follow interactive menu

---

## ✅ CHECKLIST

- [ ] Created `.venv` directory
- [ ] Installed packages: `pip install -r requirements.txt`
- [ ] Started server: `python core/server.py`
- [ ] Accessed web interface: `http://127.0.0.1:5000`
- [ ] Tested file upload
- [ ] Tested URL upload
- [ ] Run training menu: `python tools/train.py`
- [ ] Downloaded images with web_scraper
- [ ] Annotated images with annotator
- [ ] Evaluated with dataset_manager
- [ ] Reviewed `evaluation_results.xlsx`

---

**You're all set! Start with the README.md and follow the Quick Start section.** 🚀
