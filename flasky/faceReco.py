from imutils import paths
import imutils
import face_recognition
import argparse
import pickle
import cv2
import os


def recognize_face(image):
    with open("dataset.pickle", "rb") as reader:
        data = pickle.load(reader)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # detect the (x, y)-coordinates of the bounding boxes corresponding
    # to each face in the input image, then compute the facial embeddings
    # for each face
    # rgb = imutils.resize(image, width=750)
    # r = image.shape[1] / float(rgb.shape[1])
    # cv2.imshow("wino", rgb)
    # cv2.waitKey()

    print("[INFO] recognizing faces...")
    boxes = face_recognition.face_locations(rgb,
      model="cnn")
    encodings = face_recognition.face_encodings(rgb, boxes)
    print("passed 1")
    # if len(encodings) == 0:
    #   print("provide another picture")
    # initialize the list of names for each face detected
    names = []

    for encoding in encodings:
      matches = face_recognition.compare_faces(data["encodings"],encoding)
      name = "unknown"
      if True in matches:
        matchedIdxs = [i for (i,b) in enumerate(matches) if b]
        counts = {}
        for i in matchedIdxs:
          name = data["names"][i]
          counts[name] = counts.get(name,0) + 1
        name = max(counts, key = counts.get)

      names.append(name)
      return names[0]