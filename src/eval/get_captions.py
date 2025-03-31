import configparser
import json
import os

from ..utils import gpt_querier as llm

config = configparser.ConfigParser()
config.read('config.ini')
base_folder = config['DEFAULT']['DATA_SOURCE_FOLDER']
inner_labels_path = config['DEFAULT']['INNER_LABELS_PATH']
inner_data_path = config['DEFAULT']['INNER_DATA_PATH']

output_captions_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data\\open-images-v7\\train\\labels\\captions_generated_data.jsonl"
output_questions_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\caption_questions\\gpt_labeled\\"

prompt = "Briefly describe the image."


def read_captions_jsonl(filepath):
    data_instances = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                data_instances.append(data["image_id"])
            except json.JSONDecodeError as e:
                print(f"Skipping invalid line: {e}")
    return data_instances

def get_claims_and_questions(caption):
    prompt_header = "Split the following paragraph into claims, then convert each claim to a question that can be answered by True or False.\n"
    prompt_format = "\nReturn in the format:\n" + "<Claims>\n" + "<1>\n<2>\n...\n" + "<Questions>\n" + "<1>\n<2>\n...\n"

    prompt = prompt_header + "\"" + caption + "\"" + prompt_format
    print(prompt + "\n")
    response = llm.generate_gpt_response(prompt)
    print(response)

    return response

def extract_claims_and_questions(response, output_file):
    response = response.split("\n")

    claims = {}
    questions = {}
    current_section = None

    for line in response:
        line = line.strip()
        if line == "<Claims>":
            current_section = "claims"
            continue
        elif line == "<Questions>":
            current_section = "questions"
            continue
        elif line == "" or line == "</Claims>" or line == "</Questions>":
            current_section = None
            continue

        if current_section and line.startswith("<") and ">" in line:
            num_end = line.find(">")
            number = line[1:num_end].strip()
            text = line[num_end+1:].strip()
            if current_section == "claims":
                claims[number] = text
            elif current_section == "questions":
                questions[number] = text

    with open(output_file, 'w', encoding='utf-8') as file:
        for number in sorted(claims.keys(), key=int):
            claim = claims.get(number, "N/A")
            question = questions.get(number, "N/A")
            file.write(f"Claim {number}: {claim}\n")
            file.write(f"Question {number}: {question}\n")
            file.write("\n")

# images to skip
captions_file = base_folder + inner_labels_path + 'captions_data.jsonl'
processed_images = set(read_captions_jsonl(captions_file))

# read images
for filename in os.listdir(base_folder + inner_data_path):
    if filename.endswith(".jpg"):
        image_id = os.path.splitext(filename)[0]
        if image_id in processed_images:
            continue

        caption = llm.generate_response_with_image(base_folder + inner_data_path + filename, prompt)
        print(caption)

        entry = dict()
        entry["image_id"] = image_id
        entry["caption"] = caption

        with open(output_captions_path, 'a', encoding='utf-8') as file:
            json_string = json.dumps(entry)
            file.write(json_string + '\n')
            file.close()

        response = get_claims_and_questions(caption)
        extract_claims_and_questions(response, output_questions_path + image_id + ".txt")
