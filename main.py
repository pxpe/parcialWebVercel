from flask import Flask, request, render_template, redirect, url_for, session
import pymongo
from bson import ObjectId
import os

from datetime import datetime

import database.database as mongo
from cloudinaryModule.cloudinary import allowed_file, upload_image_path
from mapModule.geocode import get_coords

from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = 'random secret'

OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
OAUTH_SECRET = os.getenv("GOOGLE_OAUTH_SECRET")


# Configuración del cliente de OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=OAUTH_CLIENT_ID,
    client_secret=OAUTH_SECRET,
    #access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    #authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)



@app.route('/', methods=['GET'])
async def home():
    user = session.get('user', None)

    eventos = mongo.eventos.find()
    if request.args.get('direccion'):
        direccion = request.args.get('direccion')

        coordsDireccion = await get_coords(direccion)
        
        print(coordsDireccion)
        MAXDISTANCE = 0.2

        eventos = list(mongo.eventos.find({
            'lat': {
                '$gte': float(coordsDireccion[0]) - MAXDISTANCE,
                '$lte': float(coordsDireccion[0]) + MAXDISTANCE
            },
            'lng': {
                '$gte': float(coordsDireccion[1]) - MAXDISTANCE,
                '$lte': float(coordsDireccion[1]) + MAXDISTANCE
            }
        }))
        
    print(eventos)

    return render_template('principal.html', user=user, eventos=eventos)

@app.route('/crear', methods=['GET','POST'])
async def create():
    user = session.get('user', None)

    if not user:
        return redirect('/login')


    if request.method == 'GET':
        return render_template('create.html', user=user)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        lugar = request.form.get('lugar')
        fecha = request.form.get('fecha')
        imagen = request.files.get('imagen')

        print(fecha)
        print(nombre, lugar, fecha, imagen)

        if not allowed_file(imagen.filename):
            return render_template('create.html', user=user, error='Formato de imagen no válido')

        coords = await get_coords(lugar)

        imagen_path = await upload_image_path(imagen)

        mongo.eventos.insert_one({
            'nombre': nombre,
            'timestamp': fecha,
            'lugar': lugar,
            'coords': {'lat': coords[0], 'lon': coords[1]},
            'organizador': user['email'],
            'imagen': imagen_path,
        })

        return redirect('/')


@app.route('/logs', methods=['GET'])
def logs():
    user = session.get('user', None)
    
    l = list(mongo.logs.find().sort('date',pymongo.DESCENDING))
    
    return render_template('logs.html', user=user, logs=l)

# Rutas de autenticación con Google

@app.route('/login', methods=['GET'])
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/authorize', methods=['GET'])
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    print(user_info)

    # Guardar la información del usuario en la sesión en Logs
    mongo.logs.insert_one({
        'timestamp': datetime.now(),
        'user': user_info['email'],
        'caducidad': token['expires_at'],
        'token': token['access_token']
    })

    session['user'] = user_info
    return redirect('/')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)
