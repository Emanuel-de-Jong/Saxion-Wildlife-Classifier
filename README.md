# Wildlife Classifier

## About the project
The decline of meadow bird populations in the Netherlands has become a critical issue, exacerbated by predator pressure and habitat changes. To assist site/field administrators in making area management decisions, we propose a monitoring system that leverages computer vision (CV) and data pipelines to improve wildlife management strategies.

### Team
#### Internal project managers:
Faizan Ahmed (faizan.ahmed@utwente.nl) \
Deepak Tunuguntla (d.r.tunuguntla@saxion.nl)

#### Researchers first group:
Tiko Miedendorp de Bie (t.j.miedendorpdebie@student.utwente.nl) \
Ernests Rudzitis (e.rudzitis@student.utwente.nl) \
Ruben van der Linde (r.g.a.vanderlinde@student.utwente.nl) \
Dirck Mulder (d.mulder-2@student.utwente.nl)

#### Researchers second group:
Erik Markvoort (519894@student.saxion.nl) \
Robert Toeter (524043@student.saxion.nl) \
Simon Vermaat (515389@student.saxion.nl) \
Dominique Vos (445289@student.saxion.nl) \
Emanuel de Jong (495804@student.saxion.nl)

## Usage

### Prerequisites
- Windows or Linux (Mac OS might work with the Linux approach but is untested)
- Python 3.10.11

### Installation
0. For Linux, use the root user:
    ```
    su
    ```

1. Clone the repository:
    ```
    git clone https://github.com/deepaktunuguntla/2024-RAAK-PRO-BBB-BDT-G1-AnimalMonitoring.git
    ```

2. Install Poetry and Python packages:
    ```
    pip install poetry
    poetry install
    ```

3. Install Docker:
    - For Windows install [Docker Desktop](https://www.docker.com/get-started/).
    - For Linux follow [this guide](https://docs.docker.com/engine/install/).

### Running
1. Start the program:
    - For Windows double click `run.bat` or run it from a console.
    - For Linux run:
        ```
        bash run.sh
        ```
2. A webpage will open.
    1. Add the path to the folder with images you wish to infer and configure your settings. You can choose to save them so they are the same next time you run the program. You may also set these before running the program in `settings.yml` if you prefer it that way.
    2. Press `Start` and go to the console window. The inference has started. **The first time the program runs on a computer, it will take 5-15 minutes!**
3. When everything is done, a window for each model used will open to show its results. Close them to finish the program.
4. The annotations and statistics are also saved in the `results` folder. **THEY WILL BE DELETED the next time the program runs, so save them somewhere!**

## File and folder structure
**frontend**: The webpage that opens at the start. \
**gui**: The GUI that shows the results at the end. \
**models**: The NNs and their inference code. \
**postprocessing**: Filters image batches and creates stats from inference results. \
**\*results**: Has the results as json files per model. \
**util_scripts**: Has small scripts we used throughout the project as well as prototypes for big features that ended up being discarded. \
**main.py**: The root code that manages the flow of the program. Is called by `run.bat/.sh`. Can't be run directly! \
**pyproject.toml**: Has the Python dependencies for `main.py`. \
**\*README.md**: This file. Has instructions and information. \
**\*run.bat**: Starts the program on Windows. \
**\*run.sh**: Starts the program on Linux. \
**settings.yml**: Can be used as an alternative to the frontend form to change the programs behavior.

\* Important for users

## Advanced project information (For contributors)

### Input images
The project requires images that include a bar at the bottom displaying the date, time and camera name. The date and time are utilized during post-processing to filter out duplicate images of the same animal captured multiple times. This information also helps identify when specific animals were spotted, which camera captured them, and the leging associated with the image.

### Implemented models
- The pipeline makes use of YOLOv11 and EfficientDet for inferencing the input images. These models are run in a separate docker containers. When the frontend is started, the user can choose which model they want to use for inferencing the images. We highly recommend not to use Detectron2 at all cost if you value your time and sanity!

### Evaluation & Results
- **Viewing metrics or visualizations**: The statistics of the inferenced images are being shown using Tkinter.
- **Output files**: Output files from the pipeline are json files with all the annotated images, annotation of each leging that has been uploaded and a statistic json file that shows the same statistics as seen in Tkinter. These files are saved in the results folder.

### Testing
- Docker images are automatically reused once build, even if changes were made. Make sure to delete the images and builds with code or file changes.

## License
MIT License, refer to `LICENSE` file
