import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

dataset_dir = "yoga_dataset"  # Use yoga_dataset folder
yoga_poses_english_hindi_map = {
    "Tadasana (Mountain Pose)": "ताड़ासन",
    "Trikonasana (Triangle Pose)": "त्रिकोणासन",
    "Durvasana (Durva Grass Pose)": "दुर्वासन",
    "Ardha Chandrasana (Half Moon Pose)": "अर्धचंद्रासन",
    "Ustrasana (Camel Pose)": "उष्ट्रासन",
    "Dhanurasana (Bow Pose)": "धनुरासन",
    "Bhujangasana (Cobra Pose)": "भुजंगासन",
    "Maulasana (Garland Pose)": "मौलासन",
    "Halasana (Plow Pose)": "हलासन",
    "Setu Bandhasana (Bridge Pose)": "सेतुबंधासन"
}

fig = plt.figure(figsize=(15, 15))  # Adjust figure size as needed
rows = 3
cols = 4
plot_index = 1

for english_pose_name, hindi_pose_name in yoga_poses_english_hindi_map.items():
    original_dir = os.path.join(dataset_dir, hindi_pose_name, "original") # Access original folder
    if os.path.isdir(original_dir):
        image_files = [f for f in os.listdir(original_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if image_files:
            image_path = os.path.join(original_dir, image_files[0])  # Display first image of each pose
            img = mpimg.imread(image_path)

            ax = fig.add_subplot(rows, cols, plot_index)
            ax.imshow(img)
            ax.axis('off')
            ax.set_title(english_pose_name, fontsize=10)  # Use English pose name as title
            plot_index += 1

plt.tight_layout()
plt.show()
