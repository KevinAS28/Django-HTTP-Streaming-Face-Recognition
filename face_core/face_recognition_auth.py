import cv2
import json
import numpy as np
import os
from threading import Thread
import time
import sys

def findPeople(features_arr, positions, face_data, thres = 0.6, percent_thres = 80):
    f = open(face_data,'r')
    data_set = json.loads(f.read())

    returnRes = []
    for (i,features_128D) in enumerate(features_arr):
        result = "Unknown"
        smallest = sys.maxsize
        for person in data_set.keys():
            person_data = data_set[person][positions[i]]
            for data in person_data:
                distance = np.sqrt(np.sum(np.square(data-features_128D)))
                if(distance < smallest):
                    smallest = distance
                    result = person
        percentage =  min(100, 100 * thres / smallest)
        if percentage <= percent_thres :
            result = "Unknown"
        returnRes.append((result,percentage))
    return returnRes


def compare_face(features_arr0, positions0, face1, name1, thres = 0.6, percent_thres = 80):
    returnRes = []
    for (i,features_128D) in enumerate(features_arr0):
        smallest = sys.maxsize
        person_data = face1[positions0[i]]
        for data in person_data:
            distance = np.sqrt(np.sum(np.square(data-features_128D)))
            if(distance < smallest):
                smallest = distance
        percentage =  min(100, 100 * thres / smallest)
        returnRes.append((name1, percentage))
    return returnRes


class VideoCamera(object):

    def __init__(self, cam_num, FRGraph, aligner, extract_features, face_detect, data_face1, name1='KevinAS28', done_img="done.png", additional_data = dict()):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        FRGraph = FRGraph
        self.aligner = aligner
        self.extract_feature = extract_features
        self.face_detect = face_detect

        self.person_imgs = {"Left" : [], "Right": [], "Center": []};
        self.person_features = {"Left" : [], "Right": [], "Center": []};
        self.cam_num = cam_num
        self.video = cv2.VideoCapture(cam_num)

        self.data_face = data_face1
        self.name1 = name1

        self.done_img = open(os.path.join("static", "img", done_img), "rb").read()
        self.done = False
        
        self.frame_count_done = 20

        self.check = 0
        self.check_before = 0

        self.saved = 0

        Thread(target=self.self_check).start()

        self.additional_data = additional_data
        
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def self_check(self, seconds=5):
        print(f'Self check for camera {self.cam_num} started.')
        while not self.done:
            if self.check_before == self.check:
                print(f'Camera {self.cam_num} not active (check = {self.check})? Wait {seconds} seconds...')
                time.sleep(seconds)
                if self.check_before == self.check:
                    print(f'Not used in {seconds}: Stopping camera {self.cam_num}...')
                    self.done = True
                    print("calling __del__ from self_check...")
                    self.__del__()
                    break
            else:
                self.check_before = self.check
            time.sleep(0.5)


    def __del__(self):
        print('__del__ called...')

        self.done = True
        self.video.release()
        # super().__del__
    
    def get_frame(self):
        if self.done:
            return self.done_img            

        success, frame = self.video.read()
        
        rects, landmarks = self.face_detect.detect_face(frame, 80);  # min face size is set to 80x80
        aligns = []
        positions = []

        for (i, rect) in enumerate(rects):
            aligned_face, face_pos = self.aligner.align(160,frame,landmarks[i])
            if len(aligned_face) == 160 and len(aligned_face[0]) == 160:
                aligns.append(aligned_face)
                positions.append(face_pos)
            else: 
                print("Align face failed") #log        
        
        if(len(aligns) > 0):
            features_arr = self.extract_feature.get_features(aligns)
            recog_data = compare_face(features_arr,positions, face1=self.face1, name1=self.name1, percent_thres=self.percent_thres)
            for (i,rect) in enumerate(rects):
                cv2.rectangle(frame,(rect[0],rect[1]),(rect[0] + rect[2],rect[1]+rect[3]),(0,255,0),2) #draw bounding box for the face
                cv2.putText(frame,recog_data[i][0]+" - "+str(recog_data[i][1])+"%",(rect[0],rect[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,cv2.LINE_AA)
                print(recog_data[i][0], recog_data[i][1])

        
        # cv2.putText(frame,recog_data[i][0]+" - "+str(recog_data[i][1])+"%",(rect[0],rect[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,cv2.LINE_AA)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

def generate_frames(request, camera):
    while True:            
        frame = camera.get_frame()
        if frame==None:
            break
        
        vid =  (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        yield vid

        if camera.done:
            break
    