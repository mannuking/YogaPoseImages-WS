import os
import sys
import cv2
import numpy as np
from PIL import Image
import face_recognition
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
import shutil
import multiprocessing
from collections import Counter
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_filtering.log"),
        logging.StreamHandler()
    ]
)

# Constants
MIN_IMAGE_SIZE = 400  # Minimum width or height in pixels
MAX_IMAGE_SIZE = 4000  # Maximum width or height in pixels
TARGET_SIZE = (224, 224)  # Target size for model input
MIN_ASPECT_RATIO = 0.5  # Minimum aspect ratio (width/height)
MAX_ASPECT_RATIO = 2.0  # Maximum aspect ratio (width/height)
BACKGROUND_COMPLEXITY_THRESHOLD = 0.2  # Threshold for background complexity
HUMAN_CONFIDENCE_THRESHOLD = 0.7  # Threshold for human detection confidence
POSE_CONFIDENCE_THRESHOLD = 0.6  # Threshold for pose classification confidence

# List of yoga poses (both Hindi and English names for reference)
YOGA_POSES = {
    "ताड़ासन": "Tadasana (Mountain Pose)",
    "त्रिकोणासन": "Trikonasana (Triangle Pose)",
    "दुर्वासन": "Durvasana (Durva Grass Pose)",
    "अर्धचंद्रासन": "Ardha Chandrasana (Half Moon Pose)",
    "उष्ट्रासन": "Ustrasana (Camel Pose)",
    "धनुरासन": "Dhanurasana (Bow Pose)",
    "भुजंगासन": "Bhujangasana (Cobra Pose)",
    "मौलासन": "Maulasana (Garland Pose)",
    "हलासन": "Halasana (Plow Pose)",
    "सेतुबंधासन": "Setu Bandhasana (Bridge Pose)"
}

def load_pose_classifier():
    """
    Load or create a model for yoga pose classification.
    In a real implementation, this would load a pre-trained model.
    For this example, we'll simulate the model's behavior.
    """
    # Placeholder for a real model
    # In a real implementation, you would load a trained model like:
    # model = tf.keras.models.load_model('yoga_pose_model.h5')
    
    # For demonstration, we'll use MobileNetV2 as a feature extractor
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(len(YOGA_POSES), activation='softmax')
    ])
    
    logging.info("Pose classifier initialized")
    return model

def is_human_subject(img_np):
    """
    Determine if the image contains a real human subject.
    Uses face detection and human body detection techniques.
    
    Args:
        img_np: Numpy array of the image
        
    Returns:
        bool: True if a real human subject is detected, False otherwise
    """
    # 1. Try face detection first
    try:
        face_locations = face_recognition.face_locations(img_np)
        if len(face_locations) > 0:
            return True
    except Exception as e:
        logging.warning(f"Face detection error: {e}")
    
    # 2. Check for human body features using edge detection and contour analysis
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect edges
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and shape
        large_contours = [c for c in contours if cv2.contourArea(c) > img_np.shape[0] * img_np.shape[1] * 0.05]
        
        # If we have large contours that could be human body parts
        if len(large_contours) >= 2:
            return True
    except Exception as e:
        logging.warning(f"Body detection error: {e}")
    
    # 3. Check for skin tones
    try:
        # Convert to HSV color space
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        
        # Define range of skin color in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create a binary mask for skin color
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Calculate percentage of skin pixels
        skin_percentage = np.sum(skin_mask > 0) / (img_np.shape[0] * img_np.shape[1])
        
        # If significant skin tone is detected
        if skin_percentage > 0.15:
            return True
    except Exception as e:
        logging.warning(f"Skin detection error: {e}")
    
    return False

def is_illustration_or_animation(img_np):
    """
    Detect if an image is an illustration or animation rather than a photograph.
    
    Args:
        img_np: Numpy array of the image
        
    Returns:
        bool: True if the image is likely an illustration or animation, False otherwise
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # 1. Edge detection for cartoon-like features
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (img_np.shape[0] * img_np.shape[1])
        
        # 2. Color quantization check
        # Illustrations often have fewer unique colors
        resized = cv2.resize(img_np, (32, 32))  # Resize to reduce computation
        pixels = resized.reshape(-1, 3)
        unique_colors = np.unique(pixels, axis=0).shape[0]
        color_ratio = unique_colors / (32 * 32)
        
        # 3. Texture analysis
        # Illustrations typically have less texture variation
        texture_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        texture = cv2.filter2D(gray, -1, texture_kernel)
        texture_variance = np.var(texture)
        normalized_variance = texture_variance / (255 * 255)
        
        # Combined decision
        if (edge_density > 0.1 and color_ratio < 0.1) or normalized_variance < 0.01:
            return True
            
        return False
    except Exception as e:
        logging.warning(f"Illustration detection error: {e}")
        return False

def has_clean_background(img_np):
    """
    Determine if the image has a clean background.
    
    Args:
        img_np: Numpy array of the image
        
    Returns:
        bool: True if the background is clean, False otherwise
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect edges
        edges = cv2.Canny(blurred, 50, 150)
        
        # Calculate edge density in the border regions
        h, w = edges.shape
        border_width = int(min(h, w) * 0.1)  # 10% of the smaller dimension
        
        # Create a mask for the border regions
        mask = np.zeros_like(edges)
        mask[0:border_width, :] = 1  # Top border
        mask[h-border_width:h, :] = 1  # Bottom border
        mask[:, 0:border_width] = 1  # Left border
        mask[:, w-border_width:w] = 1  # Right border
        
        # Calculate edge density in the border regions
        border_edge_density = np.sum((edges > 0) & (mask > 0)) / np.sum(mask)
        
        # If the border has low edge density, the background is likely clean
        return border_edge_density < BACKGROUND_COMPLEXITY_THRESHOLD
    except Exception as e:
        logging.warning(f"Background analysis error: {e}")
        return False

def classify_yoga_pose(img_np, model, pose_name):
    """
    Classify the yoga pose in the image.
    
    Args:
        img_np: Numpy array of the image
        model: The pose classification model
        pose_name: The expected pose name
        
    Returns:
        tuple: (is_correct_pose, confidence)
    """
    try:
        # Resize and preprocess the image for the model
        img_resized = cv2.resize(img_np, TARGET_SIZE)
        img_array = keras_image.img_to_array(img_resized)
        img_array = preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Get model predictions
        predictions = model.predict(img_array, verbose=0)
        
        # Get the predicted class and confidence
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]
        
        # In a real implementation, you would map the predicted class to the pose name
        # For this example, we'll simulate the result based on the filename
        
        # Get the pose index from the list of poses
        pose_index = list(YOGA_POSES.keys()).index(pose_name) if pose_name in YOGA_POSES else -1
        
        # Simulate correct classification with some randomness
        # In a real implementation, you would use the actual model prediction
        is_correct_pose = (predicted_class == pose_index)
        
        return is_correct_pose, confidence
    except Exception as e:
        logging.warning(f"Pose classification error: {e}")
        return False, 0.0

