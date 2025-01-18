"""
This module defines constants used in the object detection model, specifically 
the mappings between class labels (species names) and their corresponding 
integer indices. These mappings are essential for encoding and decoding labels 
during the training and evaluation phases of the model.

Mappings:
- `CLASS_LABEL_TO_INT`: A dictionary that maps class labels (strings) 
  to unique integer indices. This mapping is used to encode the class 
  labels as integers suitable for training a machine learning model.
  
- `INT_TO_CLASS_LABEL`: A dictionary that maps integer indices back 
  to their corresponding class labels (strings). This mapping is useful 
  for interpreting model predictions and converting predicted indices 
  back to human-readable class names.
  
- `NUM_CLASSES`: An integer that denotes the number of classes in the model.

Image Metadata & Resizing:
- `IMAGE_METADATA_HEIGHT`: An integer height that specifies the expected black metadata section height of each camera trap image.
- `IMAGE_RESIZE_SIZE`: A tuple that denotes the target output image size after preprocessing.

Accepted file formats:
- `APPROPRIATE_FORMATS`: A tuple of accepted file formats

Normalizing:
- `MEAN`: Sequence of means for each channel
- `STD`: Sequence of standerd deviations for each channel

Usage:
- Import this module in other parts of the code where you need to 
  reference class labels or convert between string and integer representations.
"""


CLASS_LABEL_TO_INT = {'miscellaneous:':1,'duck':2,'gosling':3,'hare': 4,'egyptian_goose': 5,'coot': 6,'swan': 7,'crow': 8,'pidgeon': 9,'magpie': 10,'cat': 11,'oystercatcher': 12,'starling': 13,'jackdaw': 14,'greylag_goose': 15,'canadian_goose': 16,'moorhen': 17,'heron': 18, 'pheasant': 19}
ALL_LABELS = [
  "miscellaneous", "duck", "goose", "duckling", "gosling", "hare", "rabbit", 
  "ice_diver", "egyptian_goose", "egyptian_gosling", "coot", "swan", "crow", 
  "pidgeon", "magpie", "cat", "oystercatcher", "lapwing", "starling", "redshank", 
  "skylark", "meadow_pipit", "godwit", "shoveler", "summer_teal", "tufted_duck", 
  "gadwall", "fox", "buzzard", "goshawk", "harrier", "sparrowhawk", "beech_marten", 
  "polecat", "weasel", "ermine", "rat", "house_cat", "jackdaw", "raven", 
  "greylag_goose", "canadian_goose", "wagtail", "blackbird", "moorhen", 
  "common_shelduck", "black_headed_seagull", "heron", "pheasant", "stork", 
  "dog", "swallow", "tit", "orinoco_goose", "singing_bushlark", "seagull", 
  "pheasant_female", "kestrel"
]
INT_TO_CLASS_LABEL = {v: k for k, v in CLASS_LABEL_TO_INT.items()}
NUM_CLASSES = len(CLASS_LABEL_TO_INT.keys())

IMAGE_METADATA_HEIGHT = 120
IMAGE_RESIZE_SIZE = (512, 512)

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

APPROPRIATE_FORMATS = ('.png', '.jpg', '.jpeg')
DATE_TIME_FORMAT = "%m/%d/%Y %H:%M:%S"