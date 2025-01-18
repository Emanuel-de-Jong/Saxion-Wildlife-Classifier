'''
This script is used to augment the images in the dataset. You will need to first have a image directory with the images,
an output directory for the augmented images, path to annotations, path to the output for annotations
and data.json that contains the animal name, the count of animals and the amount of augmented images needed.
Created by Simon Vermaat
'''

import os
import random
import json
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import copy

# Define augmentations
def random_brightness_contrast(image):
    """ Randomly adjust brightness and contrast """
    brightness = ImageEnhance.Brightness(image).enhance(random.uniform(0.8, 1.8))
    contrast = ImageEnhance.Contrast(brightness).enhance(random.uniform(0.8, 1.8))
    return contrast

def light_blur(image):
    """ Apply a light Gaussian blur """
    return image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 0.8)))

def add_light_noise(image):
    """ Add slight Gaussian noise """
    np_image = np.array(image)
    noise = np.random.normal(0, 5, np_image.shape).astype(np.int16)
    noisy = np.clip(np_image + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy)

def horizontal_flip(image, annotations, image_width):
    """ Horizontally flip the image and adjust annotations """
    flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
    updated_annotations = []
    for ann in annotations:
        bbox = ann["bbox"].copy()  # Make a copy of the bbox
        new_x = image_width - bbox[0] - bbox[2]  # Adjust x coordinate
        updated_bbox = [new_x, bbox[1], bbox[2], bbox[3]]
        new_ann = ann.copy()
        new_ann["bbox"] = updated_bbox
        updated_annotations.append(new_ann)
    return flipped_image, updated_annotations

# Pipeline
def augment_image(image, annotations):
    width, _ = image.size  # Get image width
    flipped = random.choice([True, False])  # Randomly decide on flip
    annotations_copy = copy.deepcopy(annotations)  # Deep copy for safety
    if flipped:
        image, annotations_copy = horizontal_flip(image, annotations_copy, width)
    image = random_brightness_contrast(image)
    image = light_blur(image)
    image = add_light_noise(image)
    return image, annotations_copy

# Visualization for debugging
def visualize_bboxes(image, annotations, title="Augmented Image with Bounding Boxes"):
    fig, ax = plt.subplots(1, figsize=(10, 10))
    ax.imshow(image)
    for ann in annotations:
        x, y, w, h = ann["bbox"]
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
    plt.title(title)
    plt.show()

with open("data.json", "r") as f:
    animal_data = json.load(f)

# Extract just the animal names from the data
animals = [item["animal"] for item in animal_data]
animal_data_dict = {item["animal"]: {"count": item["count"], "needed": item["needed"]} for item in animal_data}

for animal in animals:

    # Load COCO annotations
    image_dir = f"animals/{animal}"
    output_dir = f"augmented_output/{animal}"
    coco_input_path = f"animals/{animal}/annotations.json"
    coco_output_path = f"augmented_output/{animal}/coco_annotations_{animal}_augmented.json"

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(coco_input_path):
        continue

    with open(coco_input_path, "r") as f:
        coco_data = json.load(f)

    # Get existing images and annotations from output directory if they exist
    existing_images = []
    existing_annotations = []
    if os.path.exists(coco_output_path):
        with open(coco_output_path, "r") as f:
            existing_data = json.load(f)
            existing_images = existing_data["images"]
            existing_annotations = existing_data["annotations"]

    # Start IDs after the highest existing ones
    next_image_id = max((img["id"] for img in existing_images), default=0) + 1
    annotation_id = max((ann["id"] for ann in existing_annotations), default=0) + 1

    # Initialize new_images and new_annotations with existing data
    new_images = existing_images.copy()
    new_annotations = existing_annotations.copy()

    # Process images and annotations
    image_id_map = {img["file_name"]: img["id"] for img in coco_data["images"]}
    images = coco_data["images"]
    annotations = coco_data["annotations"]

    for img in images:
        img_path = os.path.join(image_dir, img["file_name"])
        if not os.path.exists(img_path):
            continue

        # Filter annotations for this image
        img_annotations = [copy.deepcopy(ann) for ann in annotations if ann["image_id"] == img["id"]]
        image = Image.open(img_path).convert("RGB")

        animal_info = animal_data_dict[animal]
        if animal_info["count"] == 0:
            augmentations_per_image = 0
        else:
            augmentations_per_image = animal_info["needed"] - animal_info["count"]

        for i in range(augmentations_per_image):  # Generate 5 augmentations per image
            # Augment image and annotations
            augmented_image, augmented_annotations = augment_image(image, img_annotations)

            # Visualize for debugging
            # visualize_bboxes(augmented_image, augmented_annotations, title=f"Image {img['file_name']} Augmentation {i+1}")

            # Update file name and image ID
            new_file_name = f"{img['file_name'].split('.')[0]}_aug_{i}.jpg"
            # new_image_id = len(new_images) + 1
            new_image_id = next_image_id
            next_image_id += 1

            # Save augmented image
            output_path = os.path.join(output_dir, new_file_name)
            augmented_image.save(output_path)

            # Update image metadata
            new_images.append({
                "id": new_image_id,
                "file_name": new_file_name,
                "width": img["width"],
                "height": img["height"]
            })

            # Update annotation metadata
            for ann in augmented_annotations:
                ann["id"] = annotation_id
                ann["image_id"] = new_image_id
                new_annotations.append(copy.deepcopy(ann))  # Deep copy each annotation
                annotation_id += 1
        # break  # Process only the first image for debugging

    # Save new COCO JSON
    augmented_coco = {
        "images": new_images,
        "annotations": new_annotations,
        "categories": coco_data["categories"]
    }

    with open(coco_output_path, "w") as f:
        json.dump(augmented_coco, f, indent=4)

    print(f"Augmentation with COCO adjustments completed successfully for {animal}!")