def filter_image(args):
    """
    Process a single image through all filters.
    
    Args:
        args: Tuple containing (input_path, output_dir, pose_classifier)
        
    Returns:
        dict: Results of the filtering process
    """
    input_path, output_dir, pose_classifier = args
    
    # Extract pose name from the directory structure
    dir_name = os.path.basename(os.path.dirname(input_path))
    file_name = os.path.basename(input_path)
    
    result = {
        'path': input_path,
        'passed': False,
        'reason': None
    }
    
    try:
        # Open and validate the image
        with Image.open(input_path) as img:
            # Check image dimensions
            width, height = img.size
            if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
                result['reason'] = f"Image too small: {width}x{height}"
                return result
                
            if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
                result['reason'] = f"Image too large: {width}x{height}"
                return result
                
            # Check aspect ratio
            aspect_ratio = width / height
            if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
                result['reason'] = f"Invalid aspect ratio: {aspect_ratio:.2f}"
                return result
                
            # Convert to numpy array for OpenCV processing
            img_np = np.array(img)
            
            # Check if image is grayscale or has alpha channel
            if len(img_np.shape) < 3 or img_np.shape[2] < 3:
                result['reason'] = "Grayscale image"
                return result
                
            # If image has 4 channels (RGBA), convert to RGB
            if len(img_np.shape) == 3 and img_np.shape[2] == 4:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
            
            # Check if it's an illustration or animation
            if is_illustration_or_animation(img_np):
                result['reason'] = "Detected as illustration or animation"
                return result
                
            # Check if it contains a human subject
            if not is_human_subject(img_np):
                result['reason'] = "No human subject detected"
                return result
                
            # Check if it has a clean background
            if not has_clean_background(img_np):
                result['reason'] = "Background too complex or cluttered"
                return result
                
            # Classify the yoga pose
            is_correct_pose, confidence = classify_yoga_pose(img_np, pose_classifier, dir_name)
            if not is_correct_pose or confidence < POSE_CONFIDENCE_THRESHOLD:
                result['reason'] = f"Incorrect pose or low confidence: {confidence:.2f}"
                return result
                
            # If all checks pass, copy the image to the output directory
            pose_output_dir = os.path.join(output_dir, dir_name)
            os.makedirs(pose_output_dir, exist_ok=True)
            
            output_path = os.path.join(pose_output_dir, file_name)
            shutil.copy2(input_path, output_path)
            
            result['passed'] = True
            result['output_path'] = output_path
            
            return result
    except Exception as e:
        result['reason'] = f"Error processing image: {str(e)}"
        return result

def filter_dataset(input_dir, output_dir, num_processes=None):
    """
    Filter the dataset by applying all filters to each image.
    
    Args:
        input_dir: Path to the input directory
        output_dir: Path to the output directory
        num_processes: Number of processes to use (defaults to CPU count)
    """
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the pose classifier model
    pose_classifier = load_pose_classifier()
    
    # Collect all image paths
    image_paths = []
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, filename))
    
    logging.info(f"Found {len(image_paths)} images to process")
    
    # Process images in parallel
    with multiprocessing.Pool(processes=num_processes) as pool:
        args = [(path, output_dir, pose_classifier) for path in image_paths]
        results = pool.map(filter_image, args)
    
    # Analyze results
    passed = [r for r in results if r['passed']]
    failed = [r for r in results if not r['passed']]
    
    # Count failure reasons
    failure_reasons = Counter([r['reason'] for r in failed])
    
    # Log results
    logging.info(f"Filtering complete: {len(passed)} passed, {len(failed)} failed")
    logging.info("Failure reasons:")
    for reason, count in failure_reasons.most_common():
        logging.info(f"  {reason}: {count}")
    
    # Return summary
    return {
        'total': len(results),
        'passed': len(passed),
        'failed': len(failed),
        'failure_reasons': failure_reasons
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python filter_dataset.py <input_directory> <output_directory>")
        sys.exit(1)
    
    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    
    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist or is not a directory.")
        sys.exit(1)
    
    logging.info(f"Starting dataset filtering from {input_directory} to {output_directory}")
    
    results = filter_dataset(input_directory, output_directory)
    
    logging.info(f"Filtering complete. Summary:")
    logging.info(f"  Total images: {results['total']}")
    logging.info(f"  Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    logging.info(f"  Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    
    print(f"\nFiltering complete!")
    print(f"Total images processed: {results['total']}")
    print(f"Images that passed all filters: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"Images that failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print("\nTop failure reasons:")
    for reason, count in results['failure_reasons'].most_common(5):
        print(f"  {reason}: {count}")
    
    print(f"\nFiltered images saved to: {output_directory}")
    print("See dataset_filtering.log for detailed information.")

if __name__ == "__main__":
    main()
