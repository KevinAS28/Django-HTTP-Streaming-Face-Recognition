import time

from django.shortcuts import render, HttpResponse, redirect, reverse
from django.contrib.auth.models import User, auth, Group
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.template import loader, Context


from .models import PatientProfile
from .models import PatientProfile, Document, TreatmentsandMedicines, Allergies, Lifestyle, HealthConditions
from .forms import PatientCreation, SignUpForm

#face recogntion
from align_custom import AlignCustom
from face_feature import FaceFeature
from mtcnn_detect import MTCNNDetect
from tf_graph import FaceRecGraph
import camera_auth, face_recognition_add


#### Facial Recognition Functions
# ----------------------------------------------------------------------------------------------------#


# #Face recognition module. It will take around 30 seconds to run. 
print("\n\nLoading face recognition modules...")
FRGraph = FaceRecGraph()
aligner = AlignCustom()
extract_feature = FaceFeature(FRGraph)
face_detect = MTCNNDetect(FRGraph, scale_factor=2)
print("Done\n\n")

def gen(request, camera):
    while not camera.done:
        frame = camera.get_frame()
        if frame==None:
            break
        
        vid =  (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        yield vid


    # request.session['test'] = 'YAY'
    # return redirect()

def tester(request):
    # return render(request, 'vid_base_add.html', {'test': request.session['email']})
    def gen1():
          t = loader.get_template('test.html')
          for i in range(100):
            time.sleep(1)
            yield t.render({'test': '<h1>{}</h1>'.format(str(i))})
            
    return StreamingHttpResponse(gen1())
    

def add_face_src(request):
    # print("add_face_src: ", request.session["email"])
    request.session["email"] = "test@mail.com"
    frames = gen(request, face_recognition_add.VideoCamera(FRGraph, aligner, extract_feature, face_detect, name=request.session["email"]))
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


def add_face(request):
    return render(request, 'vid_base_add.html')



#### all the account processes
# ----------------------------------------------------------------------------------------------------#
# Patients Account access

# Todo
@login_required
def alertContacts(request):
  return render(request, 'patient/alert_contacts.html')

def signup(request):
  form = SignUpForm()
  form1 = UserCreationForm()
  form2 = PatientCreation()
  if request.POST:
    # form = SignUpForm(request.POST)
    # form1 = UserCreationForm(request.POST)
    # form2 = PatientCreation(request.POST, request.FILES)
    # if form.is_valid() and form1.is_valid() and form2.is_valid():
    #   user = form1.save(commit=False)
    #   user.first_name = form.cleaned_data['first_name']
    #   user.last_name = form.cleaned_data['last_name']
    #   user.email = form.cleaned_data['email']
    #   user.save()

    #   patient_group = Group.objects.get(name='Patient')
    #   patient = form2.save(commit=False)
    #   patient.user = user
    #   patient.save()
    #   patient_group.user_set.add(user)
    #   loggedIn = authenticate(username=form1.cleaned_data['username'], password=form1.cleaned_data['password1'])
    #   login(request, loggedIn)
      # return redirect('/')

      request.session["email"] = "test@mail.com"#form.cleaned_data['email']
      return render(request, 'vid_base_add.html', )

  return render(
    request,
    'account/signup.html',
    {'form': form, 'form1': form1, 'form2': form2}
  )

def documents(request):
    patient_id = request.POST.get('patient_id')
    patient = PatientProfile.objects.get(id = patient_id)
    all_docs = Document.objects.filter(patient = patient)
    return render(request, "prescriptions/documents.html", all_docs)

# our services
def services(request):
    # about us page of the application
    return render(request,'patient/our_services.html')


# ----------------------------------------------------------------------------------------------------#
# Patients Health Records

# format records
def TreatmentsandMedicinesToString(patient):
  objs = Lifestyle.objects.filter(patient=patient)
  output = []
  for obj in objs:
    output.append("%s: %s" % (obj.medicine, obj.description))

  if output == []:
    return "None"
  return "\n".join(output)

def HealthConditionsToString(patient):
  objs = HealthConditions.objects.filter(patient=patient)
  output = []
  for obj in objs:
    output.append(obj.name)

  if output == []:
    return "None"
  return "\n".join(output)

def AllergiesToString(patient):
  objs = Allergies.objects.filter(patient=patient)
  output = []
  for obj in objs:
    output.append(obj.name)

  if output == []:
    return "None"
  return "\n".join(output)

def LifestyleToString(patient):
  objs = Lifestyle.objects.filter(patient=patient)
  output = []
  for obj in objs:
    output.append("%s: %s" % (obj.activity, obj.amount))

  if output == []:
    return "Unknown"
  return "\n".join(output)

@login_required
def getPatient(request):
  user = request.user
  patient = PatientProfile.objects.get(user=user)
  return patient

@login_required
def healthRecord(request, page_section=0):
  patient = getPatient(request)
  patient_id = patient.id
  user = patient.user

  patient_name = "%s %s" % (user.first_name, user.last_name)
  patient_photo = "/static/img/avatar.png"
  main_display = [
    {'title': 'Date of birth', 'value': patient.date_of_birth},
    {'title': 'Sex', 'value': patient.sex},
    {'title': 'Pronouns', 'value': patient.pronouns},
    {'title': 'Race', 'value': patient.race},
    {'title': 'Phone number', 'value': patient.phone_number},
    {'title': 'Email', 'value': user.email},
    {'title': 'Address', 'value': "%s, %s, %s, %s, %s" % (patient.addressline1, patient.addressline2, patient.city, patient.country, patient.zipcode)},
  ]


  subtitles = [
    {'title': 'Treatments and medicines', 'content': HealthConditionsToString(patient), 'active': page_section==0, 'page_section':0},
    {'title': 'Health conditions', 'content': HealthConditionsToString(patient), 'active': page_section==1, 'page_section':1},
    {'title': 'Allergies', 'content': AllergiesToString(patient), 'active': page_section==2, 'page_section':2},
    {'title': 'Lifestyle', 'content': LifestyleToString(patient), 'active': page_section==3, 'page_section':3}
  ]

  try:
    int(request.path.split('/')[-1])
    url_path = "/".join(request.path.split('/')[:-1])
  except ValueError:
    url_path = request.path

  return render(
    request, 
    'patient/profile_list.html',
    {
      'title': "Your health record",
      "id": patient_id,
      "patient_name": patient_name,
      'profile_photo': patient_photo,
      "main_display": main_display,
      'subtitles': subtitles,
      "url_path": url_path,
    }
  )

@login_required
def emergency(request, page_section=0):
  patient = getPatient(request)
  patient_id = patient.id
  user = patient.user

  patient_name = "%s %s" % (user.first_name, user.last_name)
  patient_photo = "/static/img/avatar.png"
  main_display = "Don't let me die. Very broken bones. Handle with care. Do not ship internationally."

  subtitles = [
    {'title': 'Emergency Contact', 'content': "list of contact", 'active': page_section==0, 'page_section':0},
    {'title': 'Health condition details', 'content': HealthConditionsToString(patient), 'active': page_section==1, 'page_section':1},
    {'title': 'Allergies', 'content': AllergiesToString(patient), 'active': page_section==2, 'page_section':2},
  ]

  flags = []
  for obj in Allergies.objects.filter(patient=patient):
    flags.append(obj.name)
  for obj in HealthConditions.objects.filter(patient=patient):
    flags.append(obj.name)

  try:
    int(request.path.split('/')[-1])
    url_path = "/".join(request.path.split('/')[:-1])
  except ValueError:
    url_path = request.path

  return render(
    request, 
    'patient/profile_string.html',
    {
      'title': "Emergency details",
      "id": patient_id,
      "patient_name": patient_name,
      'profile_photo': patient_photo,
      "main_display": main_display,
      'subtitles': subtitles,
      "url_path": url_path,
      "flags": flags
    }
  )

  return render(
    request, 
    'patient/profile_string.html',
    {
      'title': "Your health record",
      "id": patient_id,
      "patient_name": patient_name,
      'profile_photo': patient_photo,
      "content": content
    }
  )

#patient files example
@login_required
def files(request):
  records = [
    {
      "name": "Test.jpg",
      "description": "A test image file.",
      "qr": "qr.jpg",
      "authorisedBy": "Dr Clever",
      "date": "13/02/2021"
    }
  ]
  return render(request,'patient/files.html', {"title": "Example", "records": records})

@login_required
def prescriptions(request):
    return render(request,'patient/files.html')

@login_required
def tests(request):
    return render(request,'patient/files.html')

@login_required
def otherFiles(request):
    return render(request,'patient/files.html')

