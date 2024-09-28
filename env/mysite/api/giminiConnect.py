
"""
Install the Google AI Python SDK

$ pip install google-generativeai
"""
import base64
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Specify the path to the image file
# image_path = r"C:\Users\huawei\Desktop\ปี  4  เทอม  1\Project\be_price_of_astophytum\env\mysite\api\not-cactus.jpeg" 
# image_path = r"C:\Users\huawei\Desktop\ปี  4  เทอม  1\Project\be_price_of_astophytum\env\mysite\api\cactus.jpg" 
image_path = r"C:\Users\huawei\Desktop\ปี  4  เทอม  1\Project\be_price_of_astophytum\env\mysite\api\superkabuto_startype_31.jpg" 


uploaded_file = upload_to_gemini(image_path, mime_type="image/jpeg")
print(uploaded_file)
prompt = (
    "What is this image? If it is a cactus astrophytum asterias nudum image, "
    "return 2000. If it is a cactus of another species, return 3000. "
    "Otherwise, return 4000."
)
result = model.generate_content(
    [uploaded_file, "\n\n", prompt]
)

# Print the generated result
print(result.text)
