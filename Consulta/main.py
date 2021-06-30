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
  def __init__(self, name, confidence, bklink):
    self.Name = name
    self.Confidence = confidence
    self.BucketLink = bklink

  def get_miniature(self):
    cap = cv2.VideoCapture(self.BucketLink)
    retval, image = cap.read()
    retval, buffer = cv2.imencode('.jpg', image)
    mini = base64.b64encode(buffer)
    self.Miniature = "data:image/jpeg;base64," + str(mini)
    
def get_videos(word):
  meta = sqlalchemy.MetaData(bind=None)
  table = sqlalchemy.Table('sis_m_video',meta, autoload=True, autoload_with=db)
  classNames = { 'background': table.c.netq0,
    'aeroplane': table.c.netq1,'plane': table.c.netq1,'avion': table.c.netq1,
    'bicycle': table.c.netq2,'bicicleta': table.c.netq2,
    'bird': table.c.netq3,'ave': table.c.netq3,'pajaro': table.c.netq3,
    'boat': table.c.netq4,'bote': table.c.netq4,
    'bottle': table.c.netq5,'botella': table.c.netq5,
    'bus': table.c.netq6,'autobus': table.c.netq6,
    'car': table.c.netq7,'carro': table.c.netq7,'auto': table.c.netq7,
    'cat': table.c.netq8,'gato': table.c.netq8,
    'chair': table.c.netq9,'silla': table.c.netq9,
    'cow': table.c.netq10,'vaca': table.c.netq10,
    'diningtable': table.c.netq11,'table': table.c.netq11,'mesa': table.c.netq11,'cena': table.c.netq11,
    'dog': table.c.netq12,'perro': table.c.netq12,
    'horse': table.c.netq13,'caballo': table.c.netq13,
    'motorbike': table.c.netq14,'moto': table.c.netq14,'motocicleta': table.c.netq14,
    'person': table.c.netq15,'persona': table.c.netq15,
    'pottedplant': table.c.netq16,'plant': table.c.netq16,'maceta': table.c.netq16,
    'sheep': table.c.netq17,'oveja': table.c.netq17,
    'sofa': table.c.netq18,'sillon': table.c.netq18,
    'train': table.c.netq19,'tren': table.c.netq19,
    'tvmonitor': table.c.netq20,'tv': table.c.netq20,'monitor': table.c.netq20,'pantalla': table.c.netq20,
  }
  stmt = sqlalchemy.select([table]).where(classNames[word] > 0.0)
  videos = []
  try:
    with db.connect() as conn:
      for r in conn.execute(stmt):
        v = Video(r['cnombre'], r[classNames[word]], r['clinkbucket'])
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
