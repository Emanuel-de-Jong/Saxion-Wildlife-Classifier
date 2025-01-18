import json
import os
import copy
import numpy as np

from PIL import Image
from .classes.metadata import MetadataProvider
from .config.constants import ALL_LABELS, APPROPRIATE_FORMATS
from .model_yolo import ModelYolo
from .utils.iou_utils import filter_boxes_by_iou
from .utils.torch_utils import get_device

model_path = "scripts/model.pt"
images_path = "test/images/cam1/leging1/"
result_file = "results/yolo/annotations.json"

annotations = []

def run():
    device = get_device()
    model = ModelYolo.create_model(device=device, filepath=model_path)

    annotation_object = {
        "licenses":[{"name":"","id":0,"url":""}],
        "info":{"contributor":"","date_created":"","description":"","url":"","version":"","year":""},
        "categories":[
            {"id":0,"name":"miscellaneous","supercategory":""},
            {"id":1,"name":"duck","supercategory":""},
            {"id":2,"name":"goose","supercategory":""},
            {"id":3,"name":"duckling","supercategory":""},
            {"id":4,"name":"gosling","supercategory":""},
            {"id":5,"name":"hare","supercategory":""},
            {"id":6,"name":"rabbit","supercategory":""},
            {"id":7,"name":"ice_diver","supercategory":""},
            {"id":8,"name":"egyptian_goose","supercategory":""},
            {"id":9,"name":"egyptian_gosling","supercategory":""},
            {"id":10,"name":"coot","supercategory":""},
            {"id":11,"name":"swan","supercategory":""},
            {"id":12,"name":"crow","supercategory":""},
            {"id":13,"name":"pidgeon","supercategory":""},
            {"id":14,"name":"magpie","supercategory":""},
            {"id":15,"name":"cat","supercategory":""},
            {"id":16,"name":"oystercatcher","supercategory":""},
            {"id":17,"name":"lapwing","supercategory":""},
            {"id":18,"name":"starling","supercategory":""},
            {"id":19,"name":"redshank","supercategory":""},
            {"id":20,"name":"skylark","supercategory":""},
            {"id":21,"name":"meadow_pipit","supercategory":""},
            {"id":22,"name":"godwit","supercategory":""},
            {"id":23,"name":"shoveler","supercategory":""},
            {"id":24,"name":"summer_teal","supercategory":""},
            {"id":25,"name":"tufted_duck","supercategory":""},
            {"id":26,"name":"gadwall","supercategory":""},
            {"id":27,"name":"fox","supercategory":""},
            {"id":28,"name":"buzzard","supercategory":""},
            {"id":29,"name":"goshawk","supercategory":""},
            {"id":30,"name":"harrier","supercategory":""},
            {"id":31,"name":"sparrowhawk","supercategory":""},
            {"id":32,"name":"beech_marten","supercategory":""},
            {"id":33,"name":"polecat","supercategory":""},
            {"id":34,"name":"weasel","supercategory":""},
            {"id":35,"name":"ermine","supercategory":""},
            {"id":36,"name":"rat","supercategory":""},
            {"id":37,"name":"house_cat","supercategory":""},
            {"id":38,"name":"jackdaw","supercategory":""},
            {"id":39,"name":"raven","supercategory":""},
            {"id":40,"name":"greylag_goose","supercategory":""},
            {"id":41,"name":"canadian_goose","supercategory":""},
            {"id":42,"name":"wagtail","supercategory":""},
            {"id":43,"name":"blackbird","supercategory":""},
            {"id":44,"name":"moorhen","supercategory":""},
            {"id":45,"name":"common_shelduck","supercategory":""},
            {"id":46,"name":"black_headed_seagull","supercategory":""},
            {"id":47,"name":"heron","supercategory":""},
            {"id":48,"name":"pheasant","supercategory":""},
            {"id":49,"name":"stork","supercategory":""},
            {"id":50,"name":"dog","supercategory":""},
            {"id":51,"name":"swallow","supercategory":""},
            {"id":52,"name":"tit","supercategory":""},
            {"id":53,"name":"orinoco_goose","supercategory":""},
            {"id":54,"name":"singing_bushlark","supercategory":""},
            {"id":55,"name":"seagull","supercategory":""},
            {"id":56,"name":"pheasant_female","supercategory":""},
            {"id":57,"name":"kestrel","supercategory":""}
        ],
        "images": [],
        "annotations": []
    }

    main_annotation = annotation_object.copy()
    annotation_copy = copy.deepcopy(annotation_object)

    for root, dirs, files in os.walk('images'):
        # Check if there is at least one image file in the current folder
        has_image = False
        for file in files:
            extension = f'.{file.lower().split(".")[-1]}'
            if extension in APPROPRIATE_FORMATS:
                has_image = True
                break
        
        if has_image:
            infer_folder(root, model, device, copy.deepcopy(annotation_copy), main_annotation)

    with open(("./results/yolo/annotations.json"), "w") as file:
        json.dump(annotation_object, file, indent=4)

def calculate_area(bbox):
    # bbox is a list or tuple in the format [x, y, width, height]
    _, _, width, height = bbox
    return int(width * height)

