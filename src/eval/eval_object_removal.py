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

classes_info = base_folder + inner_meta_path + "classes.csv"
object_removal_records = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\remove_object\\labels.txt"
output_questions_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\caption_questions\\gpt_labeled\\"

baseline_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\baseline\\data\\"
PDG_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\remove_object\\data\\"

experiment_results_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\experiment_results\\gpt_labeled_benchmark_result.jsonl"

# prompt to identify question
prompt_header = "From the given questions, identify one question that is the most relevant to "
prompt_format = "Return the question number in the form of <n>."

# prompt to evaluate
eval_prompt = "Given the image, does the question answer to true or false? Return T for true and F for false. Do not include explanation."

# read classes data
df = pd.read_csv(classes_info, header=None)
classes = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

# read removal data
removal_data = dict()
with open(object_removal_records, 'r', encoding='utf-8') as file:
    for line in file:
        image_id, removed_object_label = line.strip().split(",")
        removal_data[image_id] = classes[removed_object_label]
    file.close()

# read processed data
processed_images = set()
with open(experiment_results_path, 'r', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line.strip())
        processed_images.add(data["image_id"])

# read image dataset
for filename in os.listdir(output_questions_path):
    if filename.endswith(".txt"):
        image_id = os.path.splitext(filename)[0]
        if image_id in processed_images:
            continue
        
        label = removal_data[image_id]

        # read questions
        questions = ""
        with open(output_questions_path + filename) as file:
            for line in file:
                questions += line
            file.close()

        # find the most suitable question
        prompt = prompt_header + "\"" + label + "\".\n" + questions + prompt_format
        print(prompt + "\n")
        response = llm.generate_gpt_response(prompt)
        print(response)

        # get target question
        try:
            question_id = response[response.index("<") + 1 : response.index(">")]
        except:
            print("error!")
            question_id = "1"
        
        statements = questions.split("\n")
        for s in statements:
            if "Question " + question_id + ": " in s:
                question_content = s.strip()
        
        if "N/A" in question_content:
            for s in statements:
                if "Claim " + question_id +": " in s:
                    question_content = s.strip() + "(True / False)"
        print(question_content)

        # load image processed by baseline and our approach
        original_response = llm.generate_response_with_image(base_folder + inner_data_path + image_id + ".jpg", eval_prompt + question_content)
        print("original: ")
        print(original_response)

        baseline_response = llm.generate_response_with_image(baseline_path + image_id + ".jpg", eval_prompt + question_content)
        print("baseline: ")
        print(baseline_response)

        PDG_response = llm.generate_response_with_image(PDG_path + image_id + ".jpg", eval_prompt + question_content)
        print("PDG: ")
        print(PDG_response)

        # record results
        result = dict()
        result["image_id"] = image_id
        result["label"] = label
        result["question"] = question_content
        result["original_image"] = original_response
        result["baseline_image"] = baseline_response
        result["PDG_image"] = PDG_response

        with open(experiment_results_path, 'a', encoding='utf-8') as file:
            json_string = json.dumps(result)
            file.write(json_string + '\n')
            file.close()

