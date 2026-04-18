# 🤖 SmartGrasp - Robot Cup Detection & Grasping System

> **Real-time cup detection with C-shaped handle recognition for robotic manipulation**

## 📋 Overview

SmartGrasp is a complete system for detecting cups and their handles in images, then providing safe grasping instructions for robots. The system uses OpenCV for fast detection and provides both a web interface and command-line tools.

**Key Features:**
- ✅ Real-time cup and handle detection
- ✅ Web interface for image upload (file & URL)
- ✅ Web scraping for training data collection
- ✅ Interactive annotation tool for dataset labeling
- ✅ Robot accuracy evaluation metrics
- ✅ Data-driven optimization workflow

---

## 📁 Project Structure

```
SmartGrasp/
├── core/                        # Core modules
│   ├── smartgrasp.py           # Cup detection engine
│   └── server.py               # Flask REST API
│
├── tools/                       # Training & analysis tools
│   ├── web_scraper.py          # Download cup images
│   ├── annotator.py            # Manual image labeling
│   ├── dataset_manager.py      # Evaluation metrics
│   └── train.py                # Master launcher menu
│
├── web/                         # Web interface
│   └── templates/
│       └── upload.html         # Flask HTML template
│
├── dataset/                     # Training data
│   ├── raw_images/             # Downloaded cup images
│   └── annotations/            # Ground truth labels
│
├── data/                        # Analysis outputs
│   └── preprocessing_debug/    # Debug visualizations
│
├── results/                     # Processing results
│   └── screenshots/            # Visualization images
│
├── docs/                        # Documentation
│   └── TRAINING_WORKFLOW.md
│
├── README.md                    # This file
├── requirements.txt             # Dependencies
└── uploads/                     # Temporary uploads
```

---

## 🚀 Quick Start

### 1️⃣ Installation

```bash
# Clone/enter project directory
cd SmartGrasp

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Launch Web Server

```bash
cd core
python server.py
```

**Access at:** `http://127.0.0.1:5000`

Upload images via:
- 📁 **File Upload** - Drag & drop local images
- 🌐 **URL Upload** - Paste image web links

### 3️⃣ Train on Custom Data (Optional)

```bash
cd tools
python train.py
```

**Menu options:**
1. Download cup images from internet
2. Manually annotate cup & handle positions
3. Evaluate robot accuracy on dataset
4. View training workflow help

---

## 📚 How It Works

### Detection Pipeline

```
Input Image
    ↓
Preprocessing (threshold, morphology, distance transform)
    ↓
Contour extraction
    ↓
Cup detection (largest contour)
    ↓
Handle detection (secondary contours)
    ↓
Grasp position calculation
    ↓
Output: 🟢 Cup box + 🔵 Handle box + 🔴 Gripper position
```

### Key Algorithms

| Component | Algorithm | Purpose |
|-----------|-----------|---------|
| **Preprocessing** | Binary thresholding + Morphology | Noise removal, object separation |
| **Segmentation** | Contour detection + Distance transform | Find cup and handle regions |
| **Classification** | Size & position filtering | Distinguish cup from handle |
| **Grasping** | Center-of-mass calculation | Safe robot gripper placement |

---

## 🎯 Using the Web Interface

### File Upload

1. Open http://127.0.0.1:5000
2. Click upload area or drag image
3. Wait for processing (~1-2 seconds)
4. View results with annotations:
   - 🟢 **Green box** = Cup body
   - 🔵 **Blue box** = C-shaped handle
   - 🔴 **Red crosshair** = Robot gripper position

### URL Upload

1. Click "Upload from URL" tab
2. Paste image URL (e.g., https://example.com/cup.jpg)
3. Click "Process from URL"
4. View results

### Response Format

```json
{
  "success": true,
  "filename": "image.jpg",
  "grasp_image": "/results/..../grasp_visualization.jpg",
  "analysis": {
    "object": "cup",
    "has_handle": true,
    "cup_bbox": [200, 150, 350, 400],
    "handle_bbox": [340, 200, 390, 350],
    "grasp_type": "handle_center",
    "confidence": 0.85
  },
  "pose": [275, 275, 0.15]
}
```

---

## 🧠 Training Your Own Model

### Complete Training Workflow

```bash
cd tools
python train.py
```

**Step-by-step:**

#### Step 1: Collect Data
```bash
Menu [1] → Download cup images
```
- Scrapes Unsplash & Pexels
- Downloads ~30-50 real-world cup photos
- Saves to: `dataset/raw_images/`

#### Step 2: Label Data
```bash
Menu [2] → Annotate images
```
- Interactive GUI opens
- For each image:
  - Press `[C]` → Draw rectangle around cup body
  - Press `[H]` → Draw rectangle around handle
  - Press `[S]` → Save and next
  - Press `[Q]` → Skip
- Outputs: `dataset/annotations/*.json`

#### Step 3: Evaluate
```bash
Menu [3] → Evaluate robot
```
- Tests robot on your labeled dataset
- Calculates **IoU** (Intersection over Union) accuracy
- Shows which images are detected well
- Outputs: `evaluation_results.xlsx`

#### Step 4: Improve

**If accuracy is low:**

1. Open `core/smartgrasp.py`
2. Find line ~85 (threshold value):
   ```python
   _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
   # Try: 100, 120, 150, 180
   ```
3. Adjust and re-evaluate
4. Iterate until IoU > 0.85

---

## 📊 Understanding Evaluation Results

### evaluation_results.xlsx

| filename | type | iou | detected |
|----------|------|-----|----------|
| mug_1.jpg | cup | 0.923 | True |
| mug_1.jpg | handle | 0.856 | True |
| mug_2.jpg | cup | 0.654 | True |
| mug_2.jpg | handle | 0.412 | True |

**Interpretation:**
- **IoU = 1.0** → Perfect detection ✅
- **IoU = 0.8+** → Good detection 🟢
- **IoU = 0.5-0.8** → Fair detection 🟡
- **IoU < 0.5** → Poor detection 🔴

**Action items:**
- Low cup IoU? → Adjust binary threshold
- Low handle IoU? → Adjust morphological kernel
- No detection? → Review ground truth labels

---

## 🔧 Core Module API

### BatchSmartGrasp Class

```python
from core.smartgrasp import BatchSmartGrasp

processor = BatchSmartGrasp()

# Process single image
result = processor.process_image('path/to/image.jpg')
# Returns: {
#   'status': 'success',
#   'image_path': '...',
#   'analysis': {...},
#   'pose': [x, y, z],
#   'width': gripper_width
# }

# Batch process folder
processor.batch_process('images/')
```

### Detection Output

```python
analysis = processor.analyze_object('image.jpg')
# Returns:
{
    'object': 'cup',
    'has_handle': True/False,
    'cup_bbox': (x1, y1, x2, y2),      # Green box
    'handle_bbox': (x1, y1, x2, y2),   # Blue box
    'handle_center': (x, y),            # Handle center point
    'grasp_type': 'handle_center' | 'body_center',
    'confidence': 0.0-1.0
}
```

---

## 🌐 REST API Endpoints

### `POST /upload`
Upload image file directly
```bash
curl -F "file=@image.jpg" http://127.0.0.1:5000/upload
```

### `POST /upload-url`
Upload image from URL
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/image.jpg"}' \
  http://127.0.0.1:5000/upload-url
```

### `GET /`
Web interface

### `GET /results`
Get last 10 results

---

## 📦 Dependencies

```
opencv-python >= 4.5.0
Flask >= 3.0.0
Pillow >= 9.0.0
pandas >= 1.3.0
numpy >= 1.20.0
requests >= 2.28.0
beautifulsoup4 >= 4.11.0
Werkzeug >= 2.0.0
```

**Install all:**
```bash
pip install -r requirements.txt
```

---

## 🎨 Customization

### Change Detection Threshold

In `core/smartgrasp.py` line 85:
```python
# Try values: 100, 127 (default), 150, 180
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
```

### Change Morphological Kernel

Lines 89-92:
```python
# Try sizes: (3,3), (5,5) default, (7,7)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
```

### Change Handle Size Ratio

Line 158:
```python
# Default: 5-70% of cup size
# Try: (0.05, 0.6) or (0.1, 0.5)
if not (0.05 < size_ratio < 0.7):
    continue
```

---

## 🐛 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Server won't start | Port 5000 in use | Change port in `core/server.py` line 58 |
| Images not uploading | File too large | Check `MAX_CONTENT_LENGTH` in `core/server.py` |
| Wrong detection | Poor threshold value | Adjust threshold (100-180 range) in `core/smartgrasp.py` |
| No handle detected | Handle colors too similar | Try lower threshold value or adjust kernel size |
| Slow processing | First run (caches) | Subsequent runs are faster (~1-2 sec) |

---

## 📖 Full Documentation

- **[TRAINING_WORKFLOW.md](docs/TRAINING_WORKFLOW.md)** - Complete training guide
- **[API Reference](#-rest-api-endpoints)** - REST endpoint details
- **[Code Examples](#core-module-api)** - Usage examples

---

## 🚀 Advanced Usage

### Command-line Batch Processing

```bash
cd core
python smartgrasp.py  # Processes all images in 'uploads/' folder
```

### Run Web Scraper

```bash
cd tools
python web_scraper.py  # Downloads 30 cup images
```

### Annotate Images

```bash
cd tools
python annotator.py  # Interactive annotation GUI
```

### Evaluate Dataset

```bash
cd tools
python dataset_manager.py  # Calculates accuracy metrics
```

---

## 📈 Performance Metrics

**Baseline Performance** (after training on 30+ images):

| Metric | Target | Typical |
|--------|--------|---------|
| Cup IoU | > 0.85 | 0.88 |
| Handle IoU | > 0.80 | 0.82 |
| Processing Speed | < 2 sec | ~1.5 sec |
| Memory Usage | < 500MB | ~300MB |

---

## 💡 Tips for Best Results

✅ **Do:**
- Use 50+ training images (variety is key)
- Include different lighting, angles, colors
- Label ground truth carefully
- Validate on new images not in training set
- Save detected images to review failures

❌ **Don't:**
- Use < 10 training images
- Over-adjust threshold (0 or 255)
- Inconsistent annotation box sizes
- Skip validation step

---

## 🤝 Contributing

Issues or improvements? Create a GitHub issue or PR!

---

## 📝 License

MIT License - Feel free to use for research or commercial projects.

---

## 📞 Support

**Getting started?**
- Start with Quick Start section
- Run `python tools/train.py` for interactive menu

**Need help?**
- Check Troubleshooting section
- Review code comments in `core/smartgrasp.py`
- Check Flask logs in terminal

---

**Happy grasping! 🤖☕**