def infer_folder(target_folder, model, device, annotation_object, main_annotation):
    modified_string = target_folder
    modified_string = modified_string.replace("/", "_").replace(" ", "_")
    annotation_name = modified_string + "_annotations.json"

    
    for filename in os.listdir(target_folder):
        if f'.{filename.lower().split(".")[-1]}' in APPROPRIATE_FORMATS:
            file_path = os.path.join(target_folder, filename)
            print(file_path)
            
            image = Image.open(file_path)
            annotation_object["images"].append({"id":(len(annotation_object["images"])+1),"width":image.width,"height":image.height,"file_name":filename,"license":0,"flickr_url":"","coco_url":"","date_captured":0})
            main_annotation["images"].append({"id":(len(main_annotation["images"])+1),"width":image.width,"height":image.height,"file_name":os.path.join(*(file_path.split(os.path.sep)[1:])),"license":0,"flickr_url":"","coco_url":"","date_captured":0})

            labels, boxes, scores = inference(image, model)
            
            score_threshold = 0.1
            filtered_boxes, filtered_labels, filtered_scores = [], [], []
            
            for i in range(len(scores)):
                if scores[i] >= score_threshold:
                    filtered_boxes.append(boxes[i])
                    filtered_labels.append(labels[i])
                    filtered_scores.append(scores[i])
            
            for i in range(len(filtered_boxes)):
                animal_name = ALL_LABELS[labels[i]]
                if animal_name in ALL_LABELS:
                    animal_index = ALL_LABELS.index(animal_name)
                else:
                    continue
                annotation_object["annotations"].append({
                    "id":(len(annotation_object["annotations"])+1),
                    "image_id":len(annotation_object["images"]),
                    "category_id":animal_index,
                    "segmentation":[],
                    "area": float(calculate_area(filtered_boxes[i])),
                    "bbox": [float(x) for x in filtered_boxes[i]],
                    "iscrowd":0,
                    "attributes":{"occluded":False,"rotation":0.0}, 
                    "score": float(filtered_scores[i])
                    }) 
                main_annotation["annotations"].append({
                    "id":(len(main_annotation["annotations"])+1),
                    "image_id":len(main_annotation["images"]),
                    "category_id":animal_index,
                    "segmentation":[],
                    "area": float(calculate_area(filtered_boxes[i])),
                    "bbox": [float(x) for x in filtered_boxes[i]],
                    "iscrowd":0,
                    "attributes":{"occluded":False,"rotation":0.0}, 
                    "score": float(filtered_scores[i])
                    }) 
    with open(("./results/yolo/"+annotation_name), "w") as file:
        json.dump(annotation_object, file, indent=4)   

def inference(image, model):
    mdp = MetadataProvider()

    image_main, x = mdp.split_image_and_metadata(image)
    boxes, labels, scores = ModelYolo.infer_on_image(model, image_main)

    # Filter results
    score_threshold = 0.3
    filtered_boxes, filtered_labels, filtered_scores = [], [], []
            
    for i in range(len(scores)):
        if scores[i] >= score_threshold:
            filtered_boxes.append(boxes[i])
            filtered_labels.append(labels[i])
            filtered_scores.append(scores[i])   
            
    filtered_labels, filtered_boxes, filtered_scores = filter_boxes_by_iou(filtered_labels, filtered_boxes, filtered_scores, iou_threshold=0.3)

    return filtered_labels, filtered_boxes, filtered_scores

# def put_results_into_file(images, annotations, classes):
#      # Create file
#      # Name per file "[camera]_[leging]_annotation"
#     rf = open(result_file, "w")

#     # Write generic info into the file
#     rf.write("{\n")
#     rf.write("\"licenses\": [ \n { \n\"name\": \"\", \n \"id\": 0, \n \"url\": \"\" \n } \n ],")
#     rf.write("\n")
#     rf.write("\"info\": \n { \n \"contributor\": \"\", \n \"date_created\": \"\", \n \"description\": \"\", \n \"url\": \"\", \n \"version\": \"\", \n \"year\": \"\" \n }, ")

#     # Write category information into the file
#     rf.write("\n")
#     rf.write("\"categories\": [ \n")
#     for mclass in classes:
#          if(mclass != 0): rf.write(", \n")
#          rf.write("{")
#          rf.write(f"\n \"id\": {mclass}, \n \"name\": \"{classes[mclass]}\", \n \"supercategory\": \"\" \n")
#          rf.write("}")
#     rf.write("],")

#     # Write image information into the file
#     rf.write("\n")
#     rf.write("\"images\": [ \n")
#     for image in images:
#         if(image[0] != 1): rf.write(", \n")
#         rf.write("{")
#         rf.write(f"\n \"id\": {image[0]}, \n \"width\": {image[1]}, \n \"height\": {image[2]}, \n \"file_name\": \"{image[3]}\", \n \"license\": 0, \n \"flickr_url\": \"\", \n \"coco_url\": \"\", \n \"date_captured\": 0 \n")
#         rf.write("}")
#     rf.write("],")

#     # Write annotation information into the file
#     rf.write("\n")
#     rf.write("\"annotations\": [")
#     annotations_id = 1
#     for annotation in annotations:
#          box_id = 0
#          for label in annotation[1]:
#             if(annotations_id != 1): rf.write(", \n")
#             rf.write("{")
#             rf.write(f"\"id\": {annotations_id}, \n \"image_id\": {annotation[0]}, \n \"category_id\": {label}, \n \"segmentation\": [], \n \"area\": 0, \n \"bbox\": [ \n")
#             i = 0
#             for box in annotation[2][box_id]:
#                 rf.write(f"{box} \n")
#                 if(i != 3): rf.write(",")
#                 i += 1
#             rf.write(f"],\n \"iscrowd\": 0, \n \"attributes\": \n")
#             rf.write("{\n \"occluded\": false, \n \"rotation\": 0.0 \n } \n")
#             rf.write("}")
#             annotations_id += 1
#             box_id += 1
#     rf.write("] \n")

#     # Close file
#     rf.write("}")
#     rf.close()

# Run the program
run()