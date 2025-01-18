"""
This utility module provides helper functions for processing predicted bounding boxes 
based on the Intersection over Union (IoU) metric.

Functionality:
- `compute_iou`: 
    Computes the Intersection over Union (IoU) between two bounding boxes.

- `is_fully_covered`: 
    Determines if one bounding box is fully covered by another, either in a contained or containing relationship.

- `filter_boxes_by_iou`: 
    Filters overlapping bounding boxes based on IoU and confidence scores, keeping the box with the higher score. 
    It also checks for full coverage and suppresses boxes accordingly.
"""

import numpy as np

def compute_iou(box1, box2):
    x_min1, y_min1, x_max1, y_max1 = box1
    x_min2, y_min2, x_max2, y_max2 = box2

    inter_x_min = max(x_min1, x_min2)
    inter_y_min = max(y_min1, y_min2)
    inter_x_max = min(x_max1, x_max2)
    inter_y_max = min(y_max1, y_max2)

    inter_width = max(0, inter_x_max - inter_x_min)
    inter_height = max(0, inter_y_max - inter_y_min)
    inter_area = inter_width * inter_height

    area1 = (x_max1 - x_min1) * (y_max1 - y_min1)
    area2 = (x_max2 - x_min2) * (y_max2 - y_min2)

    union_area = area1 + area2 - inter_area

    iou = inter_area / union_area if union_area != 0 else 0
    return iou

def is_fully_covered(box1, box2):
    x_min1, y_min1, x_max1, y_max1 = box1
    x_min2, y_min2, x_max2, y_max2 = box2

    return (x_min1 >= x_min2 and y_min1 >= y_min2 and x_max1 <= x_max2 and y_max1 <= y_max2) or (x_min1 <= x_min2 and y_min1 <= y_min2 and x_max1 >= x_max2 and y_max1 >= y_max2)

def filter_boxes_by_iou(labels, boxes, scores, iou_threshold=0.3):
    keep_indices = []  
    num_boxes = len(boxes)

    suppressed = np.zeros(num_boxes, dtype=bool)

    for i in range(num_boxes):
        if suppressed[i]:
            continue

        for j in range(i + 1, num_boxes):
            if suppressed[j]:
                continue

            iou = compute_iou(boxes[i], boxes[j])

            if iou > iou_threshold or is_fully_covered(boxes[i], boxes[j]):
                if scores[i] >= scores[j]:
                    suppressed[j] = True
                else:
                    suppressed[i] = True
                    break

        if not suppressed[i]:
            keep_indices.append(i)

    filtered_labels = [labels[i] for i in keep_indices]
    filtered_boxes = [boxes[i] for i in keep_indices]
    filtered_scores = [scores[i] for i in keep_indices]

    return filtered_labels, filtered_boxes, filtered_scores