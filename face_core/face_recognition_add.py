import cv2
import json
import numpy as np
import os
from threading import Thread
import time

class VideoCamera(object):

    def __init__(self, cam_num, FRGraph, aligner, extract_features, face_detect, done_img="done.png", name="Your Name", additional_data = dict()):
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

        self.face_center_detected = 0
        self.face_right_detected = 0
        self.face_left_detected = 0

        self.name = name

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

    def save(self):
        if self.saved > 0:
            print(f'self.saved = {self.saved}, skipping save')
            
        f = open('./facerec_128D.txt','r+');
        data_set = json.loads(f.read());

        for pos in self.person_imgs: #there r some exceptions here, but I'll just leave it as this to keep it simple
            self.person_features[pos] = [np.mean(self.extract_feature.get_features(self.person_imgs[pos]),axis=0).tolist()]
        data_set[self.name] = self.person_features;
        f = open('./facerec_128D.txt', 'w+');
        f.write(json.dumps(data_set))

        self.saved += 1
        print(f'Saved! {self.name}')

    def __del__(self):
        print('__del__ called...')

        self.done = True

        self.save()

        self.video.release()
        # super().__del__
    
    def get_frame(self):
        if self.done:
            return None
        if (self.face_right_detected>=self.frame_count_done) and (self.face_left_detected>=self.frame_count_done) and (self.face_center_detected>=self.frame_count_done):
            # print("Done")
            self.done = True
            print('calling __del__ from get_frame...')
            self.__del__()
            return self.done_img

            # ret, jpeg = cv2.imencode('.jpg', self.done_img)
            # return jpeg.tobytes()

        success, image = self.video.read()
        
        rects, landmarks = self.face_detect.detect_face(image, 80);  # min face size is set to 80x80
        for (i, rect) in enumerate(rects):
            aligned_frame, pos = self.aligner.align(160,image,landmarks[i]);

            if pos=="Left":
                self.face_left_detected += 1
            elif pos=="Right":
                self.face_right_detected += 1
            else:
                self.face_center_detected += 1

            print(self.face_left_detected, self.face_center_detected, self.face_right_detected)

            if len(aligned_frame) == 160 and len(aligned_frame[0]) == 160:
                self.person_imgs[pos].append(aligned_frame)
                cv2.rectangle(image,(rect[0],rect[1]),(rect[0] + rect[2],rect[1]+rect[3]),(0,255,0),2) #draw bounding box for the face
                # print("Face captured!")
                # cv2.imshow("Captured face", aligned_frame)
        key = cv2.waitKey(1) & 0xFF

        
        
        # cv2.putText(frame,recog_data[i][0]+" - "+str(recog_data[i][1])+"%",(rect[0],rect[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1,cv2.LINE_AA)

        ret, jpeg = cv2.imencode('.jpg', image)
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
    