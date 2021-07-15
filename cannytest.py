import cv2
import numpy as np
import serial                  #아두이노와 시리얼통신을 위한 라이브러리

cap = cv2.VideoCapture(0)      #카메라를 열어준다.

#라즈베리파이와 아두이노를 연결하기 위한 과정
port="/dev/ttyUSB0"
ser = serial.Serial(port, 9600)


while(True):
    ret, frame = cap.read()
    if not ret:             #카메라 안열릴 경우
        break
    
    lower_red = np.array([110, 50, 50])   #파란색의 특징점을 잡기 위한 BLUE COLOR 의 LOW HSV값
    upper_red = np.array([130, 255, 200])  #파란색의 특징점을 잡기 위한 BLUE COLOR 의 HIGH HSV값
    rszframe = cv2.resize(frame,(640, 480))    #영상의 크기가 크기 때문에 적당한 크기의 640 x 480의 해상도로 설정
    resizeframe = frame[150:500, 400:800].copy()       #특징점과의 거리가 멀기 때문에 확대를 위한 변경된 해상도의 영상을 확대(행렬 로 좌표값)
    resizeframe2 = cv2.resize(resizeframe, dsize = (640,640), interpolation=cv2.INTER_CUBIC)     #확대 영상을 640x640의 해상도, 보간법은 큐빅보간법
    src = cv2.GaussianBlur(resizeframe2, (0, 0), 1)    #노이즈 제거를 위한 가우시안 블러 전처리
    red_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)     #BGR영상 -> HSV변환
    mask_red = cv2.inRange(red_hsv, lower_red, upper_red)   #위에서 만든 마스크생성
    dst = cv2.bitwise_and(src, src, mask = mask_red)         #영상에 마스크 적용
    hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY              #허프서클적용을 위한 GRAY 스케일로 변환

    circles = cv2.HoughCircles(hsv, cv2.HOUGH_GRADIENT, 1, 80, param1=300, param2=10,minRadius=0,maxRadius=30)   #이동시 바른 검출을 위해 각 파라미터 조절
    if circles is not None:    #원을 검출시
        ser.write([1])         #아두이노에 신호 전송
        for i in range(circles.shape[1]):
            cx, cy, radius = circles[0][i]
            cv2.circle(resizeframe2, (cx, cy), radius, (50,50,55), 2, cv2.LINE_AA) #원 그리기
    cv2.imshow("MSTRACK", resizeframe2)


    if cv2.waitKey(1)==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

