"""
SmartGrasp Web Server - Flask API
REST endpoints for image upload and robotic grasping analysis
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import from core
sys.path.insert(0, str(Path(__file__).parent))
from smartgrasp import BatchSmartGrasp

import requests
from urllib.parse import urlparse

# Get the parent directory (SmartGrasp root)
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = PROJECT_ROOT / 'web' / 'templates'
STATIC_DIR = PROJECT_ROOT / 'results'
UPLOAD_DIR = PROJECT_ROOT / 'uploads'

# Create Flask app with correct paths
app = Flask(__name__, 
            template_folder=str(TEMPLATE_DIR),
            static_folder=str(STATIC_DIR),
            static_url_path='/results')
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
processor = BatchSmartGrasp()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve main upload page"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image
        result = processor.process_image(filepath)
        analysis = result['analysis']
        
        # Build response
        response_data = {
            'success': True,
            'filename': filename,
            'grasp_image': f"/results/{result['output_dir'].split('/')[-1]}/grasp_visualization.jpg",
            'analysis': {
                'object': analysis.get('object'),
                'has_handle': analysis.get('has_handle'),
                'cup_bbox': analysis.get('cup_bbox'),
                'handle_bbox': analysis.get('handle_bbox'),
                'grasp_type': analysis.get('grasp_type'),
                'confidence': analysis.get('confidence')
            },
            'pose': result['pose']
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload-url', methods=['POST'])
def upload_from_url():
    """Handle URL-based image upload"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Download image
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to download image'}), 400
        
        # Save temporarily
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_from_url.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Process image
        result = processor.process_image(filepath)
        analysis = result['analysis']
        
        # Build response
        response_data = {
            'success': True,
            'filename': filename,
            'url_source': url,
            'grasp_image': f"/results/{result['output_dir'].split('/')[-1]}/grasp_visualization.jpg",
            'analysis': {
                'object': analysis.get('object'),
                'has_handle': analysis.get('has_handle'),
                'cup_bbox': analysis.get('cup_bbox'),
                'handle_bbox': analysis.get('handle_bbox'),
                'grasp_type': analysis.get('grasp_type'),
                'confidence': analysis.get('confidence')
            },
            'pose': result['pose']
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error processing URL: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    """Get last processed results"""
    try:
        results_folder = 'results'
        if not os.path.exists(results_folder):
            return jsonify([])
        
        # Get recent results
        results = []
        for subfolder in sorted(os.listdir(results_folder), reverse=True)[:10]:
            subfolder_path = os.path.join(results_folder, subfolder)
            if os.path.isdir(subfolder_path):
                analysis_file = os.path.join(subfolder_path, 'analysis.json')
                if os.path.exists(analysis_file):
                    with open(analysis_file, 'r') as f:
                        data = json.load(f)
                        results.append({
                            'folder': subfolder,
                            'image_url': f"/results/{subfolder}/grasp_visualization.jpg",
                            'data': data
                        })
        
        return jsonify(results)
    
    except Exception as e:
        print(f"Error retrieving results: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("🚀 SmartGrasp Server")
    print("📍 Running on http://127.0.0.1:5000")
    print("📁 Upload folder: uploads/")
    print("✅ Ready to process cup images!")
    app.run(debug=True, host='127.0.0.1', port=5000)
