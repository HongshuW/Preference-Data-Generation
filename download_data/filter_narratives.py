import json

custom_dir = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data"
inner_labels_path = "\\open-images-v7\\train\\labels\\"

# Initialize a list to store the extracted data
captions_data = []

# Open the JSONL file and read line by line
with open(custom_dir + inner_labels_path + 'combined_filtered_narratives.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        # Parse the JSON object from the current line
        data = json.loads(line.strip())
        
        # Extract the image ID and caption
        image_id = data.get('image_id')
        caption = data.get('caption')

        print(image_id)
        print(caption)
        
        # Append the extracted data to the list
        if image_id and caption:
            captions_data.append({'image_id': image_id, 'caption': caption})


output_file_path = custom_dir + inner_labels_path + 'captions_data.jsonl'

with open(output_file_path, 'w', encoding='utf-8') as file:
    for entry in captions_data:
        # Convert the dictionary to a JSON string
        json_string = json.dumps(entry)
        # Write the JSON string followed by a newline character
        file.write(json_string + '\n')
