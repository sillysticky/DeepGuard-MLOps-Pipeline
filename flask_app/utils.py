
import numpy as np
from PIL import Image
import os

def preprocess_image(image_file, target_size=(128, 128)):
    """
    Load and preprocess an image for the model.
    """
    try:
        # Open image
        img = Image.open(image_file)
        
        # Convert to RGB (in case of RGBA/Grayscale)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Resize
        img = img.resize(target_size)
        
        # Convert to array and normalize (0-1 range)
        img_array = np.array(img) / 255.0
        
        # Add batch dimension (1, 128, 128, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        print(f"Error processing image: {e}")
        return None
