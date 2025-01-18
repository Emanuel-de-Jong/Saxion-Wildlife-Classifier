import os
from PIL import Image
from .model import effdet_infer_on_image, create_model_effdet
from .utils.torch_utils import get_device
from .config.constants import LIMITED_LABELS, ALL_LABELS, APPROPRIATE_FORMATS
import json
import copy
import traceback

def calculate_area(bbox):
    # bbox is a list or tuple in the format [x, y, width, height]
    _, _, width, height = bbox
    return int(width * height)

def infer():
    device = get_device()

    model = create_model_effdet(device)

    annotation_object = {
        "licenses":[{"name":"","id":0,"url":""}],
        "info":{"contributor":"","date_created":"","description":"","url":"","version":"","year":""},
        "categories":[
            {"id":1,"name":"miscellaneous","supercategory":""},
            {"id":2,"name":"duck","supercategory":""},
            {"id":3,"name":"goose","supercategory":""},
            {"id":4,"name":"duckling","supercategory":""},
            {"id":5,"name":"gosling","supercategory":""},
            {"id":6,"name":"hare","supercategory":""},
            {"id":7,"name":"rabbit","supercategory":""},
            {"id":8,"name":"ice_diver","supercategory":""},
            {"id":9,"name":"egyptian_goose","supercategory":""},
            {"id":10,"name":"egyptian_gosling","supercategory":""},
            {"id":11,"name":"coot","supercategory":""},
            {"id":12,"name":"swan","supercategory":""},
            {"id":13,"name":"crow","supercategory":""},
            {"id":14,"name":"pidgeon","supercategory":""},
            {"id":15,"name":"magpie","supercategory":""},
            {"id":16,"name":"cat","supercategory":""},
            {"id":17,"name":"oystercatcher","supercategory":""},
            {"id":18,"name":"lapwing","supercategory":""},
            {"id":19,"name":"starling","supercategory":""},
            {"id":20,"name":"redshank","supercategory":""},
            {"id":21,"name":"skylark","supercategory":""},
            {"id":22,"name":"meadow_pipit","supercategory":""},
            {"id":23,"name":"godwit","supercategory":""},
            {"id":24,"name":"shoveler","supercategory":""},
            {"id":25,"name":"summer_teal","supercategory":""},
            {"id":26,"name":"tufted_duck","supercategory":""},
            {"id":27,"name":"gadwall","supercategory":""},
            {"id":28,"name":"fox","supercategory":""},
            {"id":29,"name":"buzzard","supercategory":""},
            {"id":30,"name":"goshawk","supercategory":""},
            {"id":31,"name":"harrier","supercategory":""},
            {"id":32,"name":"sparrowhawk","supercategory":""},
            {"id":33,"name":"beech_marten","supercategory":""},
            {"id":34,"name":"polecat","supercategory":""},
            {"id":35,"name":"weasel","supercategory":""},
            {"id":36,"name":"ermine","supercategory":""},
            {"id":37,"name":"rat","supercategory":""},
            {"id":38,"name":"house_cat","supercategory":""},
            {"id":39,"name":"jackdaw","supercategory":""},
            {"id":40,"name":"raven","supercategory":""},
            {"id":41,"name":"greylag_goose","supercategory":""},
            {"id":42,"name":"canadian_goose","supercategory":""},
            {"id":43,"name":"wagtail","supercategory":""},
            {"id":44,"name":"blackbird","supercategory":""},
            {"id":45,"name":"moorhen","supercategory":""},
            {"id":46,"name":"common_shelduck","supercategory":""},
            {"id":47,"name":"black_headed_seagull","supercategory":""},
            {"id":48,"name":"heron","supercategory":""},
            {"id":49,"name":"pheasant","supercategory":""},
            {"id":50,"name":"stork","supercategory":""},
            {"id":51,"name":"dog","supercategory":""},
            {"id":52,"name":"swallow","supercategory":""},
            {"id":53,"name":"tit","supercategory":""},
            {"id":54,"name":"orinoco_goose","supercategory":""},
            {"id":55,"name":"singing_bushlark","supercategory":""},
            {"id":56,"name":"seagull","supercategory":""},
            {"id":57,"name":"pheasant_female","supercategory":""},
            {"id":58,"name":"kestrel","supercategory":""}
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
    
    with open(("./results/efficient_det/annotations.json"), "w") as file:
        json.dump(annotation_object, file, indent=4)

def infer_folder(target_folder, model, device, annotation_object, main_annotation):
    modified_string = target_folder
    modified_string = modified_string.replace("/", "_").replace(" ", "_")
    annotation_name = modified_string + "_annotations.json"

    
    for filename in os.listdir(target_folder):
        if f'.{filename.lower().split(".")[-1]}' in APPROPRIATE_FORMATS:
            file_path = os.path.join(target_folder, filename)
            image = Image.open(file_path)
            annotation_object["images"].append({"id":(len(annotation_object["images"])+1),"width":image.width,"height":image.height,"file_name":filename,"license":0,"flickr_url":"","coco_url":"","date_captured":0})
            main_annotation["images"].append({"id":(len(main_annotation["images"])+1),"width":image.width,"height":image.height,"file_name":os.path.join(*(file_path.split(os.path.sep)[1:])),"license":0,"flickr_url":"","coco_url":"","date_captured":0})

            boxes, labels, scores = effdet_infer_on_image(model, file_path, device)
            
            score_threshold = 0.2
            filtered_boxes, filtered_labels, filtered_scores = [], [], []
            
            x_modifier = image.width / 768.0
            y_modifier = image.height / 768.0
            resized_bounding_boxes = []
            for box in boxes:
                x_min = int(box[0] * x_modifier)
                y_min = image.height - int(box[1] * y_modifier)
                width = int(box[2] * x_modifier)
                height = image.height - int(box[3] * y_modifier)
                resized_bounding_boxes.append([x_min, y_min, width, height])
            
            for i in range(len(scores)):
                if scores[i] >= score_threshold:
                    filtered_boxes.append(resized_bounding_boxes[i])
                    filtered_labels.append(labels[i])
                    filtered_scores.append(scores[i])
            
            for i in range(len(filtered_boxes)):
                animal_name = LIMITED_LABELS[labels[i] - 1]
                if animal_name in ALL_LABELS:
                    animal_index = ALL_LABELS.index(animal_name) + 1
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
    with open(("./results/efficient_det/"+annotation_name), "w") as file:
        json.dump(annotation_object, file, indent=4)      

try: 
    infer()
except Exception as exception:
    traceback.print_exc()
    error_message = f'[EFFICIENT_DET]: {str(exception)}'
    with open("./results/efficient_det/error.log", 'w') as file:
        file.write(error_message)
