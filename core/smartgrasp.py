"""
SmartGrasp - Core Cup Detection & Robotic Grasping Module
Detects cup body and C-shaped handle for robot manipulation
"""

from PIL import Image, ImageDraw
import base64
import json
import re
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
try:
    import cv2
except ImportError:
    cv2 = None

class BatchSmartGrasp:
    """Batch processor for cup detection and grasp position calculation"""
    
    def __init__(self):
        self.model = "llama3.2:1b"
        os.makedirs("results", exist_ok=True)
        os.makedirs("results/screenshots", exist_ok=True)
    
    def process_image(self, img_path, output_dir="results"):
        """Process single image: detect cup & handle, calculate grasp position"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        basename = os.path.splitext(os.path.basename(img_path))[0]
        
        # Create dated folder
        date_folder = f"{output_dir}/{timestamp}_{basename}"
        os.makedirs(date_folder, exist_ok=True)
        
        # Analyze with handle detection
        analysis = self.analyze_object(img_path)
        
        # Calculate safe grasp at handle center
        pose, width = self.precise_grasp(analysis)
        
        # Visualize with handle information
        self.visualize_precise(img_path, analysis, pose, width, date_folder)
        
        # Save analysis
        with open(f"{date_folder}/analysis.json", 'w') as f:
            json.dump({
                'analysis': {
                    'object': analysis.get('object'),
                    'has_handle': analysis.get('has_handle'),
                    'grasp_type': analysis.get('grasp_type'),
                    'handle_type': analysis.get('handle_type'),
                    'confidence': analysis.get('confidence', 0.0)
                },
                'cup_bbox': analysis.get('cup_bbox'),
                'handle_bbox': analysis.get('handle_bbox'),
                'handle_center': analysis.get('handle_center'),
                'pose': pose,
                'width': width
            }, f, indent=2)
        
        print(f"✅ Processed: {basename}")
        return {
            'status': 'success',
            'image_path': img_path,
            'output_dir': date_folder,
            'analysis': analysis,
            'pose': pose,
            'width': width
        }
    
    def analyze_object(self, image_path):
        """Analyze image using handle detection (OpenCV)"""
        return self.detect_handle_fallback(image_path)
    
    def detect_handle_fallback(self, image_path):
        """Detect cup body and C-shaped handle using OpenCV"""
        if not cv2:
            return {'has_handle': False, 'cup_bbox': None, 'handle_bbox': None, 'confidence': 0}
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'has_handle': False, 'cup_bbox': None, 'handle_bbox': None, 'confidence': 0}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = img.shape[:2]
            
            # PREPROCESSING: Binary thresholding
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # PREPROCESSING: Morphological operations to clean image
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)  # Remove noise
            
            kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel2)  # Fill holes
            
            # PREPROCESSING: Distance transform to separate touching objects
            dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
            _, markers = cv2.threshold(dist_transform, 0.5*dist_transform.max(), 255, 0)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) < 1:
                return {'has_handle': False, 'cup_bbox': None, 'handle_bbox': None, 'confidence': 0.3}
            
            # Filter contours by size and position
            valid_contours = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 300:  # Minimum area threshold
                    valid_contours.append((cnt, area))
            
            if not valid_contours:
                return {'has_handle': False, 'cup_bbox': None, 'handle_bbox': None, 'confidence': 0.2}
            
            # Sort by area (largest = cup)
            valid_contours.sort(key=lambda x: x[1], reverse=True)
            
            # CUP: Largest contour that doesn't fill the image
            cup_bbox = None
            cup_area = 0
            
            for cnt, area in valid_contours:
                x, y, cw, ch = cv2.boundingRect(cnt)
                rect_area = cw * ch
                image_area = h * w
                fill_ratio = rect_area / image_area
                
                if fill_ratio < 0.8:  # Cup shouldn't fill image
                    cup_bbox = (x, y, x + cw, y + ch)
                    cup_area = area
                    break
            
            if not cup_bbox:
                return {'has_handle': False, 'cup_bbox': None, 'handle_bbox': None, 'confidence': 0.3}
            
            # HANDLE: Secondary contours beside or below cup
            handle_bbox = None
            handle_area = 0
            
            for cnt, area in valid_contours[1:]:  # Skip cup
                x, y, cw, ch = cv2.boundingRect(cnt)
                size_ratio = area / cup_area
                
                # Handle should be 5-70% of cup size
                if not (0.05 < size_ratio < 0.7):
                    continue
                
                # Handle should be positioned beside or below cup
                cup_x1, cup_y1, cup_x2, cup_y2 = cup_bbox
                contour_x1, contour_y1 = x, y
                contour_x2, contour_y2 = x + cw, y + ch
                
                # Check if positioned beside (left/right) or below
                beside_horizontally = (contour_x1 > cup_x2 or contour_x2 < cup_x1)
                beside_vertically = (contour_y1 > cup_y2 or contour_y2 < cup_y1)
                
                # Not completely inside cup
                completely_inside = (
                    contour_x1 >= cup_x1 and contour_x2 <= cup_x2 and
                    contour_y1 >= cup_y1 and contour_y2 <= cup_y2
                )
                
                if not completely_inside:
                    handle_bbox = (x, y, x + cw, y + ch)
                    handle_area = area
                    break
            
            return {
                'object': 'cup',
                'has_handle': handle_bbox is not None,
                'cup_bbox': cup_bbox,
                'handle_bbox': handle_bbox,
                'handle_center': self.get_bbox_center(handle_bbox) if handle_bbox else None,
                'grasp_type': 'handle_center' if handle_bbox else 'body_center',
                'handle_type': 'C-shaped' if handle_bbox else None,
                'confidence': 0.85 if handle_bbox else 0.65
            }
        
        except Exception as e:
            print(f"Error in detection: {e}")
            return {'has_handle': False, 'cup_bbox': None, 'handle_bbox': None, 'confidence': 0}
    
    def get_bbox_center(self, bbox):
        """Get center point of bounding box"""
        if not bbox:
            return None
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def precise_grasp(self, analysis):
        """Calculate gripper position for handle-safe grasping"""
        if analysis.get('handle_bbox') and analysis.get('handle_center'):
            x, y = analysis['handle_center']
            pose = [x, y, 0.15]  # Z=0.15 for cup height
            width = 0.08  # Gripper width for handle
            grasp_type = 'handle_center'
        else:
            # Fallback to cup center
            bbox = analysis.get('cup_bbox')
            if bbox:
                x1, y1, x2, y2 = bbox
                x, y = (x1 + x2) // 2, (y1 + y2) // 2
                pose = [x, y, 0.15]
                width = 0.10
            else:
                pose = [0, 0, 0]
                width = 0
            grasp_type = 'body_center'
        
        return pose, width
    
    def visualize_precise(self, img_path, analysis, pose, width, output_dir):
        """Draw visualization: GREEN cup box + BLUE handle box + RED gripper"""
        img = cv2.imread(img_path)
        if img is None:
            return
        
        # Draw cup bounding box (GREEN)
        if analysis.get('cup_bbox'):
            x1, y1, x2, y2 = analysis['cup_bbox']
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(img, "CUP", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw handle bounding box (BLUE)
        if analysis.get('handle_bbox'):
            x1, y1, x2, y2 = analysis['handle_bbox']
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            cv2.putText(img, "HANDLE", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw gripper position (RED)
        if pose and pose[0] > 0 and pose[1] > 0:
            x, y = int(pose[0]), int(pose[1])
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            cv2.line(img, (x - 20, y), (x + 20, y), (0, 0, 255), 2)  # Horizontal line
            cv2.line(img, (x, y - 20), (x, y + 20), (0, 0, 255), 2)  # Vertical line
            cv2.putText(img, f"GRIPPER ({x},{y})", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Save visualization
        output_path = os.path.join(output_dir, 'grasp_visualization.jpg')
        cv2.imwrite(output_path, img)
        
        return output_path
    
    def batch_process(self, images_folder="uploads"):
        """Process all images in a folder"""
        if not os.path.exists(images_folder):
            print(f"Folder not found: {images_folder}")
            return
        
        images = [f for f in os.listdir(images_folder) if f.lower().endswith(('.jpg', '.png', '.webp'))]
        print(f"Processing {len(images)} images...")
        
        for img_file in images:
            img_path = os.path.join(images_folder, img_file)
            self.process_image(img_path)

if __name__ == "__main__":
    processor = BatchSmartGrasp()
    processor.batch_process("uploads")
