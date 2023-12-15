from cloudinary.uploader import upload_image
import cloudinaryModule.config as config
from uuid import uuid4
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def upload_image_path(file: FileStorage):
        
    public_id = uuid4()

    file.filename = str(public_id)
    response = upload_image(file, folder="public/examen")
    
    if response is None:
        raise Exception("Error al subir imagen")

    print(response.build_url())

    return response.build_url()