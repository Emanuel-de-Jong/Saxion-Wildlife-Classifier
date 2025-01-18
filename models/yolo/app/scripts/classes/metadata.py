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

import numpy as np
from ..config.constants import IMAGE_METADATA_HEIGHT
# from ..config.settings import pytesseract_executable_path

# !IMPORTANT For Installing pytesseract refer to config/settings.py
# pytesseract.pytesseract.tesseract_cmd = pytesseract_executable_path

class MetadataProvider:
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