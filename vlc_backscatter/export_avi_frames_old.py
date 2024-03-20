import cv2
import os

# Replace 'your_video.avi' with the path to your AVI file
avi_file_path = r'video_export\1m_dark_new_60hz.avi'
folder_name = os.path.splitext(os.path.basename(avi_file_path))[0]
print(folder_name)
# Create a folder named after the AVI file
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Open the AVI file
cap = cv2.VideoCapture(avi_file_path)

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # Save each frame to the folder
        frame_file = os.path.join(folder_name, f'frame_{frame_count}.jpg')
        cv2.imwrite(frame_file, frame)
        frame_count += 1
    else:
        break

# Release the video capture object
cap.release()
