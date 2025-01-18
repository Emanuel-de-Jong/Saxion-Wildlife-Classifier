"""
MetadataProvider Class

This class is designed for managing and extracting metadata from images, particularly focusing on 
the extraction of date, time, and camera information located at the bottom of images. It supports 
two operational modes: "preprocessing" for managing a CSV file of metadata and "inference" for 
extracting metadata without writing to a file.

Key Features:
- Initializes a metadata file or loads an existing one in preprocessing mode.
- Uses Optical Character Recognition (OCR) to extract relevant information from images.
- Provides functionality to create new entries in the metadata DataFrame.
- Supports saving the DataFrame to a CSV file.

Usage Example:
1. Create an instance of MetadataProvider in preprocessing mode:
   metadata_p = MetadataProvider(filepath='./scripts/md.csv')

2. Load an image and create an entry:
   from PIL import Image
   image = Image.open('./scripts/publicpreview.jpg')
   metadata_p.create_entry('unique_id_123', image, {'accuracy_sum': '0.5', 'count': '1'})

3. Save the metadata to a CSV file:
   metadata_p.save()

4. To extract metadata from an image:
   date, time, camera = metadata_p.extract_metadata(image)

5. To retrieve the DataFrame of metadata:
   df = metadata_p.get_df()

Note: Ensure Tesseract OCR is properly installed and configured in your environment.
"""

import os
from datetime import datetime
import pandas as pd
import numpy as np
import pytesseract
import re
from ..config.constants import IMAGE_METADATA_HEIGHT
from ..config.settings import pytesseract_executable_path

# !IMPORTANT For Installing pytesseract refer to config/settings.py
pytesseract.pytesseract.tesseract_cmd = pytesseract_executable_path

