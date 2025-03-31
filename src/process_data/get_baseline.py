import cv2
import numpy as np
import pandas as pd
import os


custom_dir = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data"
inner_data_path = "\\open-images-v7\\train\\data\\"

output_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\baseline\\data\\"

scaling_factor = 0.80 ** 0.5


for filename in os.listdir(custom_dir + inner_data_path):
    if filename.endswith(".jpg"):
        image_id = os.path.splitext(filename)[0]  # remove .jpg

        # get image info
        image_path = custom_dir + inner_data_path + filename
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        crop_width = int(width * scaling_factor)
        crop_height = int(height * scaling_factor)

        # Calculate cropping box
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        right = (width + crop_width) // 2
        bottom = (height + crop_height) // 2

        # Crop the image
        cropped_image = image[top:bottom, left:right]
        cv2.imwrite(output_path + filename, cropped_image)
