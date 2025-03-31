import configparser
import os
import json
import pandas as pd

from ..utils import gpt_querier as llm

config = configparser.ConfigParser()
config.read('config.ini')
base_folder = config['DEFAULT']['DATA_SOURCE_FOLDER']
inner_labels_path = config['DEFAULT']['INNER_LABELS_PATH']
inner_data_path = config['DEFAULT']['INNER_DATA_PATH']
inner_meta_path = config['DEFAULT']['INNER_META_PATH']

questions_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\caption_questions\\object_relationship\\human_labeled.jsonl"

baseline_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\baseline\\data\\"
PDG_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\modify_relationship\\data\\"

experiment_results_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\experiment_results\\object_relationship\\human_labeled_benchmark_result.jsonl"

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

# prompt to evaluate
eval_prompt = "Given the image, does the question answer to true or false? Return T for true and F for false. Do not include explanation."

# read image dataset
questions_data = read_jsonl(questions_path)
for entry in questions_data:
    image_id = entry["image_id"]
    question = entry["question"]
    print(question)

    # load image processed by baseline and our approach
    try:
        PDG_response = llm.generate_response_with_image(PDG_path + image_id + ".jpg", eval_prompt + question)
        print("PDG: ")
        print(PDG_response)

        original_response = llm.generate_response_with_image(base_folder + inner_data_path + image_id + ".jpg", eval_prompt + question)
        print("original: ")
        print(original_response)

        baseline_response = llm.generate_response_with_image(baseline_path + image_id + ".jpg", eval_prompt + question)
        print("baseline: ")
        print(baseline_response)
    except:
        continue

    # record results
    result = dict()
    result["image_id"] = image_id
    result["question"] = question
    result["original_image"] = original_response
    result["baseline_image"] = baseline_response
    result["PDG_image"] = PDG_response

    with open(experiment_results_path, 'a', encoding='utf-8') as file:
        json_string = json.dumps(result)
        file.write(json_string + '\n')
        file.close()

