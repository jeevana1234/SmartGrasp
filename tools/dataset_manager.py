"""
Dataset Manager - Evaluates robot detection against ground truth
Calculates accuracy metrics (IoU) and generates reports
"""

import json
import os
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))
from smartgrasp import BatchSmartGrasp

class DatasetManager:
    """Manage annotated dataset and evaluate robot detection"""
    
    def __init__(self, dataset_folder="../dataset/annotations"):
        self.dataset_folder = dataset_folder
        self.manifest_path = os.path.join(dataset_folder, 'manifest.json')
        self.processor = BatchSmartGrasp()
        self.results = []
    
    def load_manifest(self):
        """Load annotated dataset manifest"""
        if not os.path.exists(self.manifest_path):
            print(f"❌ No manifest found at {self.manifest_path}")
            return []
        
        with open(self.manifest_path, 'r') as f:
            return json.load(f)
    
    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union (IoU) for bounding boxes"""
        if not box1 or not box2:
            return 0.0
        
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Calculate intersection
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Calculate union
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
    
    def evaluate_detection(self, image_path, ground_truth_box, box_type='cup'):
        """Evaluate robot detection against ground truth"""
        try:
            analysis = self.processor.analyze_object(image_path)
            
            if box_type == 'cup':
                detected_box = analysis.get('cup_bbox')
            else:  # handle
                detected_box = analysis.get('handle_bbox')
            
            if not detected_box:
                return {'iou': 0, 'detected': False, 'error': 'No detection'}
            
            iou = self.calculate_iou(ground_truth_box, detected_box)
            
            return {
                'iou': iou,
                'detected': True,
                'ground_truth': ground_truth_box,
                'detected_box': detected_box,
                'error': None
            }
        
        except Exception as e:
            return {'iou': 0, 'detected': False, 'error': str(e)}
    
    def evaluate_dataset(self):
        """Evaluate robot on entire dataset"""
        manifest = self.load_manifest()
        
        if not manifest:
            print("❌ No annotated images found")
            return
        
        print(f"🤖 Evaluating robot on {len(manifest)} images...")
        print("=" * 50)
        
        cup_ious = []
        handle_ious = []
        
        for i, annotation in enumerate(manifest):
            print(f"\n[{i+1}/{len(manifest)}] {annotation['filename']}")
            
            # Evaluate cup detection
            if annotation['cup_bbox']:
                cup_result = self.evaluate_detection(
                    annotation['image_path'],
                    annotation['cup_bbox'],
                    'cup'
                )
                cup_ious.append(cup_result['iou'])
                print(f"   Cup IoU: {cup_result['iou']:.3f}")
                
                result_data = {
                    'filename': annotation['filename'],
                    'type': 'cup',
                    'iou': cup_result['iou'],
                    'detected': cup_result['detected'],
                    'error': cup_result.get('error')
                }
                self.results.append(result_data)
            
            # Evaluate handle detection
            if annotation['handle_bbox']:
                handle_result = self.evaluate_detection(
                    annotation['image_path'],
                    annotation['handle_bbox'],
                    'handle'
                )
                handle_ious.append(handle_result['iou'])
                print(f"   Handle IoU: {handle_result['iou']:.3f}")
                
                result_data = {
                    'filename': annotation['filename'],
                    'type': 'handle',
                    'iou': handle_result['iou'],
                    'detected': handle_result['detected'],
                    'error': handle_result.get('error')
                }
                self.results.append(result_data)
        
        # Calculate statistics
        print("\n" + "=" * 50)
        print("📊 EVALUATION RESULTS")
        print("=" * 50)
        
        if cup_ious:
            cup_mean = np.mean(cup_ious)
            cup_std = np.std(cup_ious)
            print(f"🏆 Cup Detection:")
            print(f"   Mean IoU: {cup_mean:.3f} (±{cup_std:.3f})")
            print(f"   Min: {min(cup_ious):.3f}, Max: {max(cup_ious):.3f}")
        
        if handle_ious:
            handle_mean = np.mean(handle_ious)
            handle_std = np.std(handle_ious)
            print(f"🏆 Handle Detection:")
            print(f"   Mean IoU: {handle_mean:.3f} (±{handle_std:.3f})")
            print(f"   Min: {min(handle_ious):.3f}, Max: {max(handle_ious):.3f}")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save evaluation results to Excel"""
        df = pd.DataFrame(self.results)
        output_path = os.path.join(self.dataset_folder, 'evaluation_results.xlsx')
        df.to_excel(output_path, index=False)
        
        print(f"\n✅ Results saved to: {output_path}")
        
        if len(df) > 0:
            print("\nTop performers:")
            print(df.nlargest(5, 'iou')[['filename', 'type', 'iou']])
            
            print("\nNeed improvement:")
            print(df.nsmallest(5, 'iou')[['filename', 'type', 'iou']])

if __name__ == "__main__":
    manager = DatasetManager()
    manager.evaluate_dataset()
