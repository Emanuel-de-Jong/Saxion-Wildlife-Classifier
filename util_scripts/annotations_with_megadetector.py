"""
Usage:
python .\\util_scripts\\annotations_with_megadetector.py "<input_path>"
"""

import os
import json
import torch
import argparse
import numpy as np
from PIL import Image
from PytorchWildlife.models.detection import MegaDetectorV5
from PytorchWildlife.data.transforms import MegaDetector_v5_Transform

PADDING = 10

parser = argparse.ArgumentParser()
parser.add_argument("input_path", type=str, help="Path to the directory containing images.")
args = parser.parse_args()

input_path = args.input_path

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model = MegaDetectorV5(device=device, pretrained=True)
transform = MegaDetector_v5_Transform(target_size=model.IMAGE_SIZE, stride=model.STRIDE)

annotation_id = 1
image_id = 0
for root, _, files in os.walk(input_path):
    coco_output = {
        "info": {},
        "images": [],
        "annotations": [],
        "categories": [
            {
                "id": 1,
                "name": "animal",
                "supercategory": "object"
            }
        ]
    }

    for file in files:
        if not file.lower().endswith('.jpg'):
            continue

        # image_num = int(file.split('.')[0][-3:])
        # if image_num <= 237:
        #     continue

        image_id += 1

        image_path = os.path.join(root, file)
        print(image_path)
        image = np.array(Image.open(image_path).convert("RGB"))

        coco_image_path = os.path.join(os.path.relpath(root, input_path), file).replace("\\", "/")
        coco_output["images"].append({
            "id": image_id,
            "file_name": file,
            "height": image.shape[0],
            "width": image.shape[1]
        })

        transformed_image = transform(image)
        results = model.single_image_detection(transformed_image)
        if 'detections' not in results:
            continue

        target_size = transform.target_size
        original_height, original_width = image.shape[:2]
        # scaling_ratio = min(target_size / original_height, target_size / original_width)
        # new_width = int(round(original_width * scaling_ratio))
        # new_height = int(round(original_height * scaling_ratio))
        # dw = (target_size - new_width) / 2
        # dh = (target_size - new_height) / 2
        
        x_scale = original_width / target_size
        y_scale = original_height / target_size
        # x_scale = original_width / new_width
        # y_scale = original_height / new_height

        detections = results['detections']
        for i in range(len(results['labels'])):
            label = results['labels'][i].split()[0]
            score = float(results['labels'][i].split()[1])
            if label != 'animal' or score < 0.5:
                continue

            x1, y1, x2, y2 = detections.xyxy[i].tolist()
            x1 = (x1 - PADDING) * x_scale
            x2 = (x2 + PADDING) * x_scale
            y1 = (y1 - PADDING) * y_scale
            y2 = (y2 + PADDING) * y_scale
            # x1 = (x1 - dw) / scaling_ratio * x_scale
            # y1 = (y1 - dh) / scaling_ratio * y_scale
            # x2 = (x2 - dw) / scaling_ratio * x_scale
            # y2 = (y2 - dh) / scaling_ratio * y_scale

            width = x2 - x1
            height = y2 - y1

            coco_output["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": 1,
                "bbox": [x1, y1, width, height],
                "area": width * height,
                "iscrowd": 0,
                "segmentation": [],
            })
            annotation_id += 1
    
    if len(coco_output["images"]) == 0:
        continue
        
    output_path = os.path.join(root, "coco_annotations.json")
    with open(output_path, 'w') as f:
        json.dump(coco_output, f, indent=4)
    
    print(f"{output_path} saved")

print("Done!")
