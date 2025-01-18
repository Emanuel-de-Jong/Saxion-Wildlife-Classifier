import os
import json
import shutil
import random
from PIL import Image
import cv2
import numpy as np

def is_colored(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Check if the image is valid
    if image is None:
        return None, "Invalid image file"

    # Split into color channels
    b, g, r = cv2.split(image)
    
    # Calculate the mean and variance of the color channels
    color_variance = np.var(b) + np.var(g) + np.var(r)

    # Decision
    if color_variance < 13000:  # Adjust threshold if necessary
        return False
    else:
        return True

def select_dataset(input_path):
    # in animal list, enter every animal that could appear in your dataset.
    animal_list = ['miscellaneous','duck','goose','duckling','gosling','hare','rabbit','ice_diver','egyptian_goose','egyptian_gosling','coot','swan','crow','pidgeon',
                   'magpie','cat','oystercatcher','lapwing','starling','redshank','skylark','meadow_pipit','godwit','shoveler','summer_teal','tufted_duck','gadwall',
                   'fox','buzzard','goshawk','harrier','sparrowhawk','beech_marten','polecat','weasel','ermine','rat','jackdaw','raven','greylag_goose','canadian_goose',
                   'wagtail','blackbird','moorhen','common_shelduck','black_headed_seagull','heron','pheasant','stork','dog','swallow','tit','orinoco_goose','singing_bushlark',
                   'seagull', 'pheasant_female', 'kestrel']
    # determine the threshold, this many annotations will be saved per animal. of the threshold amount, 70% will be for training, 20% for validation and 10% for testing
    threshold = 200
    
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
                        if is_colored(image_path):
                            annotation_dictionary_day[animal].append(annotation_image)
                            annotation_count_dictionary_day[animal] += 1
                        else:
                            annotation_dictionary_night[animal].append(annotation_image)
                            annotation_count_dictionary_night[animal] += 1

    path_list_empty_day = []
    path_list_empty_night = []
    path_list_empty_day_used = []
    path_list_empty_night_used = []
    def select_empty(list, path):
        for file in os.listdir(path):
            if file.endswith(".JPG"):
                file_path = os.path.join(path, file)  
                with Image.open(file_path) as img:
                    width, height = img.size  
                    list.append({"path": file_path, "width": width, "height": height})

    select_empty(path_list_empty_day, "./empty_day")
    select_empty(path_list_empty_night, "./empty_night")

    def split_set(annotation_dictionary, annotation_count_dictionary):
        annotation_dictionary["miscellaneous"].clear()
        annotation_count_dictionary["miscellaneous"] = 0
        selected_animal_list = []
        for key, value in annotation_count_dictionary.items():
            if(value >= threshold and value != "miscellaneous"):
                selected_animal_list.append(key)
        
        train_image_list = []
        val_image_list = []
        test_image_list = []

        for animal in selected_animal_list:
            random_selection = random.sample(annotation_dictionary[animal], int(threshold * 0.7))
            for annotation in random_selection:
                train_image_list.append(annotation)

        for animal in selected_animal_list:
            remaining_annotations = [a for a in annotation_dictionary[animal] if a not in train_image_list]
            
            if len(remaining_annotations) >= int(threshold * 0.2):
                random_selection = random.sample(remaining_annotations, int(threshold * 0.2))
                for annotation in random_selection:
                    val_image_list.append(annotation)
        for animal in selected_animal_list:
            remaining_annotations = [a for a in annotation_dictionary[animal] if a not in train_image_list and a not in val_image_list]
            
            if len(remaining_annotations) >= int(threshold * 0.2):
                random_selection = random.sample(remaining_annotations, int(threshold * 0.1))
                for annotation in random_selection:
                    test_image_list.append(annotation)
        return selected_animal_list, train_image_list, val_image_list, test_image_list
    
    selected_animal_list_day, train_image_list_day, val_image_list_day, test_image_list_day = split_set(annotation_dictionary_day, annotation_count_dictionary_day)
    selected_animal_list_night, train_image_list_night, val_image_list_night, test_image_list_night = split_set(annotation_dictionary_night, annotation_count_dictionary_night)
    
    def output(annotation_list, output_path, selected_animal_list, empty_split, empty_list, empty_list_used):
        image_list = {}
        image_list_sizes = {}
        for annotation in annotation_list:
            image_path = annotation["image_path"]
            image_size = image_annotation_sizes[image_path]
            if image_path not in image_list:
                image_list_sizes[str(len(image_list) + 1)] = image_size
                image_list[image_path] = len(image_list) + 1
        
        remaining_empty = [a for a in empty_list if a not in empty_list_used]
        random_selection = random.sample(remaining_empty, int(len(empty_list) * empty_split))
        for empty in random_selection:
            image_list_sizes[str(len(image_list) + 1)] = [empty["width"], empty["height"]]
            image_list[empty["path"]] = len(image_list) + 1
            empty_list_used.append(empty)

        print(len(image_list.keys()))
        for key, value in image_list.items():

            new_filename = f"IMG{value}.jpg"
            new_filepath = os.path.join(output_path, new_filename)

            shutil.copy(key, new_filepath)
            print(f"Copied {key} to {new_filepath}")
        
        json_output = {}
        json_output["licenses"] = [{"name":"","id":0,"url":""}]
        json_output["info"] = {"contributor":"","date_created":"","description":"","url":"","version":"","year":""}
        json_output["categories"] = [{"id":1,"name":"miscellaneous","supercategory":""}]
        for animal in selected_animal_list:
            json_output["categories"].append({"id":len(json_output["categories"])+1,"name":animal,"supercategory":""})
        json_output["images"] = []
        for key, value in image_list.items():
            name = "IMG"+str(value)+".jpg"
            print(image_list_sizes)   
            size = image_list_sizes[str(value)]
            json_output["images"].append({"id":value,"width":size[0],"height":size[1],"file_name":name,"license":0,"flickr_url":"","coco_url":"","date_captured":0})
        json_output["annotations"] = []
        for annotation in annotation_list:
            annotation["annotation"]["image_id"] = image_list[annotation["image_path"]]
            animal_name = animal_list[(annotation["annotation"]["category_id"]-1)]
            annotation["annotation"]["category_id"] = (selected_animal_list.index(animal_name)+2)
            json_output["annotations"].append(annotation["annotation"])
        with open(output_path+"/coco_annotations.json", 'w') as json_file:
            json.dump(json_output, json_file, indent=4)
    output(train_image_list_day, "./dataset/train_day", selected_animal_list_day, 0.7, path_list_empty_day, path_list_empty_day_used)
    output(val_image_list_day, "./dataset/val_day", selected_animal_list_day, 0.2, path_list_empty_day, path_list_empty_day_used)
    output(test_image_list_day, "./dataset/test_day", selected_animal_list_day, 0.1, path_list_empty_day, path_list_empty_day_used)
    output(train_image_list_night, "./dataset/train_night", selected_animal_list_night, 0.7, path_list_empty_night, path_list_empty_night_used)
    output(val_image_list_night, "./dataset/val_night", selected_animal_list_night, 0.2, path_list_empty_night, path_list_empty_night_used)
    output(test_image_list_night, "./dataset/test_night", selected_animal_list_night, 0.1, path_list_empty_night, path_list_empty_night_used)
# the root folder is the file path to the location where your data is stored. it expects the structure of camera directories in the location and leging directories in the camera.
root_folder = "./done"
select_dataset(root_folder)
