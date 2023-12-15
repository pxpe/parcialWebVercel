import os
from dotenv import load_dotenv
import cloudinary 

load_dotenv()

cloud_name = os.getenv("CLOUD_NAME")
api_key = os.getenv("CLOUD_API_KEY")
api_secret = os.getenv("CLOUD_API_SECRET")


cloudinary.config( 
  cloud_name = cloud_name, 
  api_key = api_key, 
  api_secret = api_secret 
)