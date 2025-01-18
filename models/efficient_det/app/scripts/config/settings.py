"""
settings.py

Configuration file for setting up paths and other project-wide settings.

Tesseract OCR Setup Instructions:
1) Install Tesseract OCR: Follow instructions at https://github.com/UB-Mannheim/tesseract/wiki.
2) Add the Tesseract installation directory to your system PATH or provide the absolute path below.
3) Install the pytesseract Python package using: `pip install pytesseract`.

Tesseract Executable Path:
- `pytesseract_executable_path`: List with possible OS paths where the Tesseract executable can be found (if the default installation path hasn't been changed).
                                This will automatically be changed to the correct path for the current OS.

Camera Trap Dataset Paths:
- `camera_trap_dataset_path`: Path to the folder containing raw images from camera traps for object detection and image processing tasks.
- `camera_trap_processed_dataset_path`: Path to the folder where processed camera trap images will be saved after running the preprocessing pipeline.

Pascal VOC Dataset Paths:
- `pascal_voc_dataset_path`: Path to the main folder containing the raw labeled images in Pascal VOC format.
- `pascal_voc_augmented_dataset_path`: Path to the folder where augmented versions of labeled images will be output after running 'python scripts/preprocessing/augment.py'.

Model Training Configuration:
- `model_train_dataset_path`: Directory that contains the labeled training dataset, generally it should point to either pascal_voc_dataset_path or pascal_voc_augmented_dataset_path.
- `model_weights_save_path`: Directory path for saving model weights after training. Update this path to specify where trained model weights should be stored for later use or reloading.
- `model_maximum_training_epochs`: Sets the maximum number of epochs for model training. Adjust this parameter to control how long the model will be trained to avoid overfitting.
   Note, this is the maximum number of epochs, the model can stop training preemptively due to its early stopping functionality that terminates training prematurely if no progress is made for certain period of time.

Evaluation Results Path:
- `evaluation_results_path`: Path to the folder where evaluation results will be output.

Metadata File Store Path:
- `metadata_file_store_path`: Path to where the metadata csv should be saved

!ATTENTION: It is expected that all of the provided paths exist and are valid in order to not experience unprecedented behavior.
    The default provided values are expected to be appropriate with the provided project and correct installation steps.
    If a new path has to be added, use `os.path.normpath()`. This will make the given path useable on other OS.
"""
import os
import shutil

# Path to the Tesseract OCR executable
pytesseract_executable_path = shutil.which('tesseract')

# Backup, if shutil can't find tesseract
if pytesseract_executable_path is None:
    path_list = [os.path.normpath('C:/Program Files/Tesseract-OCR/tesseract.exe')
                                , os.path.normpath('/usr/bin/tesseract/Tesseract-OCR/tesseract.exe')
                                , os.path.normpath('/usr/local/bin/tesseract/Tesseract-OCR/tesseract.exe')] # Update this list as necesarry
    for path in path_list:
        if os.path.isfile(path):
            pytesseract_executable_path = path
            break

# Path to raw camera trap images
camera_trap_dataset_path = os.path.normpath('data/raw/camera')  # Update this path as necessary

# Path for storing processed camera trap images
camera_trap_processed_dataset_path = os.path.normpath('data/processed/camera')  # Update this path as necessary

# Path to raw labeled images in Pascal VOC format
pascal_voc_dataset_path = os.path.normpath('data/raw/labeledImages')  # Update this path as necessary

# Output path for augmented labeled images
pascal_voc_augmented_dataset_path = os.path.normpath('data/processed/labeledImagesAugmented')  # Update this path as necessary

# Output path for augmented unlabeled images
augmented_dataset_path = 'data/augmented/camera'

# Directory for model training dataset
# Uncomment the appropriate setting, 
# if no augmentations are planned to be applied, keep the first setting, otherwise 
# the second setting should apply and point to a directory containing augmented labeled iamges
# model_train_dataset_path = pascal_voc_dataset_path
model_train_dataset_path = pascal_voc_augmented_dataset_path

# Directory for saving model weights
model_weights_save_path = os.path.normpath('output/model') # Update this path as necessary

# Maximum number of epochs for model training
model_maximum_training_epochs = 50 # Update this number as necessary

# Path that points to the output directory of evaluation results
evaluation_results_path = os.path.normpath('output/results') # Update this path as necessary

# Path that points to the output for the metadata csv file
metadata_file_store_path = os.path.normpath('data/metadata/md.csv') # Update this path as necessary