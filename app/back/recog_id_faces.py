from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
from services.pyimagesearch.helpers import convert_and_trim_bb
from imutils import build_montages
import face_recognition
from io import BytesIO
from PIL import Image
import numpy as np
import requests
import imutils
import cv2
import pickle
import base64 
import io
from repository.SQL_query import *

descriptors = []
images = []
faces = []

APP_ID = '69b42475-11c2-4a72-8f2d-54796e1da8f6'
SCOPES = ['Files.Read']
file_ids = '128F10A92846F712%21106'

access_token = generate_access_token(APP_ID, scopes=SCOPES)
headers = {'Authorization': 'Bearer ' + access_token['access_token']}
graph_api_endpoint = GRAPH_API_ENDPOINT + f'/me/drive/items/{file_ids}/children?top=10'

while True:


	response_file_info = requests.get(graph_api_endpoint,headers=headers)
	if response_file_info.status_code == 200:
		data = response_file_info.json()
		for item in data["value"]:
		
			if "file" in item:
				file_name = item["name"]

				file_id = item["id"]
				print(file_id)

	
				file_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
				file_response = requests.get(file_url, headers=headers)
				image_data = file_response.content
				image = Image.open(BytesIO(image_data))
				#image.show()
				# dataimg = io.BytesIO()
				# image.save(dataimg,"JPEG")
				# encode_img_data = base64.b64encode(dataimg.getvalue())

				np_img = np.array(image)
				np_img = imutils.resize(np_img, width=600)
				rgb = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

			
				boxes = face_recognition.face_locations(rgb,number_of_times_to_upsample=1,model="hog")
		
				nuevos_descriptores = face_recognition.face_encodings(rgb,boxes, num_jitters=1,model="large")
				result = get_face_db()
				if not result:
					for  d,face_descriptor in zip(boxes,nuevos_descriptores):
						(top, right, bottom, left) = d	
						face = rgb[top:bottom, left:right]
						face = cv2.resize(face, (96, 96))

						img_bytes = cv2.imencode('.jpeg', face)[1].tobytes()
						# Codifica los bytes en Base64
						base64_encoded = base64.b64encode(img_bytes)

						#faces.append(face)
						add_reco_db(file_id,pickle.dumps(face_descriptor),pickle.dumps(base64_encoded ))
						id_db = get_id_db()
						for id in id_db:
							nueva_id_cara = id[0]
						add_face_data(file_id,pickle.dumps(face_descriptor),nueva_id_cara)
						print(f"Nueva cara guardada en la base de datos con ID: {nueva_id_cara}")


				if result:

					descriptores_exist = [(row[0],pickle.loads(row[2])) for row in result]
				

					for  d,nuevo_descriptor in zip(boxes,nuevos_descriptores):
						nueva_cara_es_unica = True
						nueva_id_cara = None
						for id_cara, face_descriptor_db in descriptores_exist:

							distancia = face_recognition.face_distance([face_descriptor_db], nuevo_descriptor)
							if distancia[0] < 0.55:  # Puedes ajustar el umbral de similitud según tus necesidades
								nueva_cara_es_unica = False
								nueva_id_cara = id_cara
								break

						if nueva_cara_es_unica:
							# Si la cara es única, guárdala en la base de datos
							(top, right, bottom, left) = d	
							face = rgb[top:bottom, left:right]
							face = cv2.resize(face, (96, 96))
							#faces.append(face)

							img_bytes = cv2.imencode('.jpeg', face)[1].tobytes()
							# Codifica los bytes en Base64
							base64_encoded = base64.b64encode(img_bytes)
							
							add_reco_db(file_id,pickle.dumps(nuevo_descriptor),pickle.dumps(base64_encoded))
							id_db = get_id_db()
							for id in id_db:
								nueva_id_cara = id[0]
							add_face_data(file_id,pickle.dumps(nuevo_descriptor),nueva_id_cara)


							print(f"Nueva cara guardada en la base de datos con ID: {nueva_id_cara}")


						else:
							print(f"La cara ya existe en la base de datos con ID: {nueva_id_cara}")
							add_face_data(file_id,pickle.dumps(nuevo_descriptor),nueva_id_cara)
				

				# for  d,face_descriptor in zip(boxes,nuevos_descriptores):
				# 	mi_array_contiguo = np.ascontiguousarray(face_descriptor, dtype=np.float64)
				# 	mi_vector = dlib.vector(mi_array_contiguo)
				# 	descriptors.append(mi_vector)
				# 	images.append((rgb, d))

					

		next_page_link = data.get('@odata.nextLink')
		if not next_page_link:
				
				break
		graph_api_endpoint = next_page_link

	else:
		print("Error al listar la carpeta:", response_file_info.status_code)


# labels = dlib.chinese_whispers_clustering(descriptors, 0.5)
# labelIDs = np.unique(labels)
# numUniqueFaces = len(np.where(labelIDs > -1)[0])
# print("[INFO] # unique faces: {}".format(numUniqueFaces))
# for labelID in labelIDs:
# 	print("[INFO] faces for face ID: {}".format(labelID))
# 	idxs = np.where(labels == labelID)[0]
# 	idxs = np.random.choice(idxs, size=min(25, len(idxs)),replace=False)
#	faces = []
# 	print(idxs)
# 	for i in idxs:	
		# img,rect = images[i]   
		# (top, right, bottom, left) = rect
		# face = img[top:bottom, left:right]
		# face = cv2.resize(face, (96, 96))
		# faces.append(face)	
# photos = get_photo_db()
# for row in photos:
# 	ph = pickle.loads(row[1])
# 	faces.append(ph)
# montage = build_montages(faces, (96, 96), (5, 5))[0]
# #title = "Face ID #{}".format(labelID)
# #title = "Unknown Faces" if labelID == -1 else title
# cv2.imshow("hola", montage)
# cv2.waitKey(0)