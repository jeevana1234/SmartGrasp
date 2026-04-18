# 🤖 SmartGrasp - Complete Robot Training Workflow

## Overview
This system teaches your robot to **correctly detect cup bodies and C-shaped handles** through a data-driven approach:

1. **Web Scraping** - Download real cup images from internet
2. **Annotation** - Manually label cup & handle positions 
3. **Evaluation** - Test robot accuracy on labeled dataset
4. **Iteration** - Improve detection based on results

---

## 📋 Step-by-Step Workflow

### Step 1: Download Cup Images
```bash
cd tools
python train.py
# Select menu [1]
```

**What it does:**
- Scrapes Unsplash & Pexels for cup images
- Downloads 30+ real-world cup photos
- Saves to: `../dataset/raw_images/`

**Output:**
```
dataset/raw_images/
├── unsplash_abc123.jpg   (coffee mug with handle)
├── unsplash_def456.jpg   (ceramic cup with handle)
├── pexels_0.jpg          (tea cup)
└── ...
```

---

### Step 2: Annotate Images (Label Cup & Handle)
```bash
cd tools
python train.py
# Select menu [2]
```

**Interactive GUI:**
1. Image appears on screen
2. Press `C` then drag rectangle around **CUP BODY** (green box)
3. Press `H` then drag rectangle around **HANDLE** (blue box)
4. Press `S` to save and next image
5. Press `Q` to skip

**Example:**
```
CUP BODY (GREEN):        [200, 150, 350, 400]  ← Cylindrical part
HANDLE (BLUE):           [340, 200, 390, 350]  ← C-shaped part
```

**Output:**
```
dataset/annotations/
├── unsplash_abc123.json  (annotation for image 1)
├── unsplash_def456.json  (annotation for image 2)
├── manifest.json         (index of all annotations)
└── ...
```

manifest.json example:
```json
[
  {
    "filename": "unsplash_abc123.jpg",
    "image_path": "/path/to/image.jpg",
    "cup_bbox": [200, 150, 350, 400],
    "handle_bbox": [340, 200, 390, 350]
  },
  ...
]
```

---

### Step 3: Evaluate Robot Accuracy
```bash
cd tools
python train.py
# Select menu [3]
```

**What it does:**
1. Loads all annotated images
2. Runs robot detection on each
3. Compares detected boxes vs. ground truth
4. Calculates **IoU (Intersection over Union)** score

**Metrics:**
- **IoU = 1.0** → Perfect detection ✅
- **IoU = 0.7+** → Good detection 🟢
- **IoU = 0.5-0.7** → Fair detection 🟡
- **IoU < 0.5** → Needs improvement 🔴

**Console Output:**
```
🤖 Evaluating robot on 30 images...
==================================================

[1/30] mug_1.jpg
   Cup IoU: 0.923
   Handle IoU: 0.856

[2/30] mug_2.jpg
   Cup IoU: 0.654
   Handle IoU: 0.412

...

==================================================
📊 EVALUATION RESULTS
==================================================
🏆 Cup Detection:
   Mean IoU: 0.823 (±0.115)
   Min: 0.652, Max: 0.956

🏆 Handle Detection:
   Mean IoU: 0.756 (±0.142)
   Min: 0.512, Max: 0.921

Results saved to: ../dataset/annotations/evaluation_results.xlsx
```

---

## 📊 Understanding Results

### Excel Output: evaluation_results.xlsx
| filename | type | iou | detected | error |
|----------|------|-----|----------|-------|
| mug_1.jpg | cup | 0.923 | True | null |
| mug_1.jpg | handle | 0.856 | True | null |
| mug_2.jpg | cup | 0.654 | True | null |
| mug_2.jpg | handle | 0.412 | True | null |

**Read as:**
- **mug_1.jpg**: Excellent cup detection (0.923), good handle (0.856) ✅
- **mug_2.jpg**: Weak handle detection (0.412) - needs improvement ⚠️

### Identifying Problem Images

1. Open `evaluation_results.xlsx`
2. Sort by `iou` column (ascending)
3. Focus on images with IoU < 0.5
4. Check those images in `dataset/raw_images/`
5. Analyze what's different about them

---

## 🔧 How to Improve Accuracy

If handle IoU is low (< 0.6):

### Problem 1: Handle not detected
- **Cause**: Colors too similar to cup, threshold doesn't separate them
- **Solution**: Adjust binary threshold in `core/smartgrasp.py` line 85
  
  ```python
  # Line 85:
  _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
  #                                 ^^^
  # Try different values: 100, 120, 130, 150, 180
  # Lower = more white (more objects detected)
  # Higher = less white (fewer objects detected)
  ```

### Problem 2: Handle box too large or too small
- **Cause**: Morphological operations too aggressive or weak
- **Solution**: Adjust kernel size in `core/smartgrasp.py` lines 88-92
  
  ```python
  # Line 89:
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
  #                                                     ^^^^ kernel size
  # Try: (3,3) = less aggressive
  #      (5,5) = default
  #      (7,7) = more aggressive
  ```

### Problem 3: Wrong object detected (not separating cup & handle)
- **Cause**: Size ratios need tuning
- **Solution**: Adjust size filter in `core/smartgrasp.py` line 158
  
  ```python
  # Line 158:
  if not (0.05 < size_ratio < 0.7):
  #       ^^^^ min ratio ^^^^ max ratio
  # Default: Handle is 5-70% of cup size
  # Try: (0.05, 0.6) or (0.1, 0.5) or (0.08, 0.65)
  ```

### Problem 4: Position-based filtering not working
- **Cause**: Handle position thresholds too strict
- **Solution**: Adjust position check in `core/smartgrasp.py` line 164-176
  
  ```python
  # The code checks:
  # - Is handle positioned beside cup? (left/right)
  # - Is handle positioned below cup?
  # - Is handle NOT completely inside cup?
  # 
  # These should be loose enough to catch all valid handles
  ```

---

## 📈 Training Workflow (Iteration)

1. **Initial Run**: 
   - Scrape 30 images
   - Annotate them
   - Evaluate (baseline accuracy)

2. **First Iteration**:
   - Check evaluation_results.xlsx
   - Identify lowest IoU images
   - Make ONE parameter change (e.g., threshold 127 → 120)
   - Re-evaluate

3. **Repeat Iterations**:
   - Continue adjusting based on results
   - Test each change

4. **Validate**:
   - Run on new images not in training set
   - Confirm accuracy stays high

5. **Deploy**:
   - Once mean IoU > 0.85, robot is ready
   - Use in production with real cups

---

## 🎯 Target Performance

| Metric | Goal | Status |
|--------|------|--------|
| Cup Detection Mean IoU | > 0.85 | - |
| Handle Detection Mean IoU | > 0.80 | - |
| False Negatives | < 5% | - |
| Processing Speed | < 1 sec/image | ✅ |

---

## 📁 Directory Structure

```
SmartGrasp/
├── core/
│   ├── smartgrasp.py          (detection algorithm)
│   └── server.py              (web API)
│
├── tools/
│   ├── web_scraper.py         (download images)
│   ├── annotator.py           (label images)
│   ├── dataset_manager.py     (evaluate accuracy)
│   └── train.py               (menu launcher)
│
├── dataset/
│   ├── raw_images/            (downloaded cups)
│   └── annotations/           (ground truth labels)
│       ├── *.json             (individual annotations)
│       ├── manifest.json      (all annotations)
│       └── evaluation_results.xlsx
│
└── docs/
    └── TRAINING_WORKFLOW.md   (this file)
```

---

## 🚀 Complete Quick Start

```bash
# 1. Create dataset
cd tools
python train.py
# [1] Download images → ~30 images downloaded
# [2] Annotate images → ~10 minutes of labeling

# 2. Evaluate robot
# [3] Evaluate robot → See accuracy metrics

# 3. Check results
# Open: ../dataset/annotations/evaluation_results.xlsx
# Review which images have low accuracy

# 4. Improve (if needed)
# Edit: ../core/smartgrasp.py line 85
# Change threshold from 127 to 120 (or other value)

# 5. Re-evaluate
# [3] Evaluate robot → Check if improved
```

---

## 💡 Pro Tips

✅ **For best results:**
- Use 50+ cup images (variety = better model)
- Include different angles, lighting, colors
- Label cups consistently (similar box sizes)
- Save detected images to review mistakes
- Make one change at a time, then re-evaluate
- Keep notes of what threshold values worked for what image types

⚠️ **Common mistakes:**
- Too few training images (< 10)
- Inconsistent labeling (cup boxes vary wildly in size)
- Threshold values too extreme (0 or 255)
- Not validating on new images after changes
- Trying to adjust multiple parameters at once

---

## 🔍 Debugging

### If cup/handle not separating:

1. **Check ground truth labels first**
   - Open image in annotation tool
   - Is your ground truth correct?
   - If not, re-label it

2. **Check preprocessing steps**
   - Try different threshold values
   - Look at binary image output (white/black)
   - Does binary image clearly show cup vs handle?

3. **Check contour detection**
   - Are both cup and handle detected as separate contours?
   - Or are they merged into one big contour?
   - If merged, try lower threshold

4. **Check size filtering**
   - Is handle 5-70% of cup size?
   - Measure in pixels using annotation tool
   - Adjust ratio if needed

### If false positives (detecting wrong objects):

1. Check if binary threshold is too aggressive
2. Try higher threshold (e.g., 150 instead of 127)
3. Check morphological kernel size
4. Adjust area minimum threshold (>300 px)

---

## 📞 Quick Reference

**Common Parameter Ranges:**

| Parameter | Min | Default | Max |
|-----------|-----|---------|-----|
| Binary Threshold | 100 | 127 | 200 |
| Kernel Size | 3 | 5 | 7 |
| Handle Size Ratio Min | 0.03 | 0.05 | 0.15 |
| Handle Size Ratio Max | 0.5 | 0.7 | 0.9 |

**Performance Benchmarks:**

- Threshold=127: Works well for most cups
- Threshold=150: Better for light/bright cups
- Threshold=100: Better for dark cups
- Kernel=3: Preserves details
- Kernel=7: Fills more holes

---

## 📚 Next Steps

1. ✅ Download images (web_scraper.py)
2. ✅ Annotate images (annotator.py)
3. ✅ Evaluate accuracy (dataset_manager.py)
4. 🔄 **You are here** - Improve based on results
5. ✅ Deploy to production

---

Good luck with your robot training! 🤖☕

For questions, check [README.md](../README.md) or examine code comments.
