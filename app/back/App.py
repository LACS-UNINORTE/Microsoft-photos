from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_httpauth import HTTPBasicAuth
import flask_excel as excel
from flask_cors import CORS
from flask_paginate import Pagination #Importando paquete de paginación


#Importaciones de modulos
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
from services.config import DevelopmentConfig
from repository.SQL_query import *
from controllers.Home import *
from controllers.Admin import *
import pickle
import requests
import threading 
import subprocess
import concurrent.futures
from datetime import datetime
import os
import cv2

import numpy as np
import base64

from PIL import Image
from io import BytesIO
import io

# initializations
app = Flask(__name__, template_folder='../front/templates', static_folder='../front/static')

app.config.from_object(DevelopmentConfig)
CORS(app)

#Autenticacion
auth = HTTPBasicAuth()

def ejecutar_clasificacion():
    subprocess.Popen(["python","recog_id_faces.py"])



#Pagina inicial
@app.route('/')
def Home():
    return render_template('home.html')


#Verificacion de admins, login
@auth.verify_password
def verify_password(username, password):
    username=verify_password_home(username, password)
    return username

#Routes funcionarios
@app.route('/funcionarios')
@auth.login_required
def Home_funcionarios():
    data_final = home_funcionarios()
    return render_template('Home_funcionarios.html', Solicitudes = data_final)



#CRUD admin

@app.route('/admin')
@auth.login_required
def Admins():
    showAdmins=admin_main()
    users=showAdmins[0]
    admins=showAdmins[1]
    return render_template('admins.html', admins = admins)


@app.route('/add_admin', methods=['POST'])
@auth.login_required
def Add_admin():
    message=add_admin()
    flash(message)
    return redirect(url_for('Admins'))


@app.route('/edit_admin/<id>', methods=['POST', 'GET'])
@auth.login_required
def Get_admin(id):
    admin=edit_admin(id)
    return render_template('edit-admin.html', admin = admin)


@app.route('/update_admin/<id>', methods=['POST'])
@auth.login_required
def Update_admin(id):
    message=update_admin(id)
    flash(message)
    return redirect(url_for('Admins'))


@app.route('/delete_admin/<string:id>', methods=['POST','GET'])
@auth.login_required
def Delete_admin(id):
    message=delete_admin(id)
    flash(message)
    return redirect(url_for('Admins'))

@app.route('/ejecutar_tarea', methods=['POST'])
@auth.login_required
def ejecutar_tarea():
    if request.method == 'POST':
        # Cuando se presione el botón, crea un nuevo hilo y ejecuta la tarea
        path=os.getcwd()
        print(path)
        thread = threading.Thread(target=ejecutar_clasificacion)
        thread.start()
    return redirect(url_for('Caras_reconocidas'))

@app.route('/caras_reconocidas')
@auth.login_required
def Caras_reconocidas():
    faces = []
    photos = get_photo_db()
    for row in photos:
        ph = pickle.loads(row[1])

        faces.append((ph.decode("UTF-8"),row[0],row[2]))
    return render_template('galeria.html', imagenes=faces)



@app.route('/busqueda', methods=['GET', 'POST'])
@auth.login_required
def redireccion():
    name = None  # Inicializa la variable name
    
    if request.method == 'POST':
        name = request.form['name']
        current_url = request.form.get('current_url')
   
        id_db = get_id_wname_db(name)
        
        if id_db:
            for id_name in id_db:
                id = id_name[0]
            return redirect(url_for('show_related_photos', id=id))
        else:
             flash("No se encontraron coincidencias para el nombre proporcionado.")
             return redirect(current_url)
   
  

