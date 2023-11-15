from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
from services.pyimagesearch.helpers import convert_and_trim_bb
from io import BytesIO
from PIL import Image
import numpy as np
import requests
import imutils
import cv2
import pickle
import base64 
import dlib
from repository.SQL_query import *
import os
import tempfile


APP_ID = '69b42475-11c2-4a72-8f2d-54796e1da8f6'
SCOPES = ['Files.Read','User.Read']
file_ids = '128F10A92846F712%21106'

predictor_path = "shape_predictor_68_face_landmarks_GTX.dat"
face_rec_model_path = "dlib_face_recognition_resnet_model_v1.dat"
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

access_token = generate_access_token(APP_ID, scopes=SCOPES)
headers = {'Authorization': 'Bearer ' + access_token['access_token']}
graph_api_endpoint = GRAPH_API_ENDPOINT + f'/me/drive/items/{file_ids}/children?top=10'

def face_distance(face_encodings, face_to_compare):

    if len(face_encodings) == 0:
        return np.empty((0))

    return np.linalg.norm(face_encodings - face_to_compare, axis=1)

def es_video(file_name):
    extensiones_video = ['.mp4', '.avi', '.mov', '.mkv']  # Agrega las extensiones de video que desees reconocer

    # Obtener la extensión del archivo
    _, extension = os.path.splitext(file_name)

    # Verificar si la extensión corresponde a un video
    return extension.lower() in extensiones_video

def obtener_caras(file_id, es_video=False, factor_de_salto=60):
	descriptors = []	

	file_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
	file_response = requests.get(file_url, headers=headers)
	image_data = file_response.content	


	if es_video:

		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			temp_file.write(file_response.content)
			temp_file_path = temp_file.name
			print(temp_file_path)
		cap = cv2.VideoCapture(temp_file_path)
		conteo_fotogramas = 0

		while cap.isOpened():
			ret, frame = cap.read()

			if not ret:
				break
			conteo_fotogramas += 1
			if es_video and conteo_fotogramas % factor_de_salto != 0:
				continue

			rgb_size = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			rgb_img=frame
			
			np_img_resized = imutils.resize(frame, width=600)
			rgb = cv2.cvtColor(np_img_resized, cv2.COLOR_BGR2RGB)
			dets = detector(rgb, 1)

			for k, d in enumerate(dets):

				shape = sp(rgb, d)
				face_descriptor = np.array(facerec.compute_face_descriptor(rgb, shape))
				if not any((np.array_equal(face_descriptor, existing_descriptor) for existing_descriptor in descriptors)):

					descriptors.append(face_descriptor)

		cap.release()
		temp_file.close()

		os.remove(temp_file_path)

		scale_factor = rgb_size.shape[1] / np_img_resized.shape[1]

	else:
		
			image = Image.open(BytesIO(image_data))
			np_img = np.array(image)
			rgb_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

			np_img_resized = imutils.resize(np_img, width=600)
			rgb = cv2.cvtColor(np_img_resized, cv2.COLOR_BGR2RGB)
			dets = detector(rgb, 1)
			print("Number of faces detected: {}".format(len(dets)))
			for k, d in enumerate(dets):
				shape = sp(rgb, d)
				face_descriptor = np.array(facerec.compute_face_descriptor(rgb, shape))						
				descriptors.append(face_descriptor)
				
			scale_factor = np_img.shape[1] / np_img_resized.shape[1]	


	return (descriptors,dets,scale_factor,rgb_img)

while True:

	response_file_info = requests.get(graph_api_endpoint,headers=headers)
	if response_file_info.status_code == 200:
		data = response_file_info.json()
		for item in data["value"]:
		
			if "file" in item:
				file_name = item["name"]
				file_id = item["id"]
				print(file_id)

				files_db = get_file_db()
				files_exist = [row[0] for row in files_db]
				if file_id not in files_exist:

							
					file_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
					file_response = requests.get(file_url, headers=headers)

					if es_video(file_name):
						print(f"{file_name} es un video.")
						(descriptores_video,dets,scale_factor,rgb_img) = obtener_caras(file_id, es_video=True, factor_de_salto=10)
						nuevos_descriptores=descriptores_video 
						
					else:
						print(f"{file_name} no es un video.")
						(descriptores_imagen,dets,scale_factor,rgb_img) = obtener_caras(file_id, es_video=False)
						nuevos_descriptores=descriptores_imagen 

					result = get_face_db()

					if not result:
						for  d,nuevo_descriptor in zip(dets,nuevos_descriptores):

							(x, y, w, h) =  convert_and_trim_bb(rgb_img, d,scale_factor)
							print((x, y, w, h))
							face =rgb_img[ y:y + h,x:x + w]
							        # [top:bottom, left:right]
							face = cv2.resize(face, (200, 200))
							img_bytes = cv2.imencode('.jpeg', face)[1].tobytes()							
							base64_encoded = base64.b64encode(img_bytes)
							add_reco_db(file_id,pickle.dumps(nuevo_descriptor),pickle.dumps(base64_encoded))
							id_db = get_id_db()
							for id in id_db:
								nueva_id_cara = id[0]
							add_face_data(file_id,pickle.dumps(nuevo_descriptor),nueva_id_cara,x, y, w, h)
							print(f"Nueva cara guardada en la base de datos con ID: {nueva_id_cara}")
							
							nuevos_descriptores.pop(0)
							dets.pop(0)
							result = get_face_db()
							break
						


					if result:
						
						descriptores_exist = [(row[0],pickle.loads(row[2])) for row in result]


						for  d,nuevo_descriptor in zip(dets,nuevos_descriptores):
							(x, y, w, h) =  convert_and_trim_bb(rgb_img, d,scale_factor)
							mejor_candidato = None
							mejor_distancia = float('inf')
							for id_cara, face_descriptor_db in descriptores_exist:
								distancia = face_distance([face_descriptor_db], nuevo_descriptor)

								if distancia[0] < mejor_distancia:
									mejor_candidato = id_cara
									mejor_distancia = distancia[0]

							if mejor_candidato is not None and mejor_distancia < 0.5119:
								# Procesa la cara con el mejor candidato encontrado
								print(f"La cara coincide con la base de datos. ID: {mejor_candidato}, Distancia: {mejor_distancia}")
								# Puedes realizar alguna acción con el mejor candidato aquí
								add_face_data(file_id,pickle.dumps(nuevo_descriptor),mejor_candidato,x, y, w, h)
							else:
								
								
								face = rgb_img[ y:y + h,x:x + w]
								        # [top:bottom, left:right]
								face = cv2.resize(face, (200, 200))							
								img_bytes = cv2.imencode('.jpeg', face)[1].tobytes()				
								base64_encoded = base64.b64encode(img_bytes)
								add_reco_db(file_id,pickle.dumps(nuevo_descriptor),pickle.dumps(base64_encoded))
								id_db = get_id_db()
								for id in id_db:
									nueva_id_cara = id[0]
								print(f"La cara parecia con la base de datos. ID: {mejor_candidato}, Distancia: {mejor_distancia}")	
								print(f"Nueva cara guardada en la base de datos con ID: {nueva_id_cara}")
								add_face_data(file_id,pickle.dumps(nuevo_descriptor),nueva_id_cara,x, y, w, h)
								result = get_face_db()
								descriptores_exist = [(row[0],pickle.loads(row[2])) for row in result]
								

							

		next_page_link = data.get('@odata.nextLink')
		if not next_page_link:
				
				break
		graph_api_endpoint = next_page_link

	else:
		print("Error al listar la carpeta:", response_file_info.status_code)
