# Preference Data Generation

This repository is for CS6240 course project.

## Repo Structure
|- data\
|- download_data\
&nbsp;&nbsp;|- load_data.py\
&nbsp;&nbsp;|- load_data_narratives.py\
|- process_data.py\
|- README.md

### Data
- The `data` folder contains a benchmark of 100 images retrieved from Open Images V7 dataset. This folder contains all the data used for this project.

### Data Replication
Modify the `custom_dir` variable to download to a custom folder in the following files:

- `load_data.py` downloads images with `detections`, `classifications`, `relationships` labels. 
- `load_data_narratives.py` downloads narratives of the images.
- `filter_meta_files.py` filter the labels by downloaded image IDs.

### Baseline
TODO

### Our approach
TODO
