from flask import Flask#, request #import main Flask class and request object
from flask import render_template as render
import sqlalchemy
import cv2
import numpy as np
import base64

connection_name = "proyecto-final-cloud-318204:us-central1:video-recognition-db"
db_password = "1234"
db_name = "VideoRecognitionDB"
db_user = "root"
driver_name = 'mysql+pymysql'
query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})

db = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(drivername=driver_name,
                                                          username=db_user,
                                                          password=db_password,
                                                          database=db_name,
                                                          query=query_string,),
                                pool_size=5,
                                max_overflow=2,
                                pool_timeout=30,
                                pool_recycle=1800)


class Video:
  def __init__(self, name, confidence, ytlink, bklink):
    self.Name = name
    self.Confidence = confidence
    self.YtLink = ytlink
    self.BucketLink = bklink
  def get_miniature(self):
    cap = cv2.VideoCapture(self.BucketLink)
    retval, image = cap.read()
    retval, buffer = cv2.imencode('.jpg', image)
    mini = base64.b64encode(buffer)
    self.Miniature = "data:image/jpeg;base64," + mini
    
def get_videos(word):
  meta = sqlalchemy.MetaData(bind=None)
  table = sqlalchemy.Table('entries',meta, autoload=True, autoload_with=db)
  classNames = { 'background': table.c.LB00,
    'aeroplane': table.c.LB01,'plane': table.c.LB01,'avion': table.c.LB01,
    'bicycle': table.c.LB02,'bicicleta': table.c.LB02,
    'bird': table.c.LB03,'ave': table.c.LB03,'pajaro': table.c.LB03,
    'boat': table.c.LB04,'bote': table.c.LB04,
    'bottle': table.c.LB05,'botella': table.c.LB05,
    'bus': table.c.LB06,'autobus': table.c.LB06,
    'car': table.c.LB07,'carro': table.c.LB07,'auto': table.c.LB07,
    'cat': table.c.LB08,'gato': table.c.LB08,
    'chair': table.c.LB09,'silla': table.c.LB09,
    'cow': table.c.LB10,'vaca': table.c.LB10,
    'diningtable': table.c.LB11,'table': table.c.LB11,'mesa': table.c.LB11,'cena': table.c.LB11,
    'dog': table.c.LB12,'perro': table.c.LB12,
    'horse': table.c.LB13,'caballo': table.c.LB13,
    'motorbike': table.c.LB14,'moto': table.c.LB14,'motocicleta': table.c.LB14,
    'person': table.c.LB15,'persona': table.c.LB15,
    'pottedplant': table.c.LB16,'plant': table.c.LB16,'maceta': table.c.LB16,
    'sheep': table.c.LB17,'oveja': table.c.LB17,
    'sofa': table.c.LB18,'sillon': table.c.LB18,
    'train': table.c.LB19,'tren': table.c.LB19,
    'tvmonitor': table.c.LB20,'tv': table.c.LB20,'monitor': table.c.LB20,'pantalla': table.c.LB20,
  }
  stmt = sqlalchemy.select([table]).where(classNames[word] > 0.0)
  videos = []
  try:
    with db.connect() as conn:
      for r in conn.execute(stmt):
        v = Video(r['videoName'], r[classNames[word]], r['youtubeLink'], r['bucketLink'])
        v.get_miniature()
        videos.append(v)
  except Exception as e:
    print('Error: {}'.format(str(e)))
  
  return videos

def search(request):
  if request.method == 'POST':
    word = request.form.get('keyword')
    videos = get_videos(word)
    return render('result.html', word=word, videos=videos)

  return render('index.html')
