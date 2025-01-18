import os
from PIL import Image
from .classes.metadata import MetadataProvider
from .config.constants import APPROPRIATE_FORMATS
from .postprocessing.postprocess import remove_duplicates
from .postprocessing.stat_generator import get_statistics
import json
import traceback

IMAGE_PATH = 'images'
RESULTS_PATH = 'results'
ANNOTATION_FILE = 'annotations.json'

def find_image_filepaths(folder_path, extensions=('jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif')):
    """
    Recursively find all image file paths in a folder and its subfolders.

    Parameters
    ----------
        folder_path: String
            The root folder to search in.
        extensions: Tuple
            Tuple of image file extensions to look for.

    Returns
    -------
        image_filepaths: list
            A list of full file paths for the found images.
    """
    image_filepaths = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(extensions):
                image_filepaths.append(os.path.join(root, file))
    
    return image_filepaths

def get_inference_data(filename, complete_annotation_json):
    '''
    Get all scores, bboxes and labels, for a given file

    Parameters
    ----------
        filename: String
            The file that we want information from
        complete_annotation_json: JSON
            The complete annotation JSON

    Returns
    -------
        scores: list
            A list of all scores for the given file.
        boxes: list
            A list of all bboxes for the given file.
        labels: list
            A list of all labels for the given file.
    '''
    scores, boxes, labels = [], [], []
    images = complete_annotation_json['images']
    image_id = None
    for item in images:
        if item['file_name'] == filename:
            image_id = item['id']
            break
    if image_id == None:
        raise IndexError(f"An image id should have been found for '{filename}', but got None")

    annotations = complete_annotation_json['annotations']
    all_annotations = [annotation for annotation in annotations if annotation['image_id'] == image_id]

    for annotation in all_annotations:
        scores.append(annotation['score'])
        boxes.append(annotation['bbox'])
        labels.append(annotation['category_id'])
    
    return scores, boxes, labels
    
def process(target_folder, results_folder, model):
    '''
    Proces the inference data to statistics

    Parameters
    ----------
        target_folder: String
            The folder with all used images
        results_folder: JSON
            The folder with the inference data (the annotations json)
        model: String
            The used model

    Returns
    -------
        results: JSON
            JSON data with all results (not filtered on duplicates)
        
        OR
            
        removed_duplicates: JSON
            JSON data with the results (filtered on duplicates)
        
    '''
    # Initialize state
    mdp = MetadataProvider(mode="inference")
    
    results = []
    cat_dict = {}
    image_paths = find_image_filepaths(target_folder)
    
    complete_annotation_json = None
    with open(os.path.join(results_folder, model, ANNOTATION_FILE), 'r') as file:
        complete_annotation_json = json.load(file)
    categories = complete_annotation_json["categories"]

    # Dictionary with all id's and the labels
    for category in categories:
        cat_dict[category["id"]] = category["name"]
    
    # Loop over every file in the target folder
    for image_path in image_paths:        
        # Check if the file is an image
        if (not (os.path.isfile(image_path) and image_path.lower().endswith(APPROPRIATE_FORMATS))):
            continue

        # Load the image
        image = Image.open(image_path)
        
        # Perform preprocessing
        image_main, image_metadata = mdp.split_image_and_metadata(image)
        metadata = mdp.extract_metadata(image_metadata)

        relative_path = os.path.normpath(image_path).replace(os.sep, '/').replace(target_folder + "/", "")
        path_components = relative_path.split("/")
        current_camera = path_components[0] if len(path_components) > 1 else metadata[2]
        current_leging = path_components[1] if len(path_components) > 2 else ""
        
        # Filter results
        filtered_boxes, filtered_labels, filtered_scores = [], [], []

        scores, boxes, labels = get_inference_data(os.path.join(*(image_path.split(os.path.sep)[1:])), complete_annotation_json)
        
        for i in range(len(scores)):
            filtered_boxes.append(boxes[i])
            filtered_labels.append(cat_dict[labels[i]])
            filtered_scores.append(scores[i])

        # Store results in a list
        results.append({
            'target_filename': image_path,
            'metadata': {
                'date': metadata[0],
                'time': metadata[1],
                'camera': current_camera,
                'leging': current_leging
            },
            'coco_boxes': filtered_boxes,
            'labels': filtered_labels,
            'scores': filtered_scores
        })

    if os.environ["FILTER_BATCHES"] == 'True':
        removed_duplicates = remove_duplicates(results)
        return removed_duplicates
    
    return results

def print_result(coco_boxes, labels, scores, metadata):
    # Print metadata, coco_boxes, labels, and scores in a formatted manner
    print("Metadata Extracted:")
    print(f"Date: {metadata[0]}")
    print(f"Time: {metadata[1]}")
    print(f"Camera: {metadata[2]}")

    print("\nCOCO Boxes:")
    for box in coco_boxes:
        print(f"Box: {box}")

    print("\nLabels and Scores:")
    for label, score in zip(labels, scores):
        print(f"Label: {label}, Score: {score:.4f}")

if (__name__ == '__main__'):
    try:
        model_lst = os.environ["MODELS"].split(',')
        model = None
        for model in model_lst:
            print(f"Current model: {model}")
            results = process(IMAGE_PATH, RESULTS_PATH, model)

            stats = get_statistics(results)
            with open(os.path.join("results", model, 'stats.json'), "w") as file:
                json.dump(stats, file, indent=4)
    except Exception as exception:
        traceback.print_exc()
        error_message = f'[POSTPROCESSING]: {str(exception)}'
        error_log_path = os.path.join("results", model, "error.log")
        with open(error_log_path, 'w') as file:
            file.write(error_message)
        exit(1)