@app.route('/busqueda/<id>',methods=['GET'])
@auth.login_required
def show_related_photos(id):
    count =  get_rp_count_db(id)
    app_id = '69b42475-11c2-4a72-8f2d-54796e1da8f6'
    scopes = ['Files.Read']
    
    access_token = generate_access_token(app_id, scopes=scopes)
    headers = {'Authorization': 'Bearer ' + access_token['access_token']}
    thumbnail_urls = []
    page_num = request.args.get('page', 1, type=int)
    per_page = 20

    start_index = (page_num - 1) * per_page + 1
  
    resultados = get_related_photo_db(id,per_page,start_index - 1)
    file_ids = [fila[0] for fila in resultados]
    size = "medium"
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        thumbnail_urls = list(executor.map(lambda file_id: get_thumbnail_url(file_id, headers,size), file_ids))
        
    end_index = min(start_index + per_page, count)

    if end_index > count:
        end_index = count
   
    pagination = Pagination(page=page_num, total=count, per_page=per_page,
                            display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({count})</strong>")

    arreglo_resultante = np.column_stack(( thumbnail_urls,file_ids))

    person=[]
    perfil = get_photo_id_db(id)
    for row in perfil:
        foto_cara = pickle.loads(row[0])
        person.append((foto_cara.decode("UTF-8"),row[1]))


    return render_template('galeria_id.html',foto_cara=person,id=id,resultados= arreglo_resultante, pagination=pagination)

@app.route('/busqueda/<int:caras_id>/photos/<foto_id>')
@auth.login_required
def mostrar_fotos(caras_id, foto_id):
  
    app_id = '69b42475-11c2-4a72-8f2d-54796e1da8f6'
    scopes = ['Files.Read']
    
    access_token = generate_access_token(app_id, scopes=scopes)
    headers = {'Authorization': 'Bearer ' + access_token['access_token']}
    
	
    file_info=get_web_url(foto_id,headers)
    file_name = file_info.get('name', '')

    file_ids=[]
    rectangles = []
    faces = []

    resultados = get_related_faces_db(foto_id)

    for fila in resultados:
        (x, y, w, h )= map(int, fila[1].split(','))
        rectangles.append({"x": x, "y": y, "w": w, "h": h})
        file_ids.append(fila[0])
        
    for ID in file_ids:
        photos = get_photo_BID_db(ID)
        for row in photos:
            foto_cara = pickle.loads(row[1])
            faces.append((foto_cara.decode("UTF-8"),row[0],row[2]))

    if es_video(file_name):
       
        size="large"
        image=get_thumbnail_url(foto_id, headers,size)
        url_info = get_web_url(foto_id,headers)
        web_url = url_info.get('webUrl', '')
        return render_template('galeria_id_video.html',web_url=web_url,faces=faces,imagen=image,caras_id=caras_id)
        
    else:
       

        image = get_content_url(foto_id,headers)
        np_img = np.array(image)
        rgb_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
        img_bytes = cv2.imencode('.jpeg', rgb_img)[1].tobytes()	
        base64_encoded = base64.b64encode(img_bytes)

        return render_template('galeria_id_photo.html',rectangles=rectangles,faces=faces,imagen=base64_encoded.decode("UTF-8"),caras_id=caras_id)



@app.route('/add_name_face/<id>',methods=['POST'])
@auth.login_required
def agregar_nombre_cara(id):
    if request.method == 'POST':
        nombre = request.form['name']
        message=add_name_db(id,nombre)
        flash("nombre agregado correctamente")
    return redirect(url_for('show_related_photos',id=id))


def get_thumbnail_url(file_id,headers,size):

    url = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/thumbnails/0/{size}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('url')
    else:
        # Manejar errores adecuadamente
        return None
    
def get_content_url(file_id,headers):

    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
    response = requests.get(url, headers=headers)

    if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image'):
        image = Image.open(BytesIO(response.content))
        return image
    else:
        return None
    
def get_web_url(file_id,headers):

    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200 :
        file_info = response.json()
        return file_info
    else:
        return None
    
def es_video(file_name):
    extensiones_video = ['.mp4', '.avi', '.mov', '.mkv']  # Agrega las extensiones de video que desees reconocer

    # Obtener la extensión del archivo
    _, extension = os.path.splitext(file_name)

    # Verificar si la extensión corresponde a un video
    return extension.lower() in extensiones_video
    



#Despliegue de la app
if __name__ == '__main__':
    excel.init_excel(app)
    
    app.run(host="0.0.0.0")



