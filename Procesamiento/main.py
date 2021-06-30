import os
import cv2
import numpy as np
import sqlalchemy

connection_name = "proyecto-final-cloud-318204:us-central1:video-recognition-db"
db_password = "1234"
db_name = "VideoRecognitionDB"
db_user = "root"
driver_name = 'mysql+pymysql'
query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})

yt_base= "https://www.youtube.com/watch?v="

prototxt= 'MobileNetSSD_deploy.prototxt.txt'
weights = 'MobileNetSSD_deploy.caffemodel'

net = cv2.dnn.readNetFromCaffe(prototxt, weights)

def write(videoname,labels, videolink):
  db = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(drivername=driver_name,
                                                          username=db_user,
                                                          password=db_password,
                                                          database=db_name,
                                                          query=query_string,),
                                pool_size=5,
                                max_overflow=2,
                                pool_timeout=30,
                                pool_recycle=1800)
  
  meta = sqlalchemy.MetaData(bind=None)
  try:
    table = sqlalchemy.Table('sis_m_video', meta, autoload=True, autoload_with=db)
    print('using sis_m_video table')
  except Exception as e:
    print('Error: {}'.format(str(e)))
    return
  
  stmt = (
    sqlalchemy.insert(table).
    values(cnombre=videoname, clinkbucket=videolink,
           netq0=float(labels[0]), netq1=float(labels[1]), netq2=float(labels[2]),netq3=float(labels[3]),
           netq4=float(labels[4]), netq5=float(labels[5]), netq6=float(labels[6]), netq7=float(labels[7]),
           netq8=float(labels[8]), netq9=float(labels[9]), netq10=float(labels[10]), netq11=float(labels[11]),
           netq12=float(labels[12]), netq13=float(labels[13]), netq14=float(labels[14]), netq15=float(labels[15]),
           netq16=float(labels[16]), netq17=float(labels[17]), netq18=float(labels[18]), netq19=float(labels[19]), netq20=float(labels[20]))
  )
  
  try:
    with db.connect() as conn:
      conn.execute(stmt)
    return True
  except Exception as e:
    print('Error: {}'.format(str(e)))
    return False

def get_labels(video, nclasess=21):
  classes_val= [0.0] * nclasess
  classes_cont= [0] * nclasess
  
  ret, frame = video.read()
  while(ret):
    frame = cv2.resize(frame, (300,300))
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
    net.setInput(blob)
    detections = net.forward()
    for i in range(detections.shape[2]):
      confidence = detections[0,0,i,2]
      if confidence > 0.25:
        clas = int(detections[0,0,i,1])
        classes_val[clas]+= confidence
        classes_cont[clas]+= 1
    ret, frame = video.read()
  classes = []
  for v, c in zip(classes_val, classes_cont):
    if c == 0:
      classes.append(0.0)
    else:
      classes.append(v/float(c))
  return classes

def start(event, context):
  """Triggered by a change to a Cloud Storage bucket.
  Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
  """
  file = event

  video_url = "https://storage.googleapis.com/{}/{}".format(file['bucket'], file['name'])

  videocap = cv2.VideoCapture(video_url)

  if videocap.isOpened():
    print ("File Can be Opened")
    vname = file['name'][:-4]
    labels = get_labels(videocap)
    print("video processed")
    saved = write(vname, labels, video_url)
    if saved:
      print("video saved")
  else:
    print("Not Working")