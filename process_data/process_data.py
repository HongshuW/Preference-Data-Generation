import cv2
import numpy as np
import pandas as pd
import os


custom_dir = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data"
inner_data_path = "\\open-images-v7\\train\\data\\"
inner_labels_path = "\\open-images-v7\\train\\labels\\"

output_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\remove_object\\data\\"
output_label_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\remove_object\\labels.txt"

def remove_smallest_object(image_path, bounding_boxes, labels, output_label_path, image_id):
    """
    Removes the object with the smallest bounding box area from the image and saves its label to a file.

    Args:
        image_path (str): Path to the input image.
        bounding_boxes (list of tuples): List of bounding boxes, each defined as (x_min, y_min, x_max, y_max).
        labels (list of str): List of labels corresponding to each bounding box.
        output_label_path (str): Path to the file where the label of the removed object will be saved.

    Returns:
        np.array: Image with the smallest object removed.
    """
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Image at {image_path} could not be loaded.")

    if not bounding_boxes or not labels:
        raise ValueError("Bounding boxes and labels must be provided.")

    if len(bounding_boxes) != len(labels):
        raise ValueError("Each bounding box must have a corresponding label.")

    # Calculate the area of each bounding box and find the one with the smallest area
    smallest_area = float('inf')
    smallest_bbox = None
    smallest_label = None

    for bbox, label in zip(bounding_boxes, labels):
        x_min, y_min, x_max, y_max = bbox
        area = (x_max - x_min) * (y_max - y_min)
        if area < smallest_area:
            smallest_area = area
            smallest_bbox = bbox
            smallest_label = label

    if smallest_bbox is None or smallest_label is None:
        raise ValueError("No valid bounding box or label found.")

    # Save the label of the removed object to the specified file
    with open(output_label_path, 'a') as file:
        file.write(image_id)
        file.write(',')
        file.write(smallest_label)
        file.write('\n')

    # Create a mask for the selected bounding box
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    x_min, y_min, x_max, y_max = smallest_bbox
    mask[y_min:y_max, x_min:x_max] = 255

    # Apply inpainting to remove the object
    inpainted_image = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    return inpainted_image


for filename in os.listdir(custom_dir + inner_data_path):
    if filename.endswith(".jpg"):
        image_id = os.path.splitext(filename)[0]  # remove .jpg

        # get image info
        image_path = custom_dir + inner_data_path + filename
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        # Load bounding box data
        detections_df = pd.read_csv(custom_dir + inner_labels_path + 'filtered_detections.csv')
        image_detections = detections_df[detections_df['ImageID'] == image_id]

        bounding_boxes = []
        labels = []

        for index, row in image_detections.iterrows():
            x_min_norm = row['XMin']
            x_max_norm = row['XMax']
            y_min_norm = row['YMin']
            y_max_norm = row['YMax']

            x_min = int(x_min_norm * width)
            x_max = int(x_max_norm * width)
            y_min = int(y_min_norm * height)
            y_max = int(y_max_norm * height)

            label = row['LabelName']
            bounding_boxes.append((x_min, y_min, x_max, y_max))
            labels.append(label)

        print(bounding_boxes)

        # Save result
        output_image = remove_smallest_object(image_path, bounding_boxes, labels, output_label_path, image_id)
        cv2.imwrite(output_path + filename, output_image)
