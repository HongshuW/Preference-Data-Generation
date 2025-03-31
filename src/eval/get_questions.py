import configparser
import json

from ..utils import gpt_querier as llm

config = configparser.ConfigParser()
config.read('config.ini')
base_folder = config['DEFAULT']['DATA_SOURCE_FOLDER']
inner_labels_path = config['DEFAULT']['INNER_LABELS_PATH']

output_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\caption_questions\\"

prompt_header = "Split the following paragraph into claims, then convert each claim to a question that can be answered by True or False.\n"
prompt_format = "\nReturn in the format:\n" + "<Claims>\n" + "<1>\n<2>\n...\n" + "<Questions>\n" + "<1>\n<2>\n...\n"

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

# read caption data
captions_file = base_folder + inner_labels_path + 'captions_data.jsonl'
captions_data = read_captions_jsonl(captions_file)

for entry in captions_data:
    image_id = entry["image_id"]
    caption = entry["caption"]

    # call llm
    prompt = prompt_header + "\"" + caption + "\"" + prompt_format
    print(prompt + "\n")
    response = llm.generate_gpt_response(prompt)
    print(response)

    # process response
    extract_claims_and_questions(response, output_path + image_id + ".txt")
