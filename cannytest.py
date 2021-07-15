import cv2
import numpy as np
import serial
#import picamera ,sys
cap = cv2.VideoCapture(0)

#To aduino
port="/dev/ttyUSB0"
ser = serial.Serial(port, 9600)


while(True):
    ret, frame = cap.read()
    if not ret:
        break
    
    lower_red = np.array([110, 50, 50])   #HSV
    upper_red = np.array([130, 255, 200])  #GOOD
    rszframe = cv2.resize(frame,(640, 480))
    resizeframe = frame[150:500, 400:800].copy()
    resizeframe2 = cv2.resize(resizeframe, dsize = (640,640), interpolation=cv2.INTER_CUBIC)
    src = cv2.GaussianBlur(resizeframe2, (0, 0), 1)
    red_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(red_hsv, lower_red, upper_red)
    dst = cv2.bitwise_and(src, src, mask = mask_red)
    hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    #dst2 = cv2.GaussianBlur(hsv, (0,0), 3)
        #blr = cv2.GaussianBlur(hsv,(0,0),1.0)
        #h, s, v = cv2.split(hsv)
    circles = cv2.HoughCircles(hsv, cv2.HOUGH_GRADIENT, 1, 80, param1=300, param2=10,minRadius=0,maxRadius=30)
    if circles is not None:
        ser.write([1])
        for i in range(circles.shape[1]):
            cx, cy, radius = circles[0][i]
            cv2.circle(resizeframe2, (cx, cy), radius, (50,50,55), 2, cv2.LINE_AA)
    cv2.imshow("MSTRACK", resizeframe2)
    #cv2.imshow("MSTRACK2", resizeframe2)
    #cv2.imshow("src",rszframe)
    #cv2.imshow("MSTRACK2", resizeframe2)

    if cv2.waitKey(1)==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

