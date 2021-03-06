

from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse

from threading import Thread
from django.views.decorators.csrf import csrf_exempt
import json

#### Facial Recognition Functions
# ----------------------------------------------------------------------------------------------------#

face_scanner = dict()
face_scanner_id = 0

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

def add_face_src(request):
    global face_scanner
    # print("add_face_src: ", request.session["email"])
    print(request.GET)
    code = int(request.GET['code'])

    request.session["email"] = "test@mail.com"
    cam = camera_add.VideoCamera(FRGraph, aligner, extract_feature, face_detect, name=request.session["email"])
    
    face_scanner[code] = cam

    frames = camera_add.generate_frames(request, cam)
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


def add_face(request):
    global face_scanner_id
    code = int(face_scanner_id)
    face_scanner_id += 1
    return render(request, 'faceRecog.html', {'face_code': code})

@csrf_exempt
def check_add_face(request):
    global face_scanner, face_scanner_id

    
    
    data = json.loads(request.body)
    code = int(data['code'])
    print(code)
    try:
        cam = face_scanner[int(code)]
        to_percent = lambda x: str(x*(100/cam.frame_count_done))+"%" if x <= cam.frame_count_done else "100%"
        done = True if ((cam.face_left_detected==cam.frame_count_done) and (cam.face_center_detected==cam.frame_count_done) and (cam.face_right_detected==cam.frame_count_done)) else False
        return JsonResponse({"left": to_percent(cam.face_left_detected), "center": to_percent(cam.face_center_detected), "right": to_percent(cam.face_right_detected), 'done': done})
    except KeyError:
        print(face_scanner)
        return JsonResponse({"left": -1, "center": -1, "right": -1, 'done': False})

def auth_face_src(request):
    # print("auth_face_src: ", request.session["email"])
    request.session["email"] = "test@mail.com"
    frames = camera_auth.generate_frames(request, camera_auth.VideoCamera(FRGraph, aligner, extract_feature, face_detect))
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


def auth_face(request):
    return render(request, 'vid_base_auth.html')


