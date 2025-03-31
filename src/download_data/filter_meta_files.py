import pandas as pd

custom_dir = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data"
inner_meta_path = "\\open-images-v7\\train\\metadata\\"
inner_labels_path = "\\open-images-v7\\train\\labels\\"

def filter_csv_by_image_ids(input_csv, output_csv, image_ids):
    """
    Filters rows in the input CSV file based on the provided image IDs and writes
    the filtered data to the output CSV file.

    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file where filtered data will be saved.
        image_ids (set): Set of image IDs to retain.
    """
    # Read the CSV file
    df = pd.read_csv(input_csv)

    # Filter rows where the 'ImageID' column matches one of the specified image IDs
    filtered_df = df[df['ImageID'].isin(image_ids)]

    # Write the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_csv, index=False)


# Load image IDs
with open(custom_dir + inner_meta_path + "downloaded_image_ids.txt") as f:
    image_ids = set(line.strip() for line in f)

# Define the paths to your metadata files
metadata_files = {
    "classifications.csv": "filtered_classifications.csv",
    "detections.csv": "filtered_detections.csv",
    "relationships.csv": "filtered_relationships.csv"
}

# Filter each metadata file
for input_csv, output_csv in metadata_files.items():
    input_csv = custom_dir + inner_labels_path + input_csv
    output_csv = custom_dir + inner_labels_path + output_csv
    filter_csv_by_image_ids(input_csv, output_csv, image_ids)
    print(f"Filtered data saved to {output_csv}")
