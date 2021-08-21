import time
import cv2 as cv
from os import path

PERIOD = 60 # Seconds

cap = cv.VideoCapture(0, cv.CAP_DSHOW)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

FRAME_DIR = 'frames'

cur_frame = 0
while True:
  frame_name = f'{cur_frame}.png'

  ret, frame = cap.read()
  # frame = cv.resize(frame, (1280,720))
  print(path.join('.', FRAME_DIR, frame_name))
  # cv.imwrite(path.join(FRAME_DIR, frame_name), frame)
  cv.imshow('Frame', frame)
  print(frame.shape)
  if cv.waitKey(1) & 0xFF == ord('q'):
      break
  cur_frame += 1
  # time.sleep(PERIOD)