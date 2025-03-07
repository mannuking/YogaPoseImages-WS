import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import random
import argparse
from filter_dataset import (
    is_human_subject,
    is_illustration_or_animation,
    has_clean_background,
    classify_yoga_pose,
    load_pose_classifier,
    YOGA_POSES
)

def visualize_filtering_results(input_dir, output_dir, num_samples=5):
    """
    Visualize the filtering results by showing sample images that passed and failed.
    
    Args:
        input_dir: Path to the input directory
        output_dir: Path to the output directory
        num_samples: Number of sample images to show for each category
    """
    # Load the pose classifier model
    pose_classifier = load_pose_classifier()
    
    # Get all images from the input directory
    input_images = []
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_images.append(os.path.join(root, filename))
    
    # Get all images from the output directory
    output_images = []
    for root, _, files in os.walk(output_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                output_images.append(os.path.join(root, filename))
    
    # Find images that were filtered out
    output_basenames = [os.path.basename(path) for path in output_images]
    filtered_out = []
    
    for input_path in input_images:
        if os.path.basename(input_path) not in output_basenames:
            filtered_out.append(input_path)
    
    print(f"Total input images: {len(input_images)}")
    print(f"Images that passed: {len(output_images)}")
    print(f"Images that were filtered out: {len(filtered_out)}")
    
    # Sample images from each category
    if len(output_images) > 0:
        passed_samples = random.sample(output_images, min(num_samples, len(output_images)))
    else:
        passed_samples = []
        
    if len(filtered_out) > 0:
        failed_samples = random.sample(filtered_out, min(num_samples, len(filtered_out)))
    else:
        failed_samples = []
    
    # Create a figure to display the results
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, num_samples, figure=fig)
    
    # Plot passed images
    for i, img_path in enumerate(passed_samples):
        if i < num_samples:
            ax = fig.add_subplot(gs[0, i])
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ax.imshow(img)
            ax.set_title("Passed", color='green')
            ax.axis('off')
    
    # Plot failed images with failure reasons
    for i, img_path in enumerate(failed_samples):
        if i < num_samples:
            ax = fig.add_subplot(gs[1, i])
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Analyze why this image failed
            reasons = []
            
            # Check image dimensions
            h, w, _ = img.shape
            if w < 400 or h < 400:
                reasons.append("Too small")
            elif w > 4000 or h > 4000:
                reasons.append("Too large")
            
            # Check aspect ratio
            aspect_ratio = w / h
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                reasons.append("Bad aspect ratio")
            
            # Check if it's an illustration
            if is_illustration_or_animation(img):
                reasons.append("Illustration")
            
            # Check if it has a human subject
            if not is_human_subject(img):
                reasons.append("No human")
            
            # Check background
            if not has_clean_background(img):
                reasons.append("Cluttered background")
            
            # Check pose
            pose_name = os.path.basename(os.path.dirname(img_path))
            is_correct_pose, confidence = classify_yoga_pose(img, pose_classifier, pose_name)
            if not is_correct_pose:
                reasons.append(f"Wrong pose ({confidence:.2f})")
            
            # If no specific reason was found, mark as "Unknown"
            if not reasons:
                reasons.append("Unknown")
            
            ax.imshow(img)
            ax.set_title("\n".join(reasons), color='red')
            ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('filtering_visualization.png', dpi=300)
    plt.close()
    
    print(f"Visualization saved as 'filtering_visualization.png'")
    
    # Create a pie chart of filtering statistics
    labels = ['Passed', 'Filtered Out']
    sizes = [len(output_images), len(filtered_out)]
    colors = ['#4CAF50', '#F44336']
    
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Dataset Filtering Results')
    plt.savefig('filtering_stats.png', dpi=300)
    plt.close()
    
    print(f"Statistics chart saved as 'filtering_stats.png'")

def analyze_failure_reasons(input_dir, output_dir):
    """
    Analyze and visualize the reasons why images were filtered out.
    
    Args:
        input_dir: Path to the input directory
        output_dir: Path to the output directory
    """
    # Load the pose classifier model
    pose_classifier = load_pose_classifier()
    
    # Get all images from the input directory
    input_images = []
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_images.append(os.path.join(root, filename))
    
    # Get all images from the output directory
    output_images = []
    for root, _, files in os.walk(output_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                output_images.append(os.path.join(root, filename))
    
    # Find images that were filtered out
    output_basenames = [os.path.basename(path) for path in output_images]
    filtered_out = []
    
    for input_path in input_images:
        if os.path.basename(input_path) not in output_basenames:
            filtered_out.append(input_path)
    
    # Analyze failure reasons
    reasons_count = {
        "Too small": 0,
        "Too large": 0,
        "Bad aspect ratio": 0,
        "Illustration/Animation": 0,
        "No human subject": 0,
        "Cluttered background": 0,
        "Wrong pose": 0,
        "Unknown": 0
    }
    
    for img_path in filtered_out:
        try:
            img = cv2.imread(img_path)
            if img is None:
                reasons_count["Unknown"] += 1
                continue
                
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Check image dimensions
            h, w, _ = img.shape
            if w < 400 or h < 400:
                reasons_count["Too small"] += 1
                continue
            elif w > 4000 or h > 4000:
                reasons_count["Too large"] += 1
                continue
            
            # Check aspect ratio
            aspect_ratio = w / h
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                reasons_count["Bad aspect ratio"] += 1
                continue
            
            # Check if it's an illustration
            if is_illustration_or_animation(img):
                reasons_count["Illustration/Animation"] += 1
                continue
            
            # Check if it has a human subject
            if not is_human_subject(img):
                reasons_count["No human subject"] += 1
                continue
            
            # Check background
            if not has_clean_background(img):
                reasons_count["Cluttered background"] += 1
                continue
            
            # Check pose
            pose_name = os.path.basename(os.path.dirname(img_path))
            is_correct_pose, _ = classify_yoga_pose(img, pose_classifier, pose_name)
            if not is_correct_pose:
                reasons_count["Wrong pose"] += 1
                continue
            
            # If we got here, we don't know why it was filtered out
            reasons_count["Unknown"] += 1
            
        except Exception:
            reasons_count["Unknown"] += 1
    
    # Remove reasons with zero count
    reasons_count = {k: v for k, v in reasons_count.items() if v > 0}
    
    # Create a bar chart of failure reasons
    plt.figure(figsize=(12, 8))
    plt.bar(reasons_count.keys(), reasons_count.values(), color='#F44336')
    plt.title('Reasons for Filtering Out Images')
    plt.xlabel('Reason')
    plt.ylabel('Number of Images')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('failure_reasons.png', dpi=300)
    plt.close()
    
    print(f"Failure reasons chart saved as 'failure_reasons.png'")
    
    # Print the statistics
    print("\nFailure Reasons Statistics:")
    for reason, count in reasons_count.items():
        print(f"  {reason}: {count} ({count/len(filtered_out)*100:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description='Visualize dataset filtering results')
    parser.add_argument('input_dir', help='Path to the input directory')
    parser.add_argument('output_dir', help='Path to the output directory')
    parser.add_argument('--samples', type=int, default=5, help='Number of sample images to show')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist or is not a directory.")
        sys.exit(1)
        
    if not os.path.isdir(args.output_dir):
        print(f"Error: Output directory '{args.output_dir}' does not exist or is not a directory.")
        sys.exit(1)
    
    print(f"Visualizing filtering results from {args.input_dir} to {args.output_dir}")
    
    visualize_filtering_results(args.input_dir, args.output_dir, args.samples)
    analyze_failure_reasons(args.input_dir, args.output_dir)
    
    print("\nVisualization complete!")

if __name__ == "__main__":
    main()
