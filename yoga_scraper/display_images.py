import os
import sys
import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.gridspec import GridSpec

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Display Yoga Pose Images")
    
    parser.add_argument("--dataset-dir", default="processed_images", help="Directory containing the processed images")
    parser.add_argument("--num-poses", type=int, default=None, help="Number of poses to display (default: all)")
    parser.add_argument("--num-samples", type=int, default=5, help="Number of samples per pose to display")
    parser.add_argument("--output-file", default="yoga_poses_display.png", help="Output file for the visualization")
    parser.add_argument("--random-seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--figsize", type=int, nargs=2, default=[15, None], help="Figure size (width, height)")
    
    return parser.parse_args()

def display_images(dataset_dir, num_poses=None, num_samples=5, output_file="yoga_poses_display.png", 
                  random_seed=42, figsize=None):
    """Display yoga pose images in a grid layout."""
    # Set random seed for reproducibility
    random.seed(random_seed)
    
    # Get all subdirectories (yoga poses)
    pose_dirs = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    
    # Sort pose directories alphabetically
    pose_dirs.sort()
    
    # If num_poses is specified, select a subset of poses
    if num_poses is not None and num_poses < len(pose_dirs):
        pose_dirs = pose_dirs[:num_poses]
    
    # Number of poses to display
    num_poses = len(pose_dirs)
    
    # Calculate figure size if height is not specified
    if figsize is None:
        figsize = (15, 3 * num_poses)
    elif figsize[1] is None:
        figsize = (figsize[0], 3 * num_poses)
    
    # Create a figure with GridSpec for more control over the layout
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(num_poses, num_samples, figure=fig)
    
    # Add a title to the figure
    fig.suptitle("Yoga Pose Dataset", fontsize=16, y=0.98)
    
    # Iterate over each pose
    for i, pose_dir in enumerate(pose_dirs):
        pose_path = os.path.join(dataset_dir, pose_dir)
        
        # Get all image files for this pose
        image_files = [f for f in os.listdir(pose_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # If there are fewer images than num_samples, use all of them
        num_to_sample = min(num_samples, len(image_files))
        
        # Sample random images
        sampled_images = random.sample(image_files, num_to_sample)
        
        # Display each sampled image
        for j, image_file in enumerate(sampled_images):
            image_path = os.path.join(pose_path, image_file)
            
            # Create a subplot
            ax = fig.add_subplot(gs[i, j])
            
            try:
                # Open and display the image
                img = Image.open(image_path)
                ax.imshow(img)
                
                # Set the title for the first image in each row
                if j == 0:
                    ax.set_title(pose_dir, fontsize=12, loc='left', pad=10)
                
                # Remove axis ticks
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Add a border around the image
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_color('black')
                    spine.set_linewidth(0.5)
                
            except Exception as e:
                ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center')
                ax.set_xticks([])
                ax.set_yticks([])
        
        # If there are fewer images than num_samples, hide the remaining axes
        for j in range(num_to_sample, num_samples):
            ax = fig.add_subplot(gs[i, j])
            ax.axis('off')
    
    # Adjust the layout
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Leave space for the title
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {output_file}")
    
    # Show the figure
    plt.show()

if __name__ == "__main__":
    args = parse_arguments()
    
    display_images(
        dataset_dir=args.dataset_dir,
        num_poses=args.num_poses,
        num_samples=args.num_samples,
        output_file=args.output_file,
        random_seed=args.random_seed,
        figsize=args.figsize
    ) 
