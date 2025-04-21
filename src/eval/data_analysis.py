import json

experiment_results_path = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\experiment_results\\"

subfolders = ["object_presence", "object_relationship"]
result_files = ["gpt_labeled_benchmark_result.jsonl", "human_labeled_benchmark_result.jsonl"]


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

def setup_results_dictionary():
    results = dict()
    results["success"] = 0
    results["fail"] = 0
    return results

# baseline_results = setup_results_dictionary()
# pdg_results = setup_results_dictionary()

for folder in subfolders:
    
    baseline_results = setup_results_dictionary()
    pdg_results = setup_results_dictionary()
    
    for f in result_files:
        path = experiment_results_path + folder + "\\" + f
        results = read_jsonl(path)

        for entry in results:
            ground_truth = entry["original_image"]
            baseline = entry["baseline_image"]
            pdg = entry["PDG_image"]

            if ground_truth == 'T':
                if baseline == 'F':
                    baseline_results["success"] += 1
                else:
                    baseline_results["fail"] += 1
                if pdg == 'F':
                    pdg_results["success"] += 1
                else:
                    pdg_results["fail"] += 1
            else:
                continue
    
    baseline_success_rate = baseline_results["success"] / (baseline_results["success"] + baseline_results["fail"])
    pdg_success_rate = pdg_results["success"] / (pdg_results["success"] + pdg_results["fail"])

    print(folder)
    print("baseline success rate:")
    print(baseline_results)
    print(baseline_success_rate)
    print("pdg success rate:")
    print(pdg_results)
    print(pdg_success_rate)
