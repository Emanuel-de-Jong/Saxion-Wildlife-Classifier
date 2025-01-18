'''
This script is used to filter out the images of animals that have less than 200 images.
It will then create a data.json file that contains the animal name,
the amount of images it has and the amount of images it needs.
Created by Simon Vermaat
'''

import os
import json
import numpy as np

def count_augmented_animals(animal):
    count = 0
    path =  f"augmented_output/{animal}"
    if os.path.isdir(path):
        count = len([name for name in os.listdir(path) if name.endswith(".jpg")])        
    return count

input_path = "Input_images"

animal_list = ['miscellaneous','duck','goose','duckling','gosling','hare','rabbit','ice_diver','egyptian_goose','egyptian_gosling','coot','swan','crow','pidgeon',
                   'magpie','cat','oystercatcher','lapwing','starling','redshank','skylark','meadow_pipit','godwit','shoveler','summer_teal','tufted_duck','gadwall',
                   'fox','buzzard','goshawk','harrier','sparrowhawk','beech_marten','polecat','weasel','ermine','rat','jackdaw','raven','greylag_goose','canadian_goose',
                   'wagtail','blackbird','moorhen','common_shelduck','black_headed_seagull','heron','pheasant','stork','dog','swallow','tit','orinoco_goose','singing_bushlark',
                   'seagull', 'pheasant_female', 'kestrel']

annotation_count_dictionary_day = {key: 0 for key in animal_list}
annotation_dictionary_day = {key: [] for key in animal_list}
annotation_count_dictionary_night = {key: 0 for key in animal_list}
annotation_dictionary_night = {key: [] for key in animal_list}
image_annotation_sizes = {}

for root, dirs, files in os.walk(input_path):  
    for directory in dirs:
        sub_path = os.path.join(root, directory)
        for sub_root, sub_dirs, sub_files in os.walk(sub_path):
            for directory in sub_dirs:
                sub_sub_path = os.path.join(sub_root, directory)
                for file in os.listdir(sub_sub_path):
                    if file.startswith("coco_annotations") and file.endswith(".json"):
                        file_path = os.path.join(sub_sub_path, file)  
                        with open(file_path, 'r') as json_file:
                            json_data = json.load(json_file)
                            print(f"Loaded JSON data from {file_path}")
                        break
                category_dict = {}
                image_dict = {}
                for category in json_data["categories"]:
                    category_dict[category["id"]] = category["name"]
                for image in json_data["images"]:
                    image_dict[image["id"]] = image["file_name"]
                    image_path = sub_sub_path + "\\" + image["file_name"]
                    image_annotation_sizes[image_path] = [image["width"],image["height"]]
                for annotation in json_data["annotations"]:
                    animal = category_dict[annotation["category_id"]]
                    if animal == "raven":
                        continue
                    if animal == "animal" :
                        animal = "miscellaneous"
                    if animal == "egyptian_gosling":
                        animal = "gosling"
                    new_annotation = annotation
                    new_annotation["category_id"] = (animal_list.index(animal)+1)
                    image_path = sub_sub_path + "\\" + image_dict[annotation["image_id"]]
                    annotation_image = {
                        "annotation": annotation,
                        "image_path": image_path
                        }
                    annotation_dictionary_day[animal].append(annotation_image)
                    annotation_count_dictionary_day[animal] += 1


# Array of animals
animals = [
    "moorhen",
    "blackbird",
    "pheasant_female",
    "dog",
    "black_headed_seagull",
    "wagtail",
    "stork",
    "rabbit",
    "polecat",
    "kestrel",
    "duckling",
    "pheasant",
    "coot",
    "swallow",
    "redshank",
    "weasel",
    "common_shelduck",
    "buzzard",
    "singing_bushlark",
    "rat",
    "fox",
    "goose",
    "orinoco_goose",
    "tit",
    "lapwing",
    "gadwall",
    "goshawk",
    "ermine"
]

import shutil
import os

# Process each animal in the array
for animal in animals:
    # Create target directory if it doesn't exist
    target_dir = f"animals/{animal}"
    os.makedirs(target_dir, exist_ok=True)

    # Extract image paths into an array
    animal_paths = [item["image_path"] for item in annotation_dictionary_day[animal]]

    # Copy each image to target directory
    for image_path in animal_paths:
        shutil.copy2(image_path, target_dir)

    # Create new COCO format JSON structure
    new_json = {
        "categories": [{"id": 1, "name": animal}],
        "images": [],
        "annotations": []
    }

    # Keep track of new image IDs
    image_id_map = {}
    next_image_id = 1
    next_annotation_id = 1

    # Process each animal annotation
    for item in annotation_dictionary_day[animal]:
        image_path = item["image_path"]
        base_image_name = os.path.basename(image_path)
        
        # Add image entry if not already added
        if image_path not in image_id_map:
            image_id_map[image_path] = next_image_id
            new_json["images"].append({
                "id": next_image_id,
                "file_name": base_image_name,
                "width": image_annotation_sizes[image_path][0],
                "height": image_annotation_sizes[image_path][1]
            })
            next_image_id += 1
        
        # Add annotation with updated IDs
        annotation = item["annotation"].copy()
        annotation["id"] = next_annotation_id
        annotation["image_id"] = image_id_map[image_path]
        annotation["category_id"] = 1
        new_json["annotations"].append(annotation)
        next_annotation_id += 1

    # Save the new JSON file
    with open(f"animals/{animal}/annotations.json", "w") as f:
        json.dump(new_json, f, indent=2)

# Loop to print the count for each animal
animal_to_augment = []
for animal in animals:
    # print(f"{animal}: {annotation_count_dictionary_day[animal]}")
    augmented_animal_count = count_augmented_animals(animal)
    total = augmented_animal_count + annotation_count_dictionary_day[animal]
    if(total < 200):
        print(f"Too little photo's of {animal}: {total}")
        animal_to_augment.append({"animal": animal, "count": total, "needed": 200})
with open('data.json', 'w') as file:
    json.dump(animal_to_augment, file)





