import configparser
import os
import json
import pandas as pd
import cv2
import numpy as np
import random

config = configparser.ConfigParser()
config.read('config.ini')
base_folder = config['DEFAULT']['DATA_SOURCE_FOLDER']
inner_labels_path = config['DEFAULT']['INNER_LABELS_PATH']
inner_data_path = config['DEFAULT']['INNER_DATA_PATH']
inner_meta_path = config['DEFAULT']['INNER_META_PATH']

relationship_info_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\caption_questions\\object_relationship\\human_labeled.jsonl"
output_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\modify_relationship\\data\\"

def read_jsonl(filepath):
    data_instances = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                data_instances.append(data)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid line: {e}")
    return data_instances

def extract_object(image, bbox):
    x_min, y_min, x_max, y_max = bbox
    return image[y_min:y_max, x_min:x_max].copy()

def paste_object(image, obj, bbox):
    x_min, y_min, x_max, y_max = bbox
    target_h = y_max - y_min
    target_w = x_max - x_min

    # Resize object to match target area
    resized_obj = cv2.resize(obj, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

    image[y_min:y_max, x_min:x_max] = resized_obj
    return image

def swap_bounding_boxes(image, bbox1, bbox2):
    # Extract object regions
    obj1 = extract_object(image, bbox1)
    obj2 = extract_object(image, bbox2)

    # # Ensure sizes are the same
    # h1, w1 = obj1.shape[:2]
    # h2, w2 = obj2.shape[:2]

    # if (h1, w1) != (bbox2[3] - bbox2[1], bbox2[2] - bbox2[0]) or \
    #    (h2, w2) != (bbox1[3] - bbox1[1], bbox1[2] - bbox1[0]):
    #     raise ValueError("Bounding box sizes do not match extracted region sizes")

    # Swap the objects
    image = paste_object(image, obj1, bbox2)
    image = paste_object(image, obj2, bbox1)
    return image

def move_inner_box_outside(image, outer_bbox, inner_bbox):
    h, w = image.shape[:2]
    obj = extract_object(image, inner_bbox)

    box_width = inner_bbox[2] - inner_bbox[0]
    box_height = inner_bbox[3] - inner_bbox[1]

    # Define outer bounding box edges
    x0, y0, x1, y1 = outer_bbox

    # Possible zones: left, right, top, bottom
    zones = []
    if x0 - box_width > 0:
        zones.append('left')
    if x1 + box_width < w:
        zones.append('right')
    if y0 - box_height > 0:
        zones.append('top')
    if y1 + box_height < h:
        zones.append('bottom')

    if not zones:
        raise ValueError("not enough space")

    direction = random.choice(zones)

    if direction == 'left':
        x_min = random.randint(0, x0 - box_width)
        y_min = random.randint(0, h - box_height)
    elif direction == 'right':
        x_min = random.randint(x1, w - box_width)
        y_min = random.randint(0, h - box_height)
    elif direction == 'top':
        x_min = random.randint(0, w - box_width)
        y_min = random.randint(0, y0 - box_height)
    elif direction == 'bottom':
        x_min = random.randint(0, w - box_width)
        y_min = random.randint(y1, h - box_height)

    x_max = x_min + box_width
    y_max = y_min + box_height

    # Zero out the original inner object
    image[inner_bbox[1]:inner_bbox[3], inner_bbox[0]:inner_bbox[2]] = 0

    # Paste at new location
    image = paste_object(image, obj, (x_min, y_min, x_max, y_max))

    return image, (x_min, y_min, x_max, y_max)

def boxes_match_relationship(b1, b2, relationship):
    x1_min, y1_min, x1_max, y1_max = b1
    x2_min, y2_min, x2_max, y2_max = b2

    if relationship == "left":
        return x1_min <= x2_min
    elif relationship == "right":
        return x1_max >= x2_max
    elif relationship == "above":
        return y1_min <= y2_min
    elif relationship == "below":
        return y1_max >= y2_max
    elif relationship == "inside":
        return (x1_min >= x2_min and y1_min >= y2_min and
                x1_max <= x2_max and y1_max <= y2_max)
    elif relationship == "contains":
        return (x2_min >= x1_min and y2_min >= y1_min and
                x2_max <= x1_max and y2_max <= y1_max)
    else:
        raise ValueError(f"Unsupported relationship: {relationship}")

def scale_bounding_boxes(image, row):
    height, width = image.shape[:2]

    x_min_norm = row['XMin']
    x_max_norm = row['XMax']
    y_min_norm = row['YMin']
    y_max_norm = row['YMax']

    x_min = int(x_min_norm * width)
    x_max = int(x_max_norm * width)
    y_min = int(y_min_norm * height)
    y_max = int(y_max_norm * height)

    return (x_min, y_min, x_max, y_max)

def find_matching_pair(df, label1, label2, relationship, image):
    boxes1 = df[df['LabelName'] == label1]
    boxes2 = df[df['LabelName'] == label2]

    print(boxes1)
    print(boxes2)

    for _, row1 in boxes1.iterrows():
        b1 = (row1['XMin'], row1['YMin'], row1['XMax'], row1['YMax'])
        for _, row2 in boxes2.iterrows():
            b2 = (row2['XMin'], row2['YMin'], row2['XMax'], row2['YMax'])
            if boxes_match_relationship(b1, b2, relationship):
                b1 = scale_bounding_boxes(image, row1)
                b2 = scale_bounding_boxes(image, row2)
                return {
                    "label1_box": b1,
                    "label2_box": b2,
                    "label1_row": row1,
                    "label2_row": row2
                }

    return None


# read bounding boxes
bounding_boxes = pd.read_csv(base_folder + inner_labels_path + "filtered_detections.csv")

# all supported relationships
supported_relationships = {"left", "right", "above", "below", "inside", "contains"}
to_swap = {"left", "right", "above", "below"}

relationship_info = read_jsonl(relationship_info_path)
for entry in relationship_info:
    image_id = entry["image_id"]
    label1 = entry["label1"]
    label2 = entry["label2"]
    relationship = entry["relationship"]

    print(relationship)

    # get rows with relevant labels
    relevant_rows = bounding_boxes[bounding_boxes["ImageID"] == image_id]
    label_rows = relevant_rows[(relevant_rows["LabelName"] == label1) | (relevant_rows["LabelName"] == label2)]

    # get a pair that follows the relationship
    image = cv2.imread(base_folder + inner_data_path + image_id + ".jpg")
    pair = find_matching_pair(label_rows, label1, label2, relationship, image)

    if pair:
        print("Match found!")
        print("Label1 box:", pair['label1_box'])
        print("Label2 box:", pair['label2_box'])
    else:
        print("No matching pair found for the given relationship.")
        continue
    
    # process image
    bbox1 = pair['label1_box']
    bbox2 = pair['label2_box']
    
    try:
        if relationship in to_swap:
            # Swap positions
            output_img = swap_bounding_boxes(image.copy(), bbox1, bbox2)
        elif relationship == "inside":
        # Move inner box outside
            output_img, new_bbox = move_inner_box_outside(image.copy(), bbox2, bbox1)  # assume bbox1 inside bbox2
        elif relationship == "contains":
            # Move inner box outside
            output_img, new_bbox = move_inner_box_outside(image.copy(), bbox1, bbox2)  # assume bbox2 inside bbox1
        cv2.imwrite(output_path + image_id + ".jpg", output_img)
    except:
        continue
    