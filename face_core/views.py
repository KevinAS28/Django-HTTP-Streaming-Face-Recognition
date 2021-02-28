

from django.shortcuts import render
from django.http import StreamingHttpResponse

#face recogntion
from .align_custom import AlignCustom
from .face_feature import FaceFeature
from .mtcnn_detect import MTCNNDetect
from .tf_graph import FaceRecGraph
from . import camera_auth, camera_add
from threading import Thread

#### Facial Recognition Functions
# ----------------------------------------------------------------------------------------------------#


# #Face recognition module. It will take around 30 seconds to run. 
def load_model():
  print("\n\nLoading face recognition modules...")
  global FRGraph, aligner, extract_feature, face_detect
  FRGraph = FaceRecGraph()
  aligner = AlignCustom()
  extract_feature = FaceFeature(FRGraph)
  face_detect = MTCNNDetect(FRGraph, scale_factor=2)
  print("\n\nDone\n\n")

Thread(target=load_model).start()

def add_face_src(request):
    # print("add_face_src: ", request.session["email"])
    request.session["email"] = "test@mail.com"
    frames = camera_add.generate_frames(request, camera_add.VideoCamera(FRGraph, aligner, extract_feature, face_detect, name=request.session["email"]))
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


def add_face(request):
    return render(request, 'vid_base_add.html')


def auth_face_src(request):
    # print("auth_face_src: ", request.session["email"])
    request.session["email"] = "test@mail.com"
    frames = camera_auth.generate_frames(request, camera_auth.VideoCamera(FRGraph, aligner, extract_feature, face_detect))
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


def auth_face(request):
    return render(request, 'vid_base_auth.html')


