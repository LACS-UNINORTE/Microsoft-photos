from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
from pyimagesearch.helpers import convert_and_trim_bb
from imutils import build_montages
from io import BytesIO
from PIL import Image
import numpy as np
import requests
import imutils
import dlib
import sys
import cv2
import os


if len(sys.argv) != 3:
    print(
        "Call this program like this:\n"
        "   ./face_clustering.py shape_predictor_5_face_landmarks.dat dlib_face_recognition_resnet_model_v1.dat ../examples/faces output_folder\n"
        "You can download a trained facial shape predictor and recognition model from:\n"
        "    http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2\n"
        "    http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2")
    exit()

predictor_path = sys.argv[1]
face_rec_model_path = sys.argv[2]


# Load all the models we need: a detector to find the faces, a shape predictor
# to find face landmarks so we can precisely localize the face, and finally the
# face recognition model.
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

descriptors = []
images = []

APP_ID = '69b42475-11c2-4a72-8f2d-54796e1da8f6'
SCOPES = ['Files.Read']
save_location = os.getcwd()


file_ids = '128F10A92846F712%21106'

access_token = generate_access_token(APP_ID, scopes=SCOPES)
headers = {
	'Authorization': 'Bearer ' + access_token['access_token']
}
graph_api_endpoint = GRAPH_API_ENDPOINT + f'/me/drive/items/{file_ids}/children?top=10'

# Step 1. get the file name
while True:
	response_file_info = requests.get(graph_api_endpoint,headers=headers)
	#response_file_info = requests.get(GRAPH_API_ENDPOINT + f'/me/drive/items/{file_id}/children',headers=headers,params={'select':'name,id'})
	file_name = response_file_info.json()
	print(file_name)

	if response_file_info.status_code == 200:
		data = response_file_info.json()
		for item in data["value"]:
			# Verifica si el elemento es un archivo.
			if "file" in item:
				file_name = item["name"]
				file_id = item["id"]

			# Descarga el archivo individualmente.
				file_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
				file_response = requests.get(file_url, headers=headers)

				image_data = file_response.content
				image = Image.open(BytesIO(image_data))
				np_img = np.array(image)
				np_img = imutils.resize(np_img, width=600)
				rgb = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
				dets = detector(rgb, 1)
				print("Number of faces detected: {}".format(len(dets)))

				# Now process each face we found.
				for k, d in enumerate(dets):
					# Get the landmarks/parts for the face in box d.
					shape = sp(rgb, d)

					# Compute the 128D vector that describes the face in img identified by
					# shape.  
					face_descriptor = facerec.compute_face_descriptor(rgb, shape)
					print(face_descriptor)
					descriptors.append(face_descriptor)
					images.append((rgb, d))

		next_page_link = data.get('@odata.nextLink')
		if not next_page_link:
				
				break
		graph_api_endpoint = next_page_link

	else:
		print("Error al listar la carpeta:", response_file_info.status_code)



labels = dlib.chinese_whispers_clustering(descriptors, 0.5)
#num_classes = len(set(labels))
#print("Number of clusters: {}".format(num_classes))
labelIDs = np.unique(labels)
numUniqueFaces = len(np.where(labelIDs > -1)[0])
print("[INFO] # unique faces: {}".format(numUniqueFaces))

for labelID in labelIDs:
# find all indexes into the `data` array that belong to the
# current label ID, then randomly sample a maximum of 25 indexes
# from the set
	print("[INFO] faces for face ID: {}".format(labelID))
	idxs = np.where(labels == labelID)[0]
	idxs = np.random.choice(idxs, size=min(25, len(idxs)),replace=False)
	# initialize the list of faces to include in the montage
	faces = []
	print(idxs)
		# loop over the sampled indexes
	for i in idxs:
		# load the input image and extract the face ROI
		img,rect = images[i]   
		(x, y, w, h) =  convert_and_trim_bb(img, rect)
		face = img[ y:y + h,x:x + w]
			# [top:bottom, left:right]
		# force resize the face ROI to 96x96 and then add it to the
		# faces montage list
	
		face = cv2.resize(face, (96, 96))
		faces.append(face)
		
			# create a montage using 96x96 "tiles" with 5 rows and 5 columns
	montage = build_montages(faces, (96, 96), (5, 5))[0]
	
	# show the output montage
	title = "Face ID #{}".format(labelID)
	title = "Unknown Faces" if labelID == -1 else title
	cv2.imshow(title, montage)
	cv2.waitKey(0)
		
                              
 


    


