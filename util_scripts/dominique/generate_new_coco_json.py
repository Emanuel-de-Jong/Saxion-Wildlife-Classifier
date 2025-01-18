import os
import sys
import json

image_dir = "" # please provide the parrent dir of the folder where you want to make a new coco format file, based on pictures
image_extension = ".jpg"
json_extension = ".json"
new_annotation_id_starts_at = 1
new_category_id_starts_at = 1
new_image_id_starts_at = 1

def __get_image_per_dir():
    json_file = None
    dirs = []
    for dir in os.listdir(image_dir):
        if os.path.isdir(os.path.join(image_dir, dir)):
            dirs.append(dir)
        elif dir.lower().endswith(json_extension):
            if json_file is None:
                json_file = os.path.join(image_dir, dir)
            else:
                print(f"Multiple JSON files found! Please make sure only 1 JSON file is in the directory!")
                sys.exit()

    if len(dirs) == 0:
        print("No folders found! Please make the needed folders!")
        sys.exit()
    print(f"Found directories: {dirs}")
    if json_file is None:
        print("JSON annotation file not found! Please provide the complete JSON file!")
        sys.exit()
    print(f"Found JSON file: {json_file}")

    result_dict = {}

    for dir in dirs:
        current_dir = os.path.join(image_dir, dir)
        image_list = [os.path.join(current_dir, image) for image in os.listdir(current_dir) if image.lower().endswith(image_extension)]
        result_dict[dir] = image_list
    
    return [result_dict, dirs, json_file]

def __generate_new_json(image_list, directory, json_file):
    print(f"Generating new JSON for '{directory}' using '{json_file}'")
    total_images = len(image_list)
    print(f"Total images in '{directory}': {total_images}")
    

    json_data = json.load(open(json_file))
    licenses_part = json_data['licenses']
    info_part = json_data['info']
    categories_part = json_data['categories']
    
    cat_id_dict = {}
    new_id = new_category_id_starts_at
    for category in categories_part:
        cat_id_dict[category['id']] = new_id
        category['id'] = new_id
        new_id += 1

    image_id_list = [image['id'] for image in json_data['images'] if os.path.join(image_dir, directory, image['file_name']) in image_list]
    
    # Make a dictionary, with the old and new id's
    new_id = new_image_id_starts_at
    image_id_dict = {}

    for old_id in image_id_list:
        image_id_dict[old_id] = new_id
        new_id += 1

    # Replace the old id's with the new id's
    image_part = []
    for image in json_data['images']:
        if os.path.join(image_dir, directory, image['file_name']) in image_list:
            image['id'] = image_id_dict[image['id']]
            image_part.append(image)
    
    # Replace the image_id with the new image id's and change the annotation id's
    count = new_annotation_id_starts_at
    annotation_part = []
    for annotation in json_data['annotations']:
        if annotation['image_id'] in image_id_list:
            annotation['id'] = count
            annotation['image_id'] = image_id_dict[annotation['image_id']]
            annotation['category_id'] = cat_id_dict[annotation['category_id']]
            annotation_part.append(annotation)
            count += 1

    print(f"Images: {len(image_part)}")
    print(f"Annotations: {len(annotation_part)}")
    # The structure for the JSON file
    data = {
        "licenses": licenses_part,
        "info": info_part,
        "categories": categories_part,
        "images": image_part,
        "annotations": annotation_part
    }
    new_file = os.path.join(image_dir, directory, f"coco_annotations_{directory}.json")

    # If there is already a JSON file with the generated name, remove it
    if os.path.isfile(new_file):
        os.remove(new_file)
    
    # Make the new file
    with open(new_file, "w") as file:
        json.dump(data, file, indent=4)
    
    print(f"New JSON for directory '{directory}' has been created!\n\t'{new_file}'")

image_dict, directories, json_file = __get_image_per_dir() # Get all images per directory and get the JSON file

for directory in directories:
    __generate_new_json(image_dict[directory], directory, json_file)