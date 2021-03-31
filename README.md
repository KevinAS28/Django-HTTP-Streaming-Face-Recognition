### Installation

1. Download the model from [Here](https://drive.google.com/drive/folders/1CjdUnkLceXmPYxgmmDH_og0wrbi1c2il)

2. Inside this project directory, create a new directory called "models"

3. extract the content of "models.zip" to "models"

4. The final result should be like this
   ```sh
    kevin@kevinas28:~/Django-HTTP-Streaming-Face-Recognition$ ls
    bixpricing  face_core_config.ini     manage.py  __pycache__  staticfiles
    db.sqlite3  facerec_128D.txt         models     static       templates
    face_core   face_recognition_stream  patients   static1      url
    kevin@kevinas28:~/Django-HTTP-Streaming-Face-Recognition$ ls models
    det1.npy  __MACOSX                                               models.zip
    det2.npy  model-20170512-110547.ckpt-250000.data-00000-of-00001
    det3.npy  model-20170512-110547.ckpt-250000.index

   ```
5. Install the requirements
   ```sh
    python -m pip install -r requirements.txt
   ```

6. Run the project
   ```sh
    python manage.py runserver 0.0.0.0:8080
   ```