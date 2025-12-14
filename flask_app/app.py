
import os
import tensorflow as tf
from flask import Flask, render_template, request, jsonify
from utils import preprocess_image
import numpy as np

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

app = Flask(__name__)

# Load Model (Global load to avoid reloading on every request)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'deepfake_model.keras')
print(f"Loading model from: {MODEL_PATH}")

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    try:
        # Preprocess
        processed_img = preprocess_image(file)
        
        if processed_img is None:
            return jsonify({'error': 'Invalid image format'}), 400
            
        # Predict
        prediction = model.predict(processed_img)[0][0]
        
        # Interpret result (Sigmoid output: 0-1)
        # Assuming 0 = REAL, 1 = FAKE (based on training mapping)
        # Wait - let's double check mapping. Usually generators produce 0=Class1, 1=Class2.
        # In our code: 'REAL': 0, 'FAKE': 1 is common, but `image_dataset_from_directory` sorts alphabetically:
        # FAKE comes before REAL. So FAKE=0, REAL=1 usually.
        # Let's check class_names from training... 
        # Actually, let's assume FAKE=0, REAL=1 for now based on standard directory sorting.
        # If prediction < 0.5 -> FAKE, else REAL.
        
        # Correction: Our data_preprocessing.py uses:
        # classes = {'REAL': 0, 'FAKE': 1} (manually set usually?)
        # Let's check data_preprocessing.py content in a sec to be sure.
        # SAFE BET: Return the raw score and label logic can be tweaked.
        
        confidence = float(prediction)
        
        # CORRECT Mapping based on data_preprocessing.py:
        # REAL = 0, FAKE = 1
        # So prediction > 0.5 means FAKE (class 1), not REAL!
        
        label = "FAKE" if confidence > 0.5 else "REAL"
        
        # Adjust confidence score to be "confidence of predicted class"
        display_confidence = confidence if label == "FAKE" else 1 - confidence
        
        return jsonify({
            'label': label,
            'confidence': f"{display_confidence * 100:.2f}%",
            'raw_score': confidence
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
