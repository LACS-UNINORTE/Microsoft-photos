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
from scipy.spatial.distance import euclidean

descriptors = []
images = []
faces = []

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
    """
    Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
    for each comparison face. The distance tells you how similar the faces are.

    :param face_encodings: List of face encodings to compare
    :param face_to_compare: A face encoding to compare against
    :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
    """
    if len(face_encodings) == 0:
        return np.empty((0))

    return np.linalg.norm(face_encodings - face_to_compare, axis=1)

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

					descriptors = []			
					file_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
					file_response = requests.get(file_url, headers=headers)
					image_data = file_response.content
					image = Image.open(BytesIO(image_data))
					np_img = np.array(image)
					np_img = imutils.resize(np_img, width=600)
					rgb = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
					dets = detector(rgb, 1)
					print("Number of faces detected: {}".format(len(dets)))
					for k, d in enumerate(dets):
						shape = sp(rgb, d)
						face_descriptor = np.array(facerec.compute_face_descriptor(rgb, shape))						
						descriptors.append(face_descriptor)
						

			
					nuevos_descriptores = descriptors
					result = get_face_db()
					if not result:
						for  d,nuevo_descriptor in zip(dets,nuevos_descriptores):

							(x, y, w, h) =  convert_and_trim_bb(rgb, d)
							face = rgb[ y:y + h,x:x + w]
							face = cv2.resize(face, (200, 200))
							img_bytes = cv2.imencode('.jpeg', face)[1].tobytes()							
							base64_encoded = base64.b64encode(img_bytes)
							add_reco_db(file_id,pickle.dumps(nuevo_descriptor),pickle.dumps(base64_encoded))
							id_db = get_id_db()
							for id in id_db:
								nueva_id_cara = id[0]
							add_face_data(file_id,pickle.dumps(nuevo_descriptor),nueva_id_cara)
							print(f"Nueva cara guardada en la base de datos con ID: {nueva_id_cara}")
							
							nuevos_descriptores.pop(0)
							dets.pop(0)
							result = get_face_db()
							break
						


					if result:
						
						descriptores_exist = [(row[0],pickle.loads(row[2])) for row in result]


						for  d,nuevo_descriptor in zip(dets,nuevos_descriptores):
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
								add_face_data(file_id,pickle.dumps(nuevo_descriptor),mejor_candidato)
							else:
								
								(x, y, w, h) =  convert_and_trim_bb(rgb, d)
								face = rgb[ y:y + h,x:x + w]
								face = cv2.resize(face, (200, 200))							
								img_bytes = cv2.imencode('.jpeg', face)[1].tobytes()				
								base64_encoded = base64.b64encode(img_bytes)
								
								add_reco_db(file_id,pickle.dumps(nuevo_descriptor),pickle.dumps(base64_encoded))
								id_db = get_id_db()
								for id in id_db:
									nueva_id_cara = id[0]
								print(f"La cara parecia con la base de datos. ID: {mejor_candidato}, Distancia: {mejor_distancia}")	
								print(f"Nueva cara guardada en la base de datos con ID: {nueva_id_cara}")
								add_face_data(file_id,pickle.dumps(nuevo_descriptor),nueva_id_cara)
								result = get_face_db()
								descriptores_exist = [(row[0],pickle.loads(row[2])) for row in result]
								#result = get_face_db()
								#descriptores_exist = [(row[0],pickle.loads(row[2])) for row in result]

							

		next_page_link = data.get('@odata.nextLink')
		if not next_page_link:
				
				break
		graph_api_endpoint = next_page_link

	else:
		print("Error al listar la carpeta:", response_file_info.status_code)
