import os
import requests
import json

custom_dir = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data"
inner_data_path = "\\open-images-v7\\train\\data"
inner_meta_path = "\\open-images-v7\\train\\metadata\\"

# read image ids
image_ids = []
for filename in os.listdir(custom_dir + inner_data_path):
    if filename.endswith(".jpg"):
        image_id = os.path.splitext(filename)[0]  # remove .jpg
        image_ids.append(image_id)

# write to file
# with open(custom_dir + inner_meta_path + "downloaded_image_ids.txt", "w") as f:
#     for image_id in image_ids:
#         f.write(image_id + "\n")

image_ids = set(image_ids)

# download narratives
base_url = "https://storage.googleapis.com/localized-narratives/annotations/"
shards = [
    "open_images_train_v6_localized_narratives-00000-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00001-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00002-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00003-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00004-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00005-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00006-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00007-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00008-of-00010.jsonl",
    "open_images_train_v6_localized_narratives-00009-of-00010.jsonl",
]

# for shard in shards:
#     url = base_url + shard
#     destination_file = os.path.join(custom_dir + inner_meta_path, shard)
#     print(f"Downloading {shard} to {destination_file}...")
#     urllib.request.urlretrieve(url, destination_file)
#     print(f"Downloaded {shard}")

output_dir = custom_dir + inner_meta_path

for shard in shards:
    shard_url = base_url + shard
    response = requests.get(shard_url, stream=True)
    shard_name = shard_url.split("/")[-1]
    output_file = f"{output_dir}\\filtered_{shard_name}"
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        for line in response.iter_lines(decode_unicode=True):
            if line:
                narrative = json.loads(line)
                if narrative["image_id"] in image_ids:
                    outfile.write(json.dumps(narrative) + "\n")
    
    print(f"Filtered narratives saved to {output_file}")

combined_output_file = f"{output_dir}\\combined_filtered_narratives.jsonl"

with open(combined_output_file, "w", encoding="utf-8") as outfile:
    for shard in shards:
        filtered_file = f"{output_dir}\\filtered_{shard}"
        
        if os.path.exists(filtered_file):
            with open(filtered_file, "r", encoding="utf-8") as infile:
                for line in infile:
                    outfile.write(line)
            print(f"Added {filtered_file} to {combined_output_file}")
