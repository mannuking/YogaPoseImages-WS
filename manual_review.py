import os
import sys
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import shutil
import argparse
import json

class ImageReviewApp:
    def __init__(self, root, input_dir, output_dir, review_file=None):
        self.root = root
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.review_file = review_file
        
        # Initialize image list
        self.image_paths = []
        self.current_index = 0
        self.decisions = {}
        
        # Load previous review session if file exists
        if review_file and os.path.exists(review_file):
            try:
                with open(review_file, 'r') as f:
                    self.decisions = json.load(f)
                print(f"Loaded {len(self.decisions)} previous decisions from {review_file}")
            except Exception as e:
                print(f"Error loading review file: {e}")
        
        # Collect all images
        self._collect_images()
        
        # Set up the UI
        self._setup_ui()
        
        # Load the first image
        if self.image_paths:
            self._load_image(self.current_index)
        else:
            self._show_message("No images found in the input directory.")
    
    def _collect_images(self):
        """Collect all image paths from the input directory."""
        for root, _, files in os.walk(self.input_dir):
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    path = os.path.join(root, filename)
                    self.image_paths.append(path)
        
        print(f"Found {len(self.image_paths)} images to review")
        
        # Sort images by path for consistent ordering
        self.image_paths.sort()
        
        # Skip images that have already been decided
        if self.decisions:
            remaining = [p for p in self.image_paths if p not in self.decisions]
            decided = [p for p in self.image_paths if p in self.decisions]
            print(f"Already decided: {len(decided)} images")
            print(f"Remaining: {len(remaining)} images")
            
            # Ask if user wants to review already decided images
            if decided and remaining:
                review_decided = input("Do you want to review already decided images? (y/n): ").lower() == 'y'
                if not review_decided:
                    self.image_paths = remaining
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.root.title("Yoga Pose Image Review")
        self.root.geometry("1200x800")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image frame
        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Image canvas
        self.canvas = tk.Canvas(self.image_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        # Image info
        self.info_label = ttk.Label(info_frame, text="", font=("Arial", 12))
        self.info_label.pack(side=tk.LEFT, padx=10)
        
        # Progress info
        self.progress_label = ttk.Label(info_frame, text="", font=("Arial", 12))
        self.progress_label.pack(side=tk.RIGHT, padx=10)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        self.prev_button = ttk.Button(button_frame, text="Previous (Left Arrow)", command=self._prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.reject_button = ttk.Button(button_frame, text="Reject (R)", command=lambda: self._decide("reject"))
        self.reject_button.pack(side=tk.LEFT, padx=5)
        
        self.accept_button = ttk.Button(button_frame, text="Accept (A)", command=lambda: self._decide("accept"))
        self.accept_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(button_frame, text="Next (Right Arrow)", command=self._next_image)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(button_frame, text="Save Progress (S)", command=self._save_progress)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # Keyboard bindings
        self.root.bind("<Left>", lambda e: self._prev_image())
        self.root.bind("<Right>", lambda e: self._next_image())
        self.root.bind("a", lambda e: self._decide("accept"))
        self.root.bind("r", lambda e: self._decide("reject"))
        self.root.bind("s", lambda e: self._save_progress())
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _load_image(self, index):
        """Load and display the image at the given index."""
        if 0 <= index < len(self.image_paths):
            path = self.image_paths[index]
            
            try:
                # Load image with OpenCV for display
                img = cv2.imread(path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Get image dimensions
                h, w, _ = img.shape
                
                # Resize image to fit canvas while maintaining aspect ratio
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    # Calculate scaling factor
                    scale_w = canvas_width / w
                    scale_h = canvas_height / h
                    scale = min(scale_w, scale_h)
                    
                    # Resize image
                    new_width = int(w * scale)
                    new_height = int(h * scale)
                    img_resized = cv2.resize(img, (new_width, new_height))
                    
                    # Convert to PhotoImage
                    img_pil = Image.fromarray(img_resized)
                    self.photo = ImageTk.PhotoImage(image=img_pil)
                    
                    # Clear canvas and display image
                    self.canvas.delete("all")
                    self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo, anchor=tk.CENTER)
                    
                    # Update info labels
                    pose_name = os.path.basename(os.path.dirname(path))
                    file_name = os.path.basename(path)
                    self.info_label.config(text=f"Pose: {pose_name} | File: {file_name} | Size: {w}x{h}")
                    
                    # Update progress label
                    progress = f"Image {index+1} of {len(self.image_paths)}"
                    if path in self.decisions:
                        decision = self.decisions[path]
                        progress += f" | Decision: {decision.capitalize()}"
                    self.progress_label.config(text=progress)
                    
                    # Update status
                    self.status_var.set(f"Loaded image: {path}")
                else:
                    # Canvas not ready yet, try again after a short delay
                    self.root.after(100, lambda: self._load_image(index))
            except Exception as e:
                self._show_message(f"Error loading image {path}: {e}")
    
    def _next_image(self):
        """Move to the next image."""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self._load_image(self.current_index)
    
    def _prev_image(self):
        """Move to the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self._load_image(self.current_index)
    
    def _decide(self, decision):
        """Record a decision for the current image."""
        if self.image_paths:
            path = self.image_paths[self.current_index]
            self.decisions[path] = decision
            
            # Update progress label
            progress = f"Image {self.current_index+1} of {len(self.image_paths)} | Decision: {decision.capitalize()}"
            self.progress_label.config(text=progress)
            
            # Save decision to file
            self._save_progress()
            
            # Move to next image if available
            if self.current_index < len(self.image_paths) - 1:
                self._next_image()
            else:
                self._show_message("Reached the end of the image list. All images have been reviewed.")
                self._apply_decisions()
    
    def _save_progress(self):
        """Save the current decisions to a file."""
        if self.review_file:
            try:
                with open(self.review_file, 'w') as f:
                    json.dump(self.decisions, f, indent=2)
                self.status_var.set(f"Progress saved to {self.review_file}")
            except Exception as e:
                self._show_message(f"Error saving progress: {e}")
    
    def _apply_decisions(self):
        """Apply the decisions by copying accepted images to the output directory."""
        accepted = [path for path, decision in self.decisions.items() if decision == "accept"]
        
        if not accepted:
            self._show_message("No images were accepted.")
            return
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Copy accepted images
            for path in accepted:
                # Get relative path to maintain directory structure
                rel_path = os.path.relpath(path, self.input_dir)
                dest_path = os.path.join(self.output_dir, rel_path)
                
                # Create destination directory if it doesn't exist
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy the file
                shutil.copy2(path, dest_path)
            
            self._show_message(f"Applied decisions: {len(accepted)} images copied to {self.output_dir}")
        except Exception as e:
            self._show_message(f"Error applying decisions: {e}")
    
    def _show_message(self, message):
        """Show a message in the status bar and print to console."""
        print(message)
        self.status_var.set(message)

def main():
    parser = argparse.ArgumentParser(description='Manually review and select yoga pose images')
    parser.add_argument('input_dir', help='Path to the input directory containing images to review')
    parser.add_argument('output_dir', help='Path to the output directory where accepted images will be copied')
    parser.add_argument('--review-file', default='review_decisions.json', help='Path to the file to save review decisions')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist or is not a directory.")
        sys.exit(1)
    
    # Create Tkinter root window
    root = tk.Tk()
    app = ImageReviewApp(root, args.input_dir, args.output_dir, args.review_file)
    
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
