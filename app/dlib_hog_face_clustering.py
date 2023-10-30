from pyimagesearch.helpers import convert_and_trim_bb
import sys
import os
import dlib
import glob
import cv2
import imutils
import numpy as np
from imutils import build_montages

if len(sys.argv) != 4:
    print(
        "Call this program like this:\n"
        "   ./face_clustering.py shape_predictor_5_face_landmarks.dat dlib_face_recognition_resnet_model_v1.dat ../examples/faces output_folder\n"
        "You can download a trained facial shape predictor and recognition model from:\n"
        "    http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2\n"
        "    http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2")
    exit()

predictor_path = sys.argv[1]
face_rec_model_path = sys.argv[2]
faces_folder_path = sys.argv[3]
#output_folder_path = sys.argv[4]

# Load all the models we need: a detector to find the faces, a shape predictor
# to find face landmarks so we can precisely localize the face, and finally the
# face recognition model.
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

descriptors = []
images = []

# Now find all the faces and compute 128D face descriptors for each face.
for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
    print("Processing file: {}".format(f))
    #img = dlib.load_rgb_image(f)
    image = cv2.imread(f)
    image = imutils.resize(image, width=600)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)    
    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = detector(rgb, 1)
    print("Number of faces detected: {}".format(len(dets)))

    # Now process each face we found.
    for k, d in enumerate(dets):
        # Get the landmarks/parts for the face in box d.
        shape = sp(rgb, d)

        # Compute the 128D vector that describes the face in img identified by
        # shape.  
        face_descriptor = facerec.compute_face_descriptor(rgb, shape)
       
        descriptors.append(face_descriptor)
        images.append((image, d))

# Now let's cluster the faces.  

labels = dlib.chinese_whispers_clustering(descriptors, 0.5)
num_classes = len(set(labels))
print("Number of clusters: {}".format(num_classes))

print(labels)

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
        
    #  python dlib_hog_face_clustering.py shape_predictor_68_face_landmarks.dat dlib_face_recognition_resnet_model_v1.dat dataset2
    

