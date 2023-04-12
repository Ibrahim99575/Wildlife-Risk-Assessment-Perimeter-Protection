# Import required Library
import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
import numpy as np
import tensorflow as tf
import keras
from keras.models import load_model
from tensorflow.keras.preprocessing import image
import time
import datetime
import os
import smtplib as s
from twilio.rest import Client
import pygame
import sys

# Add the path of modules folder to sys.path
sys.path.append('./modules')

# Now import user defined module
import keys

# Initialize pygame for audio play
pygame.init()

# Function to send Normal SMS to the farmer
def sending_sms_farmer():
    client = Client(keys.account_sid, keys.auth_token)

    message = client.messages.create(
        body = "Alert! Your Farm is under the attack of normal animals.",
        from_ = keys.twilio_number,
        to = keys.target_number
        )

# Function to send Danger SMS to the farmer
def sending_sms_farmer_danger():
    client = Client(keys.account_sid, keys.auth_token)

    message = client.messages.create(
        body = "Alert! Your Farm is under the attack of dangerous animals. Please wait and don't go to farm until the forest team come for help",
        from_ = keys.twilio_number,
        to = keys.target_number
        )

# Function to send Forgery SMS to the farmer
def sending_sms_farmer_forgery():
    client = Client(keys.account_sid, keys.auth_token)

    message = client.messages.create(
        body = "Alert! Someone is so close to the camera. There might be security breech. Please look out!!.",
        from_ = keys.twilio_number,
        to = keys.target_number
        )

# Function to send Forgery SMS to the farmer
def sending_sms_farmer_sys_forgery():
    client = Client(keys.account_sid, keys.auth_token)

    message = client.messages.create(
        body = "Alert! Someone has stopped your CCTV Monitoring. There might be security breech. Please look out!!.",
        from_ = keys.twilio_number,
        to = keys.target_number
        )

# Function to send SMS to the forest officer
def sending_sms_forest():
    client = Client(keys.account_sid, keys.auth_token)
    mess = "Alert! There is a wild animal in the area. Please contact the farmer " + str(keys.target_number)
    message = client.messages.create(
        body = mess,
        from_ = keys.twilio_number,
        to = keys.forest_number
        )

# classify frame using classify function
def classify(frame):
    img = cv2.resize(frame, (224, 224))
    #img = cv2.resize(frame, (180, 180))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x, batch_size=32)[0]
    #x = np.expand_dims(img, axis=0)
    #pred = model.predict(x)[0]
    label = classes[np.argmax(pred)]
    confidence = pred[np.argmax(pred)] * 100.0
    
    # draw the label and confidence on the frame
    text = label + ' ({:.1f}%)'.format(confidence)
    return label, confidence

# classify frame using predict_class function
def predict_class(frame):

    # load the image for prediction
    img = cv2.resize(frame, (224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x /= 255.

    # make the prediction
    preds = model.predict(x)
    p = str(preds[0])[1:-5]
    #d_p = float(p)
    if preds[0] > 0.78:
        return "Not Danger", p
    else:
        #d_p = 1 - d_p
        #p = str(d_p)
        return 'Danger', p



# Draw the label and distance of object on the frame
def distan(frame, detector):
    imge, faces = detector.findFaceMesh(frame, draw=False)
    if faces:
        face = faces[0]
        pointLeft = face[145]
        pointRight = face[374]
        w, _ = detector.findDistance(pointLeft, pointRight)
        W = 6.3
        f = 340
        d = (W * f) / w
        return d
    return 0


# load the saved model
model = load_model('models/Functional/my_model_3.h5')

# define the class labels
classes =  ['Danger', 'Not Danger']
# initialize camera
cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

# set the window name and size
window_name = 'Video Classification'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 800, 600)

# Object Detection and recording parameters
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")
detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5
frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
count=1
count1 = 1
count2 = 1
count3 = 0
count4 = 0
flag=0

# Create a directory for saving recorded videos
if not os.path.exists("recording"):
    os.makedirs("recording")
s_time = time.time()
# loop to capture and classify video frames
while True:
    # read frame from camera
    ret, frame = cap.read()
    
    # draw the label and date-time on the frame
    y= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, "TIME:  " + str(y) , (10, 25), cv2.FONT_HERSHEY_PLAIN, 1.3, (0,255,0) , 1)
    
    
    # Object Detection and recording
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = body_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) + len(bodies) > 0:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(os.path.join("recording", f"{current_time}.mp4"), fourcc, 20, frame_size)
            #os.system("ok.mp3")
            pygame.mixer.music.load("audio/ok.mp3")
            pygame.mixer.music.play()
            #sending_mail()
            print("Started Recording!")
            time.sleep(1)
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                count = 1
                count1 = 1
                count2 = 1
                count3 = 0
                count4 = 0
                s_time = time.time()
                timer_started = False
                out.release()
                print('Stop Recording!')
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        
        #string, conf = classify(frame)
        string, pred = predict_class(frame)
        
        dis = distan(frame, detector)
        
        current_time = time.time()
        elapsed_time = current_time - s_time

        if elapsed_time >= 10:
            count3 = 0
            count4 = 0
            s_time = current_time
        print("Danger Count -----> ",count3, " <========> Not Danger Count -----> ", count4)
        
        if(string=="Danger"):
            count3+=1
        elif(string=="Not Danger"):
            count4+=1
        
        if(count3>count4 and count3>=15 and flag==0):
            if(count==1):
                sending_sms_farmer_danger()
                sending_sms_forest()
                count=0
            flag=1
            print("Playing Divert Sound")
            pygame.mixer.music.load("audio/Divert.mp3")
            pygame.mixer.music.play()
        elif(dis<=30 and flag==0):
            if(count2==1):
                sending_sms_farmer_forgery()
                count2 = 0
            pygame.mixer.music.load("audio/CCTV.mp3")
            pygame.mixer.music.play()
            flag=1
        elif(30<dis<=50 and flag==0):
            if(count1==1):
                sending_sms_farmer()
                count1 = 0
            pygame.mixer.music.load("audio/monitored.mp3")
            pygame.mixer.music.play()
            flag=1
        
        if not pygame.mixer.music.get_busy():
            flag = 0
        out.write(frame)

    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
    
    # Call the classify function and find the danger level
    #label, confidence = classify(frame)
    #text1 = label + ' ({:.1f}%)'.format(confidence)
    #cv2.putText(frame, text1, (220, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
    
    # Call the predict_class function and find the danger level
    string, pred = predict_class(frame)
    text1 = string +  " : " + pred + " %"
    cv2.putText(frame, text1, (220, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
    
    
    # Call the distan function and find the distance of the object
    d = distan(frame, detector)
    text2 = 'Distance: ' + str(int(d)) + ' cm'
    cv2.putText(frame, text2, (430, 25), cv2.FONT_HERSHEY_PLAIN, 1.5, (102, 102, 255), 2)
    
    # show frame in the window
    cv2.imshow(window_name, frame)

    # break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        pygame.mixer.music.load("audio/off.mp3")
        pygame.mixer.music.play()
        sending_sms_farmer_sys_forgery()
        out.release()
        time.sleep(6)
        break
    time.sleep(0.01)

# release camera and close windows
pygame.quit()
cap.release()
cv2.destroyAllWindows()