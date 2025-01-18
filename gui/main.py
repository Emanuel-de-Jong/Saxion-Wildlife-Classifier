import os
import sys
import json
import gui
import traceback
from PIL import Image

ERROR_PATH = os.path.join("..", "error.log")
RESULTS_PATH = os.path.join("..", "results")
STATS_FILENAME = "stats.json"

def run():
    try:
        image_dir_path = sys.argv[1]
        visualize_annotations = sys.argv[2] == 'True'
        visualize_statistics = sys.argv[3] == 'True'
        model = sys.argv[4]

        gui.init()

        gui.put("title", model)

        if visualize_annotations:
            show_annotation_examples(image_dir_path, model)
        
        if visualize_statistics:
            show_stats(model)

        gui.mainloop()
    except Exception as exception:
        traceback.print_exc()
        error_message = f'[GUI]: {str(exception)}'
        with open(ERROR_PATH, 'w') as file:
            file.write(error_message)
        exit(1)

def show_annotation_examples(image_dir_path, model):
    labeled_images = get_labeled_images(image_dir_path, model)
    
    used_categories = set()
    images_to_show = []
    for labeled_image in labeled_images:
        should_show_image = False
        for category in labeled_image["categories"]:
            if category not in used_categories:
                should_show_image = True
                used_categories.add(category)
        
        if should_show_image:
            images_to_show.append(labeled_image)
        
        if len(images_to_show) == 6:
            break
    
    for image_to_show in images_to_show:
        image_to_show["image"] = Image.open(image_to_show["file_path"])
    
    gui.put("annotation_examples", images_to_show)

def get_labeled_images(image_dir_path, model):
    with open(os.path.join(RESULTS_PATH, model, "annotations.json")) as file:
        annotations_file = json.load(file)
    
    image_entries = annotations_file["images"]
    annotations = annotations_file["annotations"]
    categories = {c["id"]: c["name"] for c in annotations_file["categories"]}

    labeled_images = []
    for image_entry in image_entries:
        labeled_image = {}
        image_path = os.path.normpath(image_entry["file_name"])
        image_path = os.path.join(image_dir_path, image_path)
        labeled_image["file_path"] = image_path

        labeled_image["annotations"] = []
        categories_in_image = set()
        for annotation in annotations:
            if annotation["image_id"] == image_entry["id"]:
                image_annotation = {}
                image_annotation["bbox"] = annotation["bbox"]
                image_annotation["score"] = annotation["score"]
                category = categories[annotation["category_id"]]
                categories_in_image.add(category)
                image_annotation["category"] = category

                labeled_image["annotations"].append(image_annotation)
        
        labeled_image["categories"] = categories_in_image
        
        labeled_images.append(labeled_image)
    
    return labeled_images

def show_stats(model):
    with open(os.path.join(RESULTS_PATH, model, "stats.json")) as file:
        stats = json.load(file)
    
    gui.put("stats", stats)

run()
