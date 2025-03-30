import fiftyone as fo
import fiftyone.zoo as foz

custom_dir = "C:\\Users\\admin\\repos\\Preference-Data-Generation\\data"

fo.config.dataset_zoo_dir = custom_dir

dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    max_samples=100,
    label_types=["detections", "classifications", "relationships"],
    classes=["Cat", "Dog", "Bird"],
    seed=20,
)
