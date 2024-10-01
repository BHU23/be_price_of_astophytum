import numpy as np
from PIL import Image
from io import BytesIO
from django.conf import settings
import logging
import os
import io
from ..models import HistoryPrompt,Role,Style,HistoryPredictions
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
logger = logging.getLogger('mylogger')

def analyze_image(image_data):

    if isinstance(image_data, np.ndarray):
        # Squeeze the array to remove any singleton dimensions
        image_data = np.squeeze(image_data)

        # Normalize the data if it's in a float format and convert to uint8
        if image_data.dtype == np.float32 or image_data.dtype == np.float64:
            image_data = (image_data * 255).astype('uint8')  # Scale to [0, 255]

        # Check if the resulting shape is valid for Pillow
        if image_data.ndim == 2:  # Grayscale image
            image = Image.fromarray(image_data, mode='L')
        elif image_data.ndim == 3 and image_data.shape[2] in [3, 4]:  # RGB or RGBA image
            image = Image.fromarray(image_data, mode='RGB' if image_data.shape[2] == 3 else 'RGBA')
        else:
            raise ValueError(f"Unsupported image shape: {image_data.shape}")
    else:
        # If it's already an image file (bytes), open it directly
        image = Image.open(io.BytesIO(image_data))

    # Resize the image before saving
    image = image.resize((800, 800))  # Resize to a maximum of 800x800 pixels

    image_path = os.path.join(settings.MEDIA_ROOT, 'temp_image.jpg')
    
    # Save the resized image
    image.save(image_path, format='JPEG', quality=85)  # Adjust quality as needed

    uploaded_file = upload_to_gemini(image_path, mime_type="image/jpeg")
    
    prompt = (
        "Please identify the object in this image. If it is a real cactus, specifically an Astrophytum asterias nudum, return 2000. "
        "If it is a real cactus but of a different species, return 3000. "
        "If it is a non-real or artificial cactus, return 3001. "
        "For any other type of object, return 4000."
    )
    

    result = model.generate_content([uploaded_file, "\n\n", prompt])

    prediction_value = interpret_result(result.text)

    # Optionally, remove the temporary image file
    os.remove(image_path)

    return prediction_value,uploaded_file

def generated_post(history_prompt: HistoryPrompt, uploaded_file): 
    prompt = (
        f"You are {history_prompt.role_id.name} in Astro asres Nudum, do in task [{history_prompt.prompt}]. "
        "Astro asres Nudum have. "
        f"The type (ลักษณะ) are [{history_prompt.classes}]. "
    )
    if history_prompt.price and "ขาย" in history_prompt.prompt:
        prompt += f"And the price is [{history_prompt.price}]. "

    if history_prompt.role_id.name == "ขาย":
        prompt += "ขายแล้วนะ! สนใจติดต่อได้เลยจ้า 🪴🌵 "
    elif history_prompt.role_id.name == "ผู้ซื้อ":
        prompt += "กำลังตามหา หากใครมีรุ่นนี้ติดต่อมาได้เลย! "
    elif history_prompt.role_id.name == "รีวิว":
        prompt += "รีวิวสินค้าตัวนี้: ความสวยงาม สไตล์สนุกสนาน สุดคุ้ม! "

    prompt += (
        f"Please describe the item for posting on Facebook style text is [{history_prompt.style_id.name}]. "
        "with 4-8 hashtags: "
        "based on the item image details, along with the mandatory hashtags: #classes, #nudum, and #Astro asres. "
        "The description should be written in Thai language. "
        "Keep specific product terms in English where appropriate, such as hashtags: #classes, #nudum, and #Astro asres."
    )


    logger.info(f"prompt: {prompt}", exc_info=True)
    result = model.generate_content([uploaded_file, "\n\n", prompt])

    return result.text



def interpret_result(result_text):
    """Interpret the result from the AI model."""
    if "2000" in result_text:
        return 2000
    elif "3000" in result_text:
        return 3000
    else:
        return 4000

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""

    file = genai.upload_file(path, mime_type=mime_type)
    logger.info(f"Uploads the given file to Gemini.: {file}", exc_info=True)
    return file