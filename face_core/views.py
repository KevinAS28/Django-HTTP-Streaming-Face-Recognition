

from django.http.response import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote, unquote

from threading import Thread
import json
import cv2
import traceback
import json

#### Facial Recognition Functions
# ----------------------------------------------------------------------------------------------------#

token_id = 0
token_id_done = []
camera_avail = []
camera_used = dict()

# #Face recognition module. It will take around 30 seconds to run. 
def load_model():
  print("\n\nLoading face recognition modules...")
  from .align_custom import AlignCustom
  from .face_feature import FaceFeature
  from .mtcnn_detect import MTCNNDetect
  from .tf_graph import FaceRecGraph
  from . import camera_auth, camera_add

  global FRGraph, aligner, extract_feature, face_detect, camera_add, camera_auth
  FRGraph = FaceRecGraph()
  aligner = AlignCustom()
  extract_feature = FaceFeature(FRGraph)
  face_detect = MTCNNDetect(FRGraph, scale_factor=2)
  print("\n\nDone\n\n")

Thread(target=load_model).start()

def detect_camera(seconds=1):
    global camera_avail
    def __detect():
        global camera_avail
        for i in range(10):
            if (cv2.VideoCapture(i).read()[0]):
                camera_avail.append(i)
        # camera_avail = camera_avail[::-1]
        camera_avail = [0]
        
    __detect()
    print('List camera availble: ', camera_avail)
    # while True:
    #     __detect()
    #     time.sleep(seconds)

# def camera_checkers(seconds=1):
#     global camera_avail, camera_used
#     while True:
#         for id in camera_used:
#             if camera_used[id].done:
#                 print(f'Camera {id} is done, moving to availble list')
#                 try:
#                     del camera_used[id]
#                     camera_avail.append(id)
#                 except:
#                     traceback.print_exc()
#         time.sleep(1)


Thread(target=detect_camera).start()
# Thread(target=camera_checkers).start()

def add_face_src(request):
    global camera_used
    # print("add_face_src: ", request.session["email"])
    print(request.GET)
    code = int(request.GET['code'])

    if code==-1:
        print("No Camera Availble")
        return JsonResponse({'error': 'No Camera Availble'})

    request.session["email"] = "test@mail.com"

    cam = camera_used[code]
    
    frames = camera_add.generate_frames(request, cam)
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')

def add_face_success(request):
    if (request.method=='GET'):    
        
        
        return redirect(reverse(redirect_url, permanent=True))


def add_face(request):
    if (request.method=='GET'):
        global camera_avail, camera_used, token_id

        the_token = int(token_id)
        token_id += 1
        
        params = dict()
        success_url = '/face_core/add_face'

        try:
            params = json.loads(unquote(request.GET['params']))
            if ('success_url' in params):
                success_url = params['success_url']            
        except Exception as e:
            print(e)
            
        user_id = 'KevinAS28'

        if len(camera_avail)>0:
            camera_id = int(camera_avail[-1])

            try:
                camera_used[camera_id] = camera_add.VideoCamera(camera_id, FRGraph, aligner, extract_feature, face_detect, name=user_id)
                del camera_avail[-1]
            except NameError:
                return HttpResponseBadRequest('Face recognition module not ready yet, please wait some moment')

            return render(request, 'faceRecog.html', {'face_code': camera_id, 'token_id': the_token, 'success_url': success_url, 'params': quote(json.dumps(params))})
        else:
            # return render(request, 'faceRecog.html', {'face_code': -1})
            return HttpResponseBadRequest('No Camera Availble')
    else:
        return HttpResponseBadRequest('Wrong method')

@csrf_exempt
def check_add_face(request):
    global camera_avail, camera_used, token_id_done

    data = {}
    try:
        data = json.loads(request.body)
    except:
        print('request body:', request.body)
        traceback.print_exc()

    code = int(data['code'])
    # print(code)
    try:
        cam = camera_used[int(code)]
        cam.check += 1
        to_percent = lambda x: str(x*(100/cam.frame_count_done))+"%" if x <= cam.frame_count_done else "100%"
        done = True if ((int(cam.face_left_detected)==cam.frame_count_done) and (cam.face_center_detected==cam.frame_count_done) and (cam.face_right_detected==cam.frame_count_done)) else False
        done = True if cam.done==True else done
        json_data = {"left": to_percent(cam.face_left_detected), "center": to_percent(cam.face_center_detected), "right": to_percent(cam.face_right_detected), 'done': done}
        if done:
            print(f'Camera {code} done, moving to availble list...')
            try:
                del camera_used[code]
                camera_avail.append(code)   
                token_id_done.append(int(data['token_id']))
            except:
                traceback.print_exc()

        return JsonResponse(json_data)
    except KeyError:
        try:
            if (int(data['token_id']) in token_id_done):
                return JsonResponse({'left': '100%', 'center': '100%', 'right': '100%', 'done': True})
            raise Exception("Hummm..?")

        except KeyError:
            print('check_add_face ERROR 0:', camera_used)
            return JsonResponse({"left": -1, "center": -1, "right": -1, 'done': 'fail'})

def auth_face_src(request):
    # print("auth_face_src: ", request.session["email"])
    request.session["email"] = "test@mail.com"
    frames = camera_auth.generate_frames(request, camera_auth.VideoCamera(FRGraph, aligner, extract_feature, face_detect))
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


def auth_face(request):
    return render(request, 'vid_base_auth.html')


