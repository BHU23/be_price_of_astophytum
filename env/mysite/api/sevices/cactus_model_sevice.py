import base64
import numpy as np
from PIL import Image
from io import BytesIO
from tensorflow.keras.models import model_from_json,load_model
import logging
import base64
from dotenv import load_dotenv

from ..models import Class
load_dotenv()


# Configure logger
logger = logging.getLogger('mylogger')

def process_image(image):
    try:
        model = load_model('C:/Users/huawei/Desktop/ปี  4  เทอม  1/Project/price_of_astrophytum_be/env/mysite/api/models/model4.h5')
        model.summary()

        predictions = model.predict(image)
        predicted_classes = np.argmax(predictions, axis=1)
        class_labels = ['normal', 'special']
        listpredicted = [class_labels[i] for i in predicted_classes]
        logger.info(f"listpredicted {listpredicted}", exc_info=True)
        if len(listpredicted) > 0:
            logger.info(f"listpredicted true", exc_info=True)
            if listpredicted[0] == "normal":
                logger.info(f"listpredicted normal", exc_info=True)
                return "normal",[1]
            elif(listpredicted[0] == "special"):
                logger.info(f"listpredicted special", exc_info=True)
                return "special",[0]
        else :
            logger.info(f"listpredicted false", exc_info=True)
            return "error",[]

    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        return "error",[]
    
def specail_image(image):
    try:
        # Load the model
        model = load_model('C:\\Users\\huawei\\Desktop\\ปี  4  เทอม  1\\Project\\price_of_astrophytum_be\\env\\mysite\\mysite\\models\\model5s.h5')
        model.summary()
        
        predictions = model.predict(image)
        logger.info(f"Predicted value: {predictions}", exc_info=True)
        threshold = 0.1

        # Find indices where predictions exceed the threshold
        predicted_indices = np.where(predictions[0] > threshold)[0]
        logger.info(f"predicted_indices: {predicted_indices}", exc_info=True)
        # Define class labels
        class_labels = ["starshape-high", "starshape-medium", "starshape-low", 
                        "Vtype-high", "Vtype-low", "variegated-high", 
                        "variegated-low", "variegated-medium", "rensei", 
                        "cristatum"]

        # Map predictions to class labels
        listpredicted = [class_labels[i] for i in predicted_indices]
        logger.info(f"Predicted classes: {listpredicted}", exc_info=True)

        # Prioritize levels for "starshape"
        starshape_levels = None
        if any("starshape-high" in pred for pred in listpredicted):
            starshape_levels = "high"
        elif any("starshape-medium" in pred for pred in listpredicted):
            starshape_levels = "medium"
        elif any("starshape-low" in pred for pred in listpredicted):
            starshape_levels = "low"

        logger.info(f"Starshape level: {starshape_levels}", exc_info=True)

        # Prioritize levels for "Vtype"
        # Vtype_levels = None
        # if any("Vtype-high" in pred for pred in listpredicted):
        #     Vtype_levels = "high"
        # elif any("Vtype-low" in pred for pred in listpredicted):
        #     Vtype_levels = "low"

        # logger.info(f"Vtype level: {Vtype_levels}", exc_info=True)

        # Prioritize levels for "variegated"
        variegated_levels = None
        if any("variegated-high" in pred for pred in listpredicted):
            variegated_levels = "high"
        elif any("variegated-medium" in pred for pred in listpredicted):
            variegated_levels = "medium"
        elif any("variegated-low" in pred for pred in listpredicted):
            variegated_levels = "low"

        logger.info(f"Variegated level: {variegated_levels}", exc_info=True)

        # Create a new list including prioritized levels and other predictions
        listpredicted_new = []

        if starshape_levels:
            listpredicted_new.append(f"starshape-{starshape_levels}")
        # if Vtype_levels:
        #     listpredicted_new.append(f"Vtype-{Vtype_levels}")
        if variegated_levels:
            listpredicted_new.append(f"variegated-{variegated_levels}")

        # Add other predictions (e.g., "rensei", "cristatum") that are not part of the levels
        # other_predictions = [pred for pred in listpredicted if "starshape" not in pred and "Vtype" not in pred and "variegated" not in pred]
        other_predictions = [pred for pred in listpredicted if "starshape" not in pred and "variegated" not in pred]
        listpredicted_new.extend(other_predictions)

        logger.info(f"New predicted classes: {listpredicted_new}", exc_info=True)
        # Initialize response variables
        classes = []
        class_ids = []

        # Check predictions and handle each class label separately
        if len(listpredicted_new) > 0:
            logger.info(f"Predictions available", exc_info=True)
                
            for prediction in listpredicted_new:
       
                try:
                    matching_class = Class.objects.get(name__iexact=prediction)
                    logger.info(f"Class is {matching_class.name}", exc_info=True)
                    classes.append(matching_class.name)
                    class_ids.append(matching_class.id)
                except Class.DoesNotExist:
                    logger.info(f"No matching class found for prediction: {prediction}", exc_info=True)
                    classes.append("Unknown")
                    class_ids.append(0)
            return classes, class_ids
        else:
            logger.info(f"No predictions", exc_info=True)
            return "error", []
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        return "error", []


def convert_image(base64_image):
    # Ensure that base64_image is a string before processing
    if isinstance(base64_image, str):
        if base64_image.startswith('data:image'):
            base64_image = base64_image.split(',')[1]

        image_data = base64.b64decode(base64_image)
        logger.info(f"image_data: {image_data}")

        try:
            image = Image.open(BytesIO(image_data)).convert('RGB')
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            return ""

        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)
        logger.info(f"image done!!!!")
        return image
    else:
        logger.error("Input is not a base64 encoded string.")
        return None
