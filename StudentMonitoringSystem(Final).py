{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "pygame 2.0.1 (SDL 2.0.14, Python 3.8.5)\n",
      "Hello from the pygame community. https://www.pygame.org/contribute.html\n",
      "WARNING:tensorflow:From <ipython-input-1-3ec8a970748d>:153: Sequential.predict_classes (from tensorflow.python.keras.engine.sequential) is deprecated and will be removed after 2021-01-01.\n",
      "Instructions for updating:\n",
      "Please use instead:* `np.argmax(model.predict(x), axis=-1)`,   if your model does multi-class classification   (e.g. if it uses a `softmax` last-layer activation).* `(model.predict(x) > 0.5).astype(\"int32\")`,   if your model does binary classification   (e.g. if it uses a `sigmoid` last-layer activation).\n"
     ]
    }
   ],
   "source": [
    "import cv2\n",
    "import os\n",
    "from keras.models import load_model\n",
    "import numpy as np\n",
    "from pygame import mixer\n",
    "import time\n",
    "from keras.preprocessing.image import img_to_array\n",
    "import imutils\n",
    "from keras.models import load_model\n",
    "\n",
    "mixer.init()\n",
    "sound = mixer.Sound('alarm.wav')\n",
    "\n",
    "# parameters for loading data and images\n",
    "detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'\n",
    "emotion_model_path = 'models/_mini_XCEPTION.102-0.66.hdf5'\n",
    "\n",
    "face = cv2.CascadeClassifier('haar cascade files\\haarcascade_frontalface_alt.xml')\n",
    "leye = cv2.CascadeClassifier('haar cascade files\\haarcascade_lefteye_2splits.xml')\n",
    "reye = cv2.CascadeClassifier('haar cascade files\\haarcascade_righteye_2splits.xml')\n",
    "\n",
    "\n",
    "glass_cascade= cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')\n",
    "\n",
    "def detect(gray,pic):\n",
    "    fc=cv2.CascadeClassifier('haarcascade_files/haarcascade_frontalface_default.xml')\n",
    "    face=fc.detectMultiScale(gray,1.3,5)\n",
    "    for (x,y,w,h) in face:\n",
    "        cv2.rectangle(pic,(x,y),(x+w,y+h),(255,0,0),2)\n",
    "        converted_gray=gray[y:y+h,x:x+w]\n",
    "        converted_color=pic[y:y+h,x:x+w]\n",
    "        glass = glass_cascade.detectMultiScale(converted_gray,1.04,5)\n",
    "        \n",
    "        for(ex,ey,ew,eh) in glass:\n",
    "            imag=cv2.rectangle(converted_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)\n",
    "            cv2.putText(imag,'active',(ex,ey-10),cv2.FONT_HERSHEY_SIMPLEX,0.9,(36,255,12),2)\n",
    "    return pic\n",
    "\n",
    "\n",
    "# hyper-parameters for bounding boxes shape\n",
    "# loading models\n",
    "face_detection = cv2.CascadeClassifier(detection_model_path)\n",
    "emotion_classifier = load_model(emotion_model_path, compile=False)\n",
    "EMOTIONS = [\"Frustrated\" ,\"disgusted\",\"scared\", \"Talking\", \"Depressed\", \"surprised\",\n",
    " \"neutral\"]\n",
    "\n",
    "\n",
    "lbl=['Close','Open']\n",
    "\n",
    "model = load_model('models/cnncat2.h5')\n",
    "path = os.getcwd()\n",
    "cap = cv2.VideoCapture(0)\n",
    "font = cv2.FONT_HERSHEY_COMPLEX_SMALL\n",
    "count=0\n",
    "score=0\n",
    "thicc=2\n",
    "rpred=[99]\n",
    "lpred=[99]\n",
    "\n",
    "\n",
    "# starting video streaming\n",
    "cv2.namedWindow('your_face')\n",
    "camera = cv2.VideoCapture(0)\n",
    "while True:\n",
    "    frame = camera.read()[1]\n",
    "    #reading the frame\n",
    "    frame = imutils.resize(frame,width=300)\n",
    "    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)\n",
    "    draw=detect(gray,frame)\n",
    "    cv2.imshow('Video',draw)\n",
    "    faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)\n",
    "    \n",
    "    #left_eye = leye.detectMultiScale(gray)\n",
    "    #right_eye =  reye.detectMultiScale(gray)\n",
    "    \n",
    "    \n",
    "    canvas = np.zeros((250, 300, 3), dtype=\"uint8\")\n",
    "    frameClone = frame.copy()\n",
    "    if len(faces) > 0:\n",
    "        faces = sorted(faces, reverse=True,\n",
    "        key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]\n",
    "        (fX, fY, fW, fH) = faces\n",
    "                    # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare\n",
    "            # the ROI for classification via the CNN\n",
    "        roi = gray[fY:fY + fH, fX:fX + fW]\n",
    "        roi = cv2.resize(roi, (64, 64))\n",
    "        roi = roi.astype(\"float\") / 255.0\n",
    "        roi = img_to_array(roi)\n",
    "        roi = np.expand_dims(roi, axis=0)\n",
    "        \n",
    "        \n",
    "        preds = emotion_classifier.predict(roi)[0]\n",
    "        emotion_probability = np.max(preds)\n",
    "        label = EMOTIONS[preds.argmax()]\n",
    "    else: continue\n",
    "\n",
    " \n",
    "    for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):\n",
    "                # construct the label text\n",
    "                text = \"{}: {:.2f}%\".format(emotion, prob * 100)\n",
    "\n",
    "                # draw the label + probability bar on the canvas\n",
    "               # emoji_face = feelings_faces[np.argmax(preds)]\n",
    "\n",
    "                \n",
    "                w = int(prob * 300)\n",
    "                cv2.rectangle(canvas, (7, (i * 35) + 5),\n",
    "                (w, (i * 35) + 35), (0, 0, 255), -1)\n",
    "                cv2.putText(canvas, text, (10, (i * 35) + 23),\n",
    "                cv2.FONT_HERSHEY_SIMPLEX, 0.45,\n",
    "                (255, 255, 255), 2)\n",
    "                cv2.putText(frameClone, label, (fX, fY - 10),\n",
    "                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)\n",
    "                cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),\n",
    "                              (0, 0, 255), 2)\n",
    "                \n",
    "    height,width = frame.shape[:2] \n",
    "\n",
    "    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)\n",
    "    \n",
    "    faces = face.detectMultiScale(gray,minNeighbors=5,scaleFactor=1.1,minSize=(25,25))\n",
    "    left_eye = leye.detectMultiScale(gray)\n",
    "    right_eye =  reye.detectMultiScale(gray)\n",
    "\n",
    "    cv2.rectangle(frame, (0,height-50) , (200,height) , (0,0,0) , thickness=cv2.FILLED )\n",
    "\n",
    "    for (x,y,w,h) in faces:\n",
    "        cv2.rectangle(frame, (x,y) , (x+w,y+h) , (100,100,100) , 1 )\n",
    "\n",
    "    for (x,y,w,h) in right_eye:\n",
    "        r_eye=frame[y:y+h,x:x+w]\n",
    "        count=count+1\n",
    "        r_eye = cv2.cvtColor(r_eye,cv2.COLOR_BGR2GRAY)\n",
    "        r_eye = cv2.resize(r_eye,(24,24))\n",
    "        r_eye= r_eye/255\n",
    "        r_eye=  r_eye.reshape(24,24,-1)\n",
    "        r_eye = np.expand_dims(r_eye,axis=0)\n",
    "        rpred = model.predict_classes(r_eye)\n",
    "        if(rpred[0]==1):\n",
    "            lbl='Open' \n",
    "        if(rpred[0]==0):\n",
    "            lbl='Closed'\n",
    "        break\n",
    "\n",
    "    for (x,y,w,h) in left_eye:\n",
    "        l_eye=frame[y:y+h,x:x+w]\n",
    "        count=count+1\n",
    "        l_eye = cv2.cvtColor(l_eye,cv2.COLOR_BGR2GRAY)  \n",
    "        l_eye = cv2.resize(l_eye,(24,24))\n",
    "        l_eye= l_eye/255\n",
    "        l_eye=l_eye.reshape(24,24,-1)\n",
    "        l_eye = np.expand_dims(l_eye,axis=0)\n",
    "        lpred = model.predict_classes(l_eye)\n",
    "        if(lpred[0]==1):\n",
    "            lbl='Open'   \n",
    "        if(lpred[0]==0):\n",
    "            lbl='Closed'\n",
    "        break\n",
    "\n",
    "    if(rpred[0]==0 and lpred[0]==0):\n",
    "        score=score+1\n",
    "        cv2.putText(frame,\"Closed\",(10,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)\n",
    "    # if(rpred[0]==1 or lpred[0]==1):\n",
    "    else:\n",
    "        score=score-1\n",
    "        cv2.putText(frame,\"Open\",(10,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)\n",
    "    \n",
    "        \n",
    "    if(score<0):\n",
    "        score=0   \n",
    "    cv2.putText(frame,'Score:'+str(score),(100,height-20), font, 1,(255,255,255),1,cv2.LINE_AA)\n",
    "    if(score>15):\n",
    "        #person is feeling sleepy so we beep the alarm\n",
    "        cv2.imwrite(os.path.join(path,'image.jpg'),frame)\n",
    "        try:\n",
    "            sound.play()\n",
    "            \n",
    "        except:  # isplaying = False\n",
    "            pass\n",
    "        if(thicc<16):\n",
    "            thicc= thicc+2\n",
    "        else:\n",
    "            thicc=thicc-2\n",
    "            if(thicc<2):\n",
    "                thicc=2\n",
    "        cv2.rectangle(frame,(0,0),(width,height),(0,0,255),thicc)\n",
    "        \n",
    "    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)\n",
    "    draw=detect(gray,frame)\n",
    "    cv2.imshow('Video',draw)\n",
    "    #cv2.imshow('frame',frame)\n",
    "\n",
    "    cv2.imshow('your_face', frameClone)\n",
    "    cv2.imshow(\"Probabilities\", canvas)\n",
    "    if cv2.waitKey(1) & 0xFF == ord('q'):\n",
    "        break\n",
    "\n",
    "camera.release()\n",
    "cv2.destroyAllWindows()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
