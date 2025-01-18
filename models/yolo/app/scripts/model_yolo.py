import os
import cv2
from ultralytics import YOLO
from scripts.model.model_interface import ModelInterface
# from ..config.settings import model_weights_save_path

FINETUNNED_MODEL_NAME = 'modelv1.pt'

class ModelYolo(ModelInterface):
    def create_model(filepath, device='cpu'):
        """
        Load the YOLO11 model from the .pt file.

        Args:
            device : optional[str]
                The device to load the model on ('cpu' or 'cuda'). Defaults to 'cpu'.

        Returns:
            model: The YOLO11 model.
        """
        model = YOLO(os.path.join(filepath))
        model.to(device)
        return model
    
    def infer_on_image(model, image):
        """
        Perform inference on a single image using the YOLO11 model.

        Parameters
        ----------
        model : The trained YOLO11 model
        
        image : The image as a numpy array
        
        Returns
        -------
        boxes : A numpy array containing the bounding boxes from the predictions found by the model
        
        labels : A numpy array containing all label ids of the predictions found by the model
        
        scores : A numpy array containing the scores for all predictions found by the model
        """
        og_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = model(og_img)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        scores = results[0].boxes.conf.cpu().numpy()
        labels = results[0].boxes.cls.cpu().numpy().astype(int)

        return boxes, labels, scores
    
    def evauate(model):
        """
        Evaluate the model on the validation dataset.

        Parameters:
        Model - The YOLO11 model to be validated

        Returns:
        Model evaluation
        """
        return model.val()