class MetadataProvider:
    def __init__(self, filepath: str = None, overwrite: bool = True, mode: str = "preprocessing") -> None:
        """
        Initializes the metadata provider utility class

        Parameters
        ----------
        filepath : optional[str]
            Filepath to the CSV metadata file. Required if in "preprocessing" mode.
            
        overwrite : optional[bool]
            Mode of operation - "preprocessing" to manage possible existing metadata file. If True, completely overwrites the contents of the file, otherwise operates in append mode. True by default.
        
        mode : optional[str]
            Mode of operation - "preprocessing" to manage metadata file, or "inference" to only perform metadata extraction. 
            Defaults to "preprocessing".
        """
        
        self.filepath = filepath
        self.mode = mode
        
        # Initialize the DataFrame and handle file creation in preprocessing mode
        if self.mode == "preprocessing":
            if self.filepath is None:
                raise ValueError("Filepath must be provided in 'preprocessing' mode.")

            # Create directories if they don’t exist
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            # Create or load the CSV file based on the overwrite flag
            if not os.path.exists(self.filepath) or overwrite:
                with open(self.filepath, 'w'):
                    pass
                
                self.df = pd.DataFrame()
                print("[MetadataProvider] Initialized an empty file.")
            else:
                # Try to load an existing csv file
                try:
                    self.df = pd.read_csv(self.filepath)
                    print("[MetadataProvider] Loaded existing metadata.")
                except Exception as e:
                    self.df = pd.DataFrame()
                    print("[MetadataProvider] Error loading file:", e)      
        # The provided mode was inference, no csv operations are supported              
        elif self.mode == "inference":
            print("[MetadataProvider] Initialized in inference mode. CSV file operations are disabled.")
        else:
            raise ValueError("Invalid mode. Use 'preprocessing' or 'inference'.")

    def extract_metadata(self, image: np.ndarray):
        """
        Extracts metadata information from the bottom of an image.
 
        Parameters
        ----------
        image : np.ndarray
            Image loaded as numpy array.

        Returns
        -------
        date : str or None
            The extracted date from the image, or None if not found.
            
        time : str or None
            The extracted time from the image, or None if not found.
            
        camera : str or None
            The extracted camera identifier from the image, or None if not found.
        """
        
        # The image must be of type of np.ndarray
        if (type(image) != np.ndarray):
            image = np.array(image)

        # Convert to uint8 if the image is in a different format
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        # Check if the image has the expected metadata dimensions
        height, width = image.shape[:2]

        # By analysis, the dataset contains images whose metadata is located at the bottom of the image,
        # thus we crop the image at the bottom to have the most important information
        start_y = height - IMAGE_METADATA_HEIGHT

        if image.ndim == 2:  # Grayscale image with no channel dimension
            image_cropped = image[start_y:height, 0:width]
        elif image.ndim == 3:  # Color image with a channel dimension
            image_cropped = image[start_y:height, 0:width, :] 

        # Use pytesseract to extract text from the bottom area, all detected text is saved
        text = pytesseract.image_to_string(image_cropped, config='--psm 11')
        single_line_text = ' '.join(text.split('\n'))
        lines = single_line_text.split(' ')  # Split text into an array of lines
        lines = [re.sub(r"[^a-zA-Z0-9:/]","", line) for line in lines]
        lines = [line for line in lines if line != ""]  # Remove empty lines

        # Example text: i LAE OSA/T Sa ca 4 i - B AWCO6 O65F 18C 012/04/2024 21:03:34
        # not all text is detected well but important information can be read from camera name, time and date.
        # date and time are converted into a '%m/%d/%Y %I:%M%p' format.

        # Time format 1
        time_format = 1
        matches_time = [word for word in lines if re.match(r'(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d', word)]
        if len(matches_time) > 0:
            matches_time[0] = datetime.strptime(matches_time[0], "%H:%M:%S")
        
        # Time format 2
        if len(matches_time) == 0:
            matches_time = [word for word in lines if re.match(r'(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)', word)]
            if len(matches_time) > 0:
                time_format = 2
                matches_time[0] = datetime.strptime(matches_time[0], "%I:%M%p")
        
        # Time to string
        if len(matches_time) > 0:
            matches_time[0] = matches_time[0].strftime("%H:%M:%S")
        
        date_regex = r"\d{2}/\d{2}/\d{4}"
        matches_date = [re.search(date_regex, word).group() for word in lines if bool(re.compile(date_regex).match(word))]
        if len(matches_date) > 0:
            date1, date2, year = matches_date[0].split('/')
            date1 = int(date1)
            date2 = int(date2)
            year = int(year)
            if (date1 > 12 and date2 > 12) or (date1 > 31 or date2 > 31) or (year < 2000 or year > datetime.now().year):
                matches_date = []
            else:
                if date1 > 12:
                    time_format = 2
                if date2 > 12:
                    time_format = 1
                
                if time_format == 1:
                    matches_date[0] = f"{date2}/{date1}/{year}"
                elif time_format == 2:
                    matches_date[0] = f"{date1}/{date2}/{year}"

        matches_camera = [word for word in lines if re.match(r'^[A-Z0-9]{5,}$', word)]
        matches_camera = [cam.replace("o", "0").replace("O", "0") for cam in matches_camera]
        
        date = matches_date[0] if len(matches_date) > 0 else "01/01/2000"
        time = matches_time[0] if len(matches_time) > 0 else "00:00:00"
        camera = matches_camera[0] if len(matches_camera) > 0 else "UNKNOWN"

        return date, time, camera

    def split_image_and_metadata(self, image: np.ndarray):
        """
        Splits an image into two parts: the main content (without metadata) and the metadata section.

        Parameters
        ----------
        image : np.ndarray
            The original image as a numpy array.

        Returns
        -------
        image_main : np.ndarray
            The image without the metadata portion at the bottom.

        image_metadata : np.ndarray
            The cropped metadata portion from the bottom of the image.
        """
        # Check if the image is a numpy array
        if not isinstance(image, np.ndarray):
            image = np.array(image)

        # Get image dimensions
        height = image.shape[0]

        # Define cropping dimensions for metadata area
        start_y = height - IMAGE_METADATA_HEIGHT
        
        if start_y < 0:
            raise ValueError(f"IMAGE_METADATA_HEIGHT of {IMAGE_METADATA_HEIGHT} is larger than the image height.")

        # Split image into main content and metadata
        if image.ndim == 2:  # Grayscale image
            image_main = image[:start_y, :]
            image_metadata = image[start_y:height, :]
        elif image.ndim == 3:  # Color image
            image_main = image[:start_y, :, :]
            image_metadata = image[start_y:height, :, :]
        else:
            raise ValueError("Unsupported image dimensions.")

        return image_main, image_metadata