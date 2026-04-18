#!/usr/bin/env python
"""
SmartGrasp Robot Training Launcher
Master script to manage entire workflow
"""

import os
import subprocess
import sys
from pathlib import Path

def print_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("🤖 SmartGrasp Robot Training System")
    print("="*60)
    print("\n📋 WORKFLOW:")
    print("  1. Download cup images from internet (web scraping)")
    print("  2. Manually label cup & handle locations (annotation)")
    print("  3. Evaluate robot accuracy (dataset evaluation)")
    print("  4. Review & improve detection")
    print("\n🎯 MENU:")
    print("  [1] Step 1: Download cup images (web_scraper.py)")
    print("  [2] Step 2: Annotate images (annotator.py)")
    print("  [3] Step 3: Evaluate robot (dataset_manager.py)")
    print("  [4] Help: View training workflow")
    print("  [5] Status: Check dataset progress")
    print("  [Q] Quit")
    print("-"*60)

def check_dependencies():
    """Check if required packages are installed"""
    required = ['cv2', 'pandas', 'PIL', 'requests']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install opencv-python pandas pillow requests beautifulsoup4")
        return False
    return True

def run_script(script_name, description):
    """Run a Python script"""
    print(f"\n▶️  {description}")
    print("-"*60)
    
    try:
        subprocess.run([sys.executable, script_name], check=False)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("-"*60)

def show_dataset_status():
    """Show dataset progress"""
    print("\n📊 DATASET STATUS")
    print("="*60)
    
    base_path = Path(__file__).parent.parent
    folders = {
        base_path / 'dataset' / 'raw_images': 'Raw downloaded images',
        base_path / 'dataset' / 'annotations': 'Annotated images (labeled)',
        base_path / 'data' / 'preprocessing_debug': 'Debug visualizations'
    }
    
    for folder, desc in folders.items():
        if folder.exists():
            files = len([f for f in folder.iterdir() if f.is_file()])
            print(f"✅ {str(folder):60} ({files} files)")
        else:
            print(f"❌ {str(folder):60} (not created yet)")
    
    # Check for results files
    print("\n📈 EVALUATION RESULTS:")
    results_file = base_path / 'dataset' / 'annotations' / 'evaluation_results.xlsx'
    if results_file.exists():
        print(f"✅ evaluation_results.xlsx (Open in Excel)")
    else:
        print(f"❌ evaluation_results.xlsx (not created yet)")
    
    print("="*60)

def show_help():
    """Show training workflow help"""
    print("\n📚 TRAINING WORKFLOW GUIDE")
    print("="*60)
    print("""
PHASE 1: DATA COLLECTION
  → Run: [1] Download cup images (web_scraper.py)
  → Downloads real-world cup images from Unsplash & Pexels
  → Creates: dataset/raw_images/
  
PHASE 2: DATA LABELING  
  → Run: [2] Annotate images (annotator.py)
  → Manually mark cup body and handle positions
  → Creates: dataset/annotations/manifest.json
  → Use: [C] for cup, [H] for handle, [S] to save
  
PHASE 3: MODEL EVALUATION
  → Run: [3] Evaluate robot (dataset_manager.py)
  → Tests robot against ground truth labels
  → Calculates IoU accuracy score
  → Creates: evaluation_results.xlsx
  
PHASE 4: ITERATION
  → Review evaluation_results.xlsx in Excel
  → Find images with low accuracy
  → Adjust thresholds in core/smartgrasp.py
  → Re-run evaluation
  → Repeat until accuracy > 0.85

KEY CONCEPTS:
  IoU (Intersection over Union):
    - Measures how well detected box matches ground truth
    - 1.0 = perfect, 0.5 = acceptable, 0.0 = completely wrong
    
  Ground Truth:
    - The "correct" answer (manually labeled positions)
    - Robot detection is compared against this
    
  Threshold:
    - Edge detection cutoff value in image preprocessing
    - Affects which objects are detected

TROUBLESHOOTING:
  Low cup IoU   → Adjust threshold (try 100-180)
  Low handle IoU → Adjust morphological kernel size
  No detection  → Check if images were properly labeled

📖 Full guide: docs/TRAINING_WORKFLOW.md
""")
    print("="*60)

def main():
    """Main launcher"""
    print("\n🚀 SmartGrasp Robot Training Launcher")
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️  Please install missing packages first")
        return
    
    while True:
        print_menu()
        choice = input("Enter choice [1-5, Q]: ").upper().strip()
        
        if choice == '1':
            run_script('web_scraper.py', 'Web Scraper - Downloading cup images')
        
        elif choice == '2':
            run_script('annotator.py', 'Image Annotator - Label cup & handle positions')
        
        elif choice == '3':
            run_script('dataset_manager.py', 'Dataset Manager - Evaluate robot accuracy')
        
        elif choice == '4':
            show_help()
        
        elif choice == '5':
            show_dataset_status()
        
        elif choice == 'Q':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
