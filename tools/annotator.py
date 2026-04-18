"""
Interactive Annotation Tool
Manually label cup and handle bounding boxes in images
Creates ground truth dataset for robot training
"""

import cv2
import os
import json
from pathlib import Path

class ImageAnnotator:
    """Interactively annotate images with cup and handle bounding boxes"""
    
    def __init__(self, images_folder="../dataset/raw_images", output_folder="../dataset/annotations"):
        self.images_folder = images_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
        self.current_image = None
        self.current_path = None
        self.annotations = {}
        self.drawing = False
        self.points = []
        self.current_type = None  # 'cup' or 'handle'
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drawing bounding boxes"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points = [(x, y)]
            self.drawing = True
        
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            # Draw preview rectangle
            if len(self.points) > 0:
                img_copy = self.current_image.copy()
                color = (0, 255, 0) if self.current_type == 'cup' else (255, 0, 0)
                cv2.rectangle(img_copy, self.points[0], (x, y), color, 2)
                cv2.imshow('Annotate Image', img_copy)
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.points.append((x, y))
            self.drawing = False
            x1, y1 = min(self.points[0][0], self.points[1][0]), min(self.points[0][1], self.points[1][1])
            x2, y2 = max(self.points[0][0], self.points[1][0]), max(self.points[0][1], self.points[1][1])
            
            # Save annotation
            if self.current_type:
                if self.current_type not in self.annotations:
                    self.annotations[self.current_type] = []
                
                bbox = [x1, y1, x2, y2]
                self.annotations[self.current_type].append(bbox)
                print(f"✅ Marked {self.current_type.upper()}: {bbox}")
                
                # Draw on image
                color = (0, 255, 0) if self.current_type == 'cup' else (255, 0, 0)
                cv2.rectangle(self.current_image, (x1, y1), (x2, y2), color, 2)
                cv2.imshow('Annotate Image', self.current_image)
    
    def annotate_image(self, image_path):
        """Annotate a single image interactively"""
        self.current_image = cv2.imread(image_path)
        self.current_path = image_path
        self.annotations = {}
        
        filename = os.path.basename(image_path)
        print(f"\n📝 Annotating: {filename}")
        print("=" * 50)
        
        cv2.namedWindow('Annotate Image')
        cv2.setMouseCallback('Annotate Image', self.mouse_callback)
        
        while True:
            cv2.imshow('Annotate Image', self.current_image)
            print("\n🎯 Instructions:")
            print("  [C] Mark CUP body - Draw rectangle around cup")
            print("  [H] Mark HANDLE - Draw rectangle around C-shaped handle")
            print("  [U] Undo last annotation")
            print("  [S] Save and next image")
            print("  [Q] Quit without saving")
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('c'):
                self.current_type = 'cup'
                print("🟢 Ready to mark CUP - Click and drag to draw rectangle")
            
            elif key == ord('h'):
                self.current_type = 'handle'
                print("🔵 Ready to mark HANDLE - Click and drag to draw rectangle")
            
            elif key == ord('u'):
                # Undo
                if self.annotations:
                    last_type = list(self.annotations.keys())[-1]
                    if self.annotations[last_type]:
                        self.annotations[last_type].pop()
                        print("↩️  Undo - Removed last annotation")
                        self.current_image = cv2.imread(self.current_path)
                        self.redraw_annotations()
            
            elif key == ord('s'):
                # Save
                if 'cup' in self.annotations and 'handle' in self.annotations:
                    self.save_annotation(filename)
                    break
                else:
                    print("⚠️  Must mark both CUP and HANDLE before saving!")
            
            elif key == ord('q'):
                print("❌ Skipped")
                break
        
        cv2.destroyAllWindows()
    
    def redraw_annotations(self):
        """Redraw all annotations on current image"""
        for ann_type, bboxes in self.annotations.items():
            color = (0, 255, 0) if ann_type == 'cup' else (255, 0, 0)
            for bbox in bboxes:
                x1, y1, x2, y2 = bbox
                cv2.rectangle(self.current_image, (x1, y1), (x2, y2), color, 2)
    
    def save_annotation(self, filename):
        """Save annotation to JSON"""
        json_path = os.path.join(self.output_folder, f"{Path(filename).stem}.json")
        
        data = {
            'filename': filename,
            'image_path': self.current_path,
            'cup_bbox': self.annotations.get('cup', [None])[0],
            'handle_bbox': self.annotations.get('handle', [None])[0]
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Saved annotation: {json_path}")
    
    def annotate_folder(self):
        """Annotate all images in folder"""
        images = sorted([
            f for f in os.listdir(self.images_folder)
            if f.lower().endswith(('.jpg', '.png', '.webp'))
        ])
        
        if not images:
            print(f"❌ No images found in {self.images_folder}")
            return
        
        print(f"📷 Found {len(images)} images to annotate")
        
        for i, img_file in enumerate(images):
            img_path = os.path.join(self.images_folder, img_file)
            print(f"\n[{i+1}/{len(images)}]", end="")
            self.annotate_image(img_path)
        
        print("\n✅ Annotation complete!")
    
    def create_dataset_manifest(self):
        """Create manifest of all annotated images"""
        manifest = []
        
        json_files = [f for f in os.listdir(self.output_folder) if f.endswith('.json')]
        
        for json_file in json_files:
            with open(os.path.join(self.output_folder, json_file), 'r') as f:
                data = json.load(f)
                manifest.append(data)
        
        manifest_path = os.path.join(self.output_folder, 'manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Created manifest: {manifest_path}")
        print(f"   Contains {len(manifest)} annotated images")
        
        return manifest

if __name__ == "__main__":
    annotator = ImageAnnotator()
    
    print("🏷️  Interactive Annotation Tool")
    print("=" * 50)
    print()
    
    # Annotate all images
    annotator.annotate_folder()
    
    # Create manifest
    annotator.create_dataset_manifest()
    
    print("\n✅ Dataset ready for robot training!")
