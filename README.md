# Preference Data Generation

This repository is for CS6240 course project.

## Repo Structure
|- data\
|- remove_object\
|- download_data\
&nbsp;&nbsp;|- load_data.py\
&nbsp;&nbsp;|- load_data_narratives.py\
&nbsp;&nbsp;|- filter_meta_files.py\
&nbsp;&nbsp;|- find_images_with_missing_labels.py\
|- process_data\
&nbsp;&nbsp;|- process_data.py\
|- README.md

### Original Data
- The `data` folder contains a benchmark of 100 images retrieved from Open Images V7 dataset. This folder contains all the data used for this project.
- The dataset can be used directly, to replicate the dataset, please refer to "Data Replication".

### Original Data Replication
To replicate the dataset, execute the scripts in the following order.
Modify the `custom_dir` variable to download to a custom folder in the following files:

- `load_data.py` downloads images with `detections`, `classifications`, `relationships` labels. 
- `load_data_narratives.py` downloads narratives of the images.
- `filter_meta_files.py` filter the labels by downloaded image IDs.
- `find_images_with_missing_labels.py` checks and records which images contain missing labels.

## Baseline
TODO

## Our approach
- The `remove_object` folder contains processed images, each with a removed object.
- `labels.txt` in this folder records the label of the removed object in each image.
