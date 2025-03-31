import pandas as pd

custom_dir = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data"
inner_meta_path = "\\open-images-v7\\train\\metadata\\"
inner_labels_path = "\\open-images-v7\\train\\labels\\"


# Load metadata
classifications_df = pd.read_csv(custom_dir + inner_labels_path + 'filtered_classifications.csv')
classification_image_ids = set(classifications_df['ImageID'].unique())

detections_df = pd.read_csv(custom_dir + inner_labels_path + 'filtered_detections.csv')
detection_image_ids = set(detections_df['ImageID'].unique())

relationships_df = pd.read_csv(custom_dir + inner_labels_path + 'filtered_relationships.csv')
relationship_image_ids = set(relationships_df['ImageID'].unique())

# read image IDs
with open(custom_dir + inner_meta_path + "downloaded_image_ids.txt") as f:
    all_image_ids = set(line.strip() for line in f)


# Determine Missing Image IDs for Each Metadata File
missing_from_classifications = all_image_ids - classification_image_ids
missing_from_detections = all_image_ids - detection_image_ids
missing_from_relationships = all_image_ids - relationship_image_ids

def write_missing_ids(missing_ids, filename):
    with open(filename, 'w') as f:
        for image_id in sorted(missing_ids):
            f.write(f"{image_id}\n")

# Save missing image IDs
write_missing_ids(missing_from_classifications, custom_dir + inner_meta_path + 'missing_from_classifications.txt')
write_missing_ids(missing_from_detections, custom_dir + inner_meta_path + 'missing_from_detections.txt')
write_missing_ids(missing_from_relationships, custom_dir + inner_meta_path + 'missing_from_relationships.txt')
