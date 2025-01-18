import subprocess
import webbrowser
import os
import yaml
import platform
import shutil
import asyncio
import traceback
import signal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

"""
We are SO sorry for the monster below!

We hope you can forgive us!

May the lord have mercy on you
:)
"""


SETTINGS_PATH = 'settings.yml'
FRONTEND_PATH = 'frontend'
FRONTEND_SETTINGS_PATH = os.path.join(FRONTEND_PATH, SETTINGS_PATH)
MODELS_PATH = 'models'
CUDA_IMAGE = 'nvidia/cuda'
CUDA_IMAGE_VERSION = '12.1.1-base-ubuntu22.04'
NON_CUDA_IMAGE = 'python'
NON_CUDA_IMAGE_VERSION = '3.10.11-slim'
RESULTS_PATH = 'results'
ERROR_FILENAME = 'error.log'
POSTPROCESSING_PATH = 'postprocessing'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PostFormRequest(BaseModel):
    image_dir_path: str
    models_to_inference: list[str]
    options: dict[str, bool]
    save_settings: bool

@app.post("/post-form")
async def post_form(request: PostFormRequest):
    image_dir_path = request.image_dir_path
    if not image_dir_path or len(image_dir_path) == 0:
        raise HTTPException(status_code=400, detail="image_dir_path is required.")
    
    models_to_inference = request.models_to_inference
    if not models_to_inference or len(models_to_inference) == 0:
        raise HTTPException(status_code=400, detail="models_to_inference is required.")
    
    options = request.options
    if not options or len(options) == 0:
        raise HTTPException(status_code=400, detail="options is required.")
    
    save_settings = request.save_settings
    if save_settings == None:
        raise HTTPException(status_code=400, detail="save_settings is required.")
    
    settings = {
        'image_dir_path': image_dir_path,
        'models_to_inference': models_to_inference,
        'options': options
    }
    
    asyncio.create_task(async_start_inference_middleman(settings, save_settings))

async def async_start_inference_middleman(settings, save_settings):
    # Give FastAPI time to send HTTP response
    await asyncio.sleep(0.5)
    handle_exceptions(start_inference, settings, save_settings)

def start_inference(settings, save_settings):
    if save_settings:
        with open(SETTINGS_PATH, 'w') as file:
            yaml.dump(settings, file)
    
    settings["image_dir_path"] = make_absolute(settings["image_dir_path"])
    
    run_models(settings)
    run_postprocessing(settings)
    if settings['options']['visualize_annotations'] or settings['options']['visualize_statistics']:
        run_gui(settings)
    
    os.kill(os.getpid(), signal.SIGTERM)

def get_settings(location):
    '''
    Get the front end settings

    Parameter
    -----
    location
        String

    Return
    -----
    settings
        dictionary
    '''
    with open(location, 'r') as file:
        settings = yaml.safe_load(file)
    
    return settings

def can_use_cuda():
    '''
    Check if the machine, that this code runs on, can use cuda
    
    Return
    -----
        True -> if cuda can be used\n
        False -> if cuda can't be used
    '''
    try:
        # Determine if where or which should be used
        command = 'where' if platform.system() == 'Windows' else 'which'
        # Attempt to locate nvidia-smi
        result = subprocess.run([command, 'nvidia-smi'], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            os.environ['NVIDIA_GPU'] = 'found'
            return True
    except subprocess.CalledProcessError:
        # The subprocess failed, because the current machine doesn't have nvidia
        pass
    return False

def check_results(path, content_check_file='annotations.json'):
    error_log_path = os.path.join(path, ERROR_FILENAME)
    if os.path.exists(error_log_path):
        with open(error_log_path, 'r') as file:
            error = file.read()
        raise Exception(error)
    
    content_path = os.path.join(path, content_check_file)

    if not os.path.exists(content_path):
        error_msg_prefix = os.path.basename(path) if content_check_file == "annotations.json" else f"Postprogress {os.path.basename(path)}"
        raise Exception(f"{error_msg_prefix} stopped but did not create '{content_check_file}'")

def make_absolute(path):
    if not os.path.isabs(path):
        return os.path.abspath(path)
    return path

def run_postprocessing(settings):
    settings_models = settings['models_to_inference']
    used_models = ','.join(settings_models)
    filter_batches = settings['options']['filter_batches']
    results_dir = os.path.abspath(RESULTS_PATH)

    subprocess.run(['docker', 'build', '-t', 'postprocess_image'
                        , '--build-arg', f'IMAGE={NON_CUDA_IMAGE}'
                        , '--build-arg', f'VERSION={NON_CUDA_IMAGE_VERSION}'
                        , '--build-arg', f'USED_MODELS={used_models}'
                        , '--build-arg', f'FILTER_BATCHES={filter_batches}', '.'], cwd=POSTPROCESSING_PATH)

    subprocess.run(['docker', 'run', '--name', 'postprocess_container'
                            , '--mount', f'type=bind,source={results_dir},target=/app/results'
                            , '--mount', f'type=bind,source={settings["image_dir_path"]},target=/app/images'
                            , 'postprocess_image'])

    # Stop the containter
    subprocess.run(['docker', 'stop', 'postprocess_container'])

    # Remove the container
    subprocess.run(['docker', 'rm', 'postprocess_container'])

    for model in settings_models:
        results_model_path = os.path.join(RESULTS_PATH, model)
        check_results(results_model_path, content_check_file='stats.json')

def run_gui(settings):
    tasks = []
    for model in settings['models_to_inference']:
        command = ['poetry', 'run', 'python', '-m', 'main', settings["image_dir_path"], \
                    str(settings['options']['visualize_annotations']), \
                    str(settings['options']['visualize_statistics']), \
                    model]
        tasks.append(subprocess.Popen(command, cwd='gui'))
    
    for task in tasks:
        task.wait()

def run_models(settings):
    '''
    Run the chosen models in their containers

    Parameter
    -----
    model_options - list
        A list with the models that needs to be used
    '''
    use_cuda = can_use_cuda()
    use = 'GPU' if use_cuda else 'CPU'
    image = CUDA_IMAGE if use_cuda else NON_CUDA_IMAGE
    image_version = CUDA_IMAGE_VERSION if use_cuda else NON_CUDA_IMAGE_VERSION
    results_dir = os.path.abspath(RESULTS_PATH)
    
    for model in settings["models_to_inference"]:
        model_dockerfile_path = os.path.join(MODELS_PATH, model)
        
        results_model_path = os.path.join(RESULTS_PATH, model)
        if os.path.exists(results_model_path):
            shutil.rmtree(results_model_path)
        os.mkdir(results_model_path)
        open(os.path.join(results_model_path, '.gitkeep'), 'a').close()

        images = subprocess.run(['docker', 'image', 'inspect', f'{model}_image'], stdout=subprocess.PIPE)
        
        check_result = images.stdout
        if f'{model}_image' not in str(check_result):
            # Make the image
            print(f"Docker image '{model}_image' does not exist!")
            subprocess.run(['docker', 'build', '-t', f'{model}_image'
                        , '--build-arg', f'USE={use}'
                        , '--build-arg', f'IMAGE={image}'
                        , '--build-arg', f'VERSION={image_version}', '.'], cwd=model_dockerfile_path)
        else:
            print(f"Docker image '{model}_image' already exists, skipping docker build for that image!")
        
        # Run the container
        if use_cuda:
            subprocess.run(['docker', 'run', '--name', f'{model}_container'
                            , '--mount', f'type=bind,source={results_dir},target=/app/results'
                            , '--mount', f'type=bind,source={settings["image_dir_path"]},target=/app/images'
                            , '--gpus', 'all', '-it'
                            , f'{model}_image'])
        else:
            subprocess.run(['docker', 'run', '--name', f'{model}_container'
                            , '--mount', f'type=bind,source={results_dir},target=/app/results'
                            , '--mount', f'type=bind,source={settings["image_dir_path"]},target=/app/images'
                            , f'{model}_image'])

        # Stop the containter
        subprocess.run(['docker', 'stop', f'{model}_container'])

        # Remove the container
        subprocess.run(['docker', 'rm', f'{model}_container'])

        check_results(results_model_path)

def prepare():
    if os.path.exists(ERROR_FILENAME):
        os.remove(ERROR_FILENAME)
    
    start_frontend()

def start_frontend():
    '''
    This will open the frontend and start the backend
    '''
    
    shutil.copyfile(SETTINGS_PATH, FRONTEND_SETTINGS_PATH)

    # Start the frontend and open a webpage
    frontend_process = subprocess.Popen(["python", "-m" "http.server", "--directory", "frontend", "5500"])
    webbrowser.open("http://localhost:5500")

def handle_exceptions(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as exception:
        traceback.print_exc()
        error_message = str(exception)
        with open(ERROR_FILENAME, 'w') as file:
            file.write(error_message)
        exit(1)

handle_exceptions(prepare)
