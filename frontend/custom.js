const MODELS = ['yolo', 'efficient_det'];
const OPTIONS = ['visualize_annotations', 'visualize_statistics', 'filter_batches'];

const statusElement = document.getElementById('status');
const imageDirPathInput = document.getElementById('image_dir_path');
const saveSettingsCheck = document.getElementById('save_settings');
const submit_button = document.getElementById('submit_button');

let modelChecks = {};
for (const model of MODELS) {
    modelChecks[model] = document.getElementById(model);
}

let optionChecks = {};
for (const option of OPTIONS) {
    optionChecks[option] = document.getElementById(option);
}

submit_button.addEventListener('click', async () => {
    submit_button.disabled = true;

    const imageDirPath = imageDirPathInput.value;

    let modelsToInference = [];
    for (const model in modelChecks) {
        if (modelChecks[model].checked) {
            modelsToInference.push(model);
        }
    }

    let options = {};
    for (const option of OPTIONS) {
        options[option] = document.getElementById(option).checked;
    }

    let saveSettings = saveSettingsCheck.checked;

    let response;
    try {
        response = await fetch('http://127.0.0.1:8000/post-form', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify({
                image_dir_path: imageDirPath,
                models_to_inference: modelsToInference,
                options: options,
                save_settings: saveSettings,
            }),
        });
    } catch (error) {
        console.error(error);
        alert('Error: ' + error);

        submit_button.disabled = false;
        return;
    }

    if (!response.ok) {
        console.error(response);
        alert('Status code: ' + response.status);
        
        submit_button.disabled = false;
        return;
    }

    const data = await response.json();
    console.log(data);

    statusElement.textContent = "Inference started. Please open up the console window to view progress and potential problems.";
    statusElement.style.display = "block";
});

async function fetchSettings() {
    let response;
    try {
        response = await fetch('http://localhost:5500/settings.yml');
    } catch (error) {
        console.error(error);
        alert('Error: ' + error);
        return;
    }

    if (!response.ok) {
        console.error(response);
        alert('Status code: ' + response.status);
        return;
    }

    const text = await response.text();
    const settings = jsyaml.load(text);
    
    if (settings.image_dir_path.length > 0) {
        imageDirPathInput.value = settings.image_dir_path;
    }

    for (const model in modelChecks) {
        modelChecks[model].checked = settings.models_to_inference.includes(model);
    }

    for (const option in optionChecks) {
        if (!settings.options.hasOwnProperty(option)) {
            continue;
        }
        
        optionChecks[option].checked = settings.options[option];
    }
};

fetchSettings();
