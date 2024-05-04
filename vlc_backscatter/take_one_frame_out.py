import cv2
import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Convert AVI videos to frames.')
parser.add_argument('folder_path', type=str, help='Path to the folder containing AVI files.')

# Parse arguments
args = parser.parse_args()

# Function to process each AVI file
def process_avi_file(avi_file_path):
    folder_name = os.path.splitext(os.path.basename(avi_file_path))[0]
    folder_path = os.path.join(os.path.dirname(avi_file_path), folder_name)
    
    # Create a folder named after the AVI file if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
        # Open the AVI file
        cap = cv2.VideoCapture(avi_file_path)
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Save each frame to the folder
                frame_file = os.path.join(folder_path, f'frame_{frame_count}.jpg')
                cv2.imwrite(frame_file, frame)
                frame_count += 1
            else:
                break
                
        # Release the video capture object
        cap.release()
    else:
        print(f"Frames for '{avi_file_path}' are already extracted.")

# Iterate over all files in the given folder and process AVI files
for file in os.listdir(args.folder_path):
    if file.endswith(".avi"):
        avi_file_path = os.path.join(args.folder_path, file)
        process_avi_file(avi_file_path)
