import cv2
import os
import sys
import json
import numpy as np

from django.conf import settings

def findPeople(features_arr, positions, face_data, thres = 0.6, percent_thres = 80):
    '''
    :param features_arr: a list of 128d Features of all faces on screen
    :param positions: a list of face position types of all faces on screen
    :param thres: distance threshold
    :return: person name and percentage
    '''
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

class VideoCamera(object):
    def __init__(self, FRGraph, aligner, extract_features, face_detect, percent_thres=80, face_data=os.path.join(settings.BASE_DIR, "facerec_128D.txt"), done_img="done.png"):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        FRGraph = FRGraph
        self.aligner = aligner
        self.extract_feature = extract_features
        self.face_detect = face_detect

        self.person_imgs = {"Left" : [], "Right": [], "Center": []}
        self.person_features = {"Left" : [], "Right": [], "Center": []}
        self.video = cv2.VideoCapture(0)

        # self.names = json.load(open("names.txt"))
        self.face_data = face_data

        self.percent_thres = percent_thres

        self.done_img = open(os.path.join("static", "img", done_img), "rb").read()
        self.done = False

        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):

        _,frame = self.video.read()

        if type(frame)==type(None):
            print("Frame not availble (None)")
            exit()

        # u can certainly add a roi here but for the sake of a demo i'll just leave it as simple as this
        rects, landmarks = self.face_detect.detect_face(frame, 80)#min face size is set to 80x80
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
            recog_data = findPeople(features_arr,positions, face_data=self.face_data, percent_thres=self.percent_thres)
            for (i,rect) in enumerate(rects):
                cv2.rectangle(frame,(rect[0],rect[1]),(rect[0] + rect[2],rect[1]+rect[3]),(0,255,0),2) #draw bounding box for the face
                cv2.putText(frame,recog_data[i][0]+" - "+str(recog_data[i][1])+"%",(rect[0],rect[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,cv2.LINE_AA)
                print(recog_data[i][0], recog_data[i][1])
                # for rollno, name in self.names.items():   
                #     if name == recog_data[i][0]:
                #         for i in range(1):
                #             print(str(recog_data))
                #             return 
                #             # vs.release()
                #             # cv2.destroyAllWindows()
                #             # os.system('python auth1.py')

                #             # vs.release()
                #             # cv2.destroyAllWindows()
                #             # vs.release() # camera release 
                #             # cv2.destroyAllWindows() 
                #     else:
                #         pass 
            
        # cv2.imshow("Capturing Face",frame)
        # key = cv2.waitKey(1) & 0xFF
        # if key == 27 or key == ord("q"):
        #     break


        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


def generate_frames(request, camera):
    while not camera.done:
        frame = camera.get_frame()
        if frame==None:
            break
        
        vid =  (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        yield vid
