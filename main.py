import os
# import datetime
# from google.cloud import storage
import cv2
import numpy as np
#import sqlalchemy

connection_name = "clouducsp:us-central1:taggedmedia"
db_password = "root"
db_name = "clouducsp"
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
    table = sqlalchemy.Table('videos', meta, autoload=True, autoload_with=db)
    print('using videos table')
  except Exception as e:
    print('Error: {}'.format(str(e)))
    return
  
  stmt = (
    sqlalchemy.insert(table).
    values(videoName=videoname, youtubeLink=yt_base+videoname, bucketLink=videolink,
           LB00=float(labels[0]), LB01=float(labels[1]), LB02=float(labels[2]),LB03=float(labels[3]),
           LB04=float(labels[4]), LB05=float(labels[5]), LB06=float(labels[6]), LB07=float(labels[7]),
           LB08=float(labels[8]), LB09=float(labels[9]), LB10=float(labels[10]), LB11=float(labels[11]),
           LB12=float(labels[12]), LB13=float(labels[13]), LB14=float(labels[14]), LB15=float(labels[15]),
           LB16=float(labels[16]), LB17=float(labels[17]), LB18=float(labels[18]), LB19=float(labels[19]), LB20=float(labels[20]))
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
      if confidence < 0.25:
        continue
      clas = int(detections[0,0,i,1])
      classes_val[clas]+= confidence
      classes_cont[clas]+= 1
    ret, frame = video.read()
  classes = []
  for v, c in zip(classes_val, classes_cont):
    if c == 0:
      classes.append(0.0)
      continue
    classes.append(v/float(c))
  return classes

def start():
  """Triggered by a change to a Cloud Storage bucket.
  Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
  """

  video_url = "https://storage.googleapis.com/{}/{}".format(file['bucket'], file['name'])

  videocap = cv2.VideoCapture(video_url)

  if videocap.isOpened():
    print ("File Can be Opened")
    vname = video_url[:-4]
    labels = get_labels(videocap)
    print(labels)
    print("video processed")
    saved = write(vname, labels, video_url)
    if saved:
      print("video saved")
  else:
    print("Not Working")


start()