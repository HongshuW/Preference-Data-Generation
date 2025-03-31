import configparser
import pandas as pd
import random
import json

from ..utils import gpt_querier as llm

config = configparser.ConfigParser()
config.read('config.ini')
base_folder = config['DEFAULT']['DATA_SOURCE_FOLDER']
inner_labels_path = config['DEFAULT']['INNER_LABELS_PATH']
inner_data_path = config['DEFAULT']['INNER_DATA_PATH']
inner_meta_path = config['DEFAULT']['INNER_META_PATH']

output_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\caption_questions\\object_relationship\\human_labeled.jsonl"

prompt_header = "Given the following text, what is the relationship between "
prompt_format = "\nReturn the relationship as a short sentence without explanation. It should be in the format \"<A> <R> <B>\", where <A> and <B> are the two given objects in the given sequence, <R> is a relationship chosen from: <on the left of>, <on the right of>, <above>, <below>, <inside>, <contains>\nReturn N/A if there is no relationship."

question_prompt_header = "Given the following relationship, convert it to a question that can be answered by True or False.\n"
question_prompt_format = "\nReturn the question as one sentence only."

def read_captions_jsonl(filepath):
    data_instances = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                data_instances.append(data)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid line: {e}")
    return data_instances


# read classes data
classes_info = base_folder + inner_meta_path + "classes.csv"
df = pd.read_csv(classes_info, header=None)
classes = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

# read bounding boxes
bounding_boxes = pd.read_csv(base_folder + inner_labels_path + "filtered_detections.csv")

# read caption data
captions_file = base_folder + inner_labels_path + 'captions_data.jsonl'
captions_data = read_captions_jsonl(captions_file)

# all supported relationships
supported_relationships = {"left", "right", "above", "below", "inside", "contains"}

for entry in captions_data:
    image_id = entry["image_id"]
    caption = entry["caption"]

    # get all labels from this image
    relative_rows = bounding_boxes[bounding_boxes["ImageID"] == image_id]
    original_labels = list(relative_rows['LabelName'].unique())
    if len(original_labels) < 2:
        continue

    # randomly choose two labels are ask for their relationship
    two_items = random.sample(original_labels, 2)
    labels = []
    for l in two_items:
        labels.append(classes[l])
    
    # generate question about relationship
    prompt = prompt_header + "\"" + labels[0] + "\" and \"" + labels[1] + "\"?\n\"" + caption + "\""
    prompt += prompt_format
    print(prompt + "\n")

    relationship = llm.generate_gpt_response(prompt)
    print(relationship + "\n")
    
    relationship = relationship.strip()
    if "N/A" in relationship:
        continue

    extracted_relationship = None
    for r in supported_relationships:
        if not r in relationship:
            continue
        else:
            extracted_relationship = r
            break
    if not extracted_relationship:
        continue

    question_prompt = question_prompt_header + "\"" + relationship + "\"" + question_prompt_format
    print(question_prompt + "\n")
    question = llm.generate_gpt_response(question_prompt)
    print(question + "\n")

    entry = dict()
    entry["image_id"] = image_id
    entry["caption"] = caption
    entry["label1"] = two_items[0]
    entry["label2"] = two_items[1]
    entry["text_label1"] = labels[0]
    entry["text_label2"] = labels[1]
    entry["relationship"] = extracted_relationship
    entry["question"] = question
    with open(output_path, 'a', encoding='utf-8') as file:
        json_string = json.dumps(entry)
        file.write(json_string + '\n')
        file.close()
