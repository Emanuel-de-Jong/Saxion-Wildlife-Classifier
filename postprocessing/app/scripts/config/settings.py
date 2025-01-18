"""
settings.py

Configuration file for setting up paths and other postprocess-wide settings.

Tesseract OCR Setup Instructions:
1) Install Tesseract OCR: Follow instructions at https://github.com/UB-Mannheim/tesseract/wiki.
2) Add the Tesseract installation directory to your system PATH or provide the absolute path below.
3) Install the pytesseract Python package using: `pip install pytesseract`.

Tesseract Executable Path:
- `pytesseract_executable_path`: List with possible OS paths where the Tesseract executable can be found (if the default installation path hasn't been changed).
                                This will automatically be changed to the correct path for the current OS.
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