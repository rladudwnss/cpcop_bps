import cv2                 #opencv 
import numpy as np         #영상을 다루기 위해 배열 numpy
import serial              #시리얼 통신을 위함
import os                  #운영체제 제어를 위함
from socket import*        #소켓통신을 위함
from threading import*     #object detection과 통신을 위해 쓰레딩

port="/dev/ttyUSB0"                #시리얼 통신에 대한 초기설정
ser = serial.Serial(port, 9600)

#쓰레드를 사용할 수 있도록 카메라 기능에 대한 함수 정의
def camfunc():
    serwrite_flag = 0                #원을 검출 했는지 판단하기 위한 flag
    cap = cv2.VideoCapture(0)        #웹캠을 킴
    #while문을 통하여 프레임을 받아오고, 해당 프레임에 대해 원 검출을 하는 과정
    while(True):                      
        ret, frame = cap.read()
        if not ret:
            break
         #색상을 검출하기 위한 범위 설정
        lower_red = np.array([110, 50, 50])  
        upper_red = np.array([130, 255, 200])  
        #원검출을 확실하게 하기 위해 받아온 영상의 크기를 조절하고 확대하는 과정
        rszframe = cv2.resize(frame,(640, 480))
        resizeframe = frame[150:500, 400:800].copy()
        resizeframe2 = cv2.resize(resizeframe, dsize = (640,640), interpolation=cv2.INTER_CUBIC)    #영상을 확대시 보간법을 정해주어야 하는데 이는 INTER_CUBIC이다.
        #위에서 만들어준 색상 범위를 적용하여 특정색만 검출 하도록 해주는 과정이다.
        src = cv2.GaussianBlur(resizeframe2, (0, 0), 1)
        red_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(red_hsv, lower_red, upper_red)
        dst = cv2.bitwise_and(src, src, mask = mask_red)
        hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)


        #허프서클 알고리즘을 사용하여 원을 검출하는 과정이다. 함수 내의 파라미터를 조절하여 민감도를 설정해 줄 수 있다.
        circles = cv2.HoughCircles(hsv, cv2.HOUGH_GRADIENT, 1, 80, param1=300, param2=10,minRadius=0,maxRadius=30)
        #원을 검출 했는지 판단하여 ser값을 아두이노로 넘겨주는 과정.
        if serwrite_flag == 1:
            circles = None
            serwrite_flag = 0
            ser.write([2])
            print(serwrite_flag)
        if circles is not None:
            for i in range(circles.shape[1]):
                cx, cy, radius = circles[0][i]
                cv2.circle(resizeframe2, (cx, cy), radius, (50,50,55), 2, cv2.LINE_AA)
                ser.write([5])
                serwrite_flag = 1
                print(serwrite_flag)

        cv2.imshow("MSTRACK", resizeframe2)
        if cv2.waitKey(1)==ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

#스레드를 사용하여 소켓통신을 하기 위해 만든 함수이다.
def serverfunc():
    #host에 대한 ip와 해당하는 port번호를 열어주었다. -> 포트포워딩을 하였고, 이 코드는 서버 코드이다.
    host = "192.168.0.98"  #host ip #"220.149.217.230"
    Port = 54321          #host port ID
    #server setting
    SER = serial.Serial(port, 9600)
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((host, Port))
    serverSocket.listen(1)
    print("wait")  
    (connectionSocket, addr) = serverSocket.accept()
    print(str(addr),"from connet.") #connet check
    #휴대폰 어플을 통해 접속하여, 해당하는 버튼을 눌렀을 경우, 그에 맞는 신호를 아두이노에 보내주는 반복문 + 조건문들 이다.
    while(True):
        data = connectionSocket.recv(1024)
        #if data=='d':
         #   print("recv data:", data.decode("utf-8"))
        #print("recv data:", data.decode("utf-8"))
         
        if data.decode("utf-8")=='r':   #우회전
            print("recv data:", data.decode("utf-8"))
            SER.write([1])  #right turn serial number '1'
        elif data.decode("utf-8")=='u': #전진
            print("recv data:", data.decode("utf-8"))
            SER.write([3])  #forward serial number  '3'
        elif data.decode("utf-8")=='d': #후진
            print("recv data:", data.decode("utf-8"))
            SER.write([4])  #backward serial number '4'
        elif data.decode("utf-8")=='l': #좌회전
            print("recv data:", data.decode("utf-8"))
            SER.write([6])   #left turn serial number '6'
        elif data.decode("utf-8")=='t': #자율주행 모드
            print("recv data:", data.decode("utf-8"))
            SER.write([7])   #auto mode serial number '7'
        elif data.decode("utf-8")=='m': #수동주행 모드
            print("recv data:", data.decode("utf-8"))
            SER.write([8])   #manual mode serial mode number '8'
        elif data.decode("utf-8")=='s': #수동주행 모드에서 브레이크
            print("recv data:", data.decode("utf-8"))
            SER.write([9])   #stop mode serial  mode number '9'
        elif data.decode("utf-8")=='p': #수동주행 모드에서 소독액 분사하는 과정
            print("recv data:", data.decode("utf-8"))
            SER.write([10])  #spray run serial number '10'
    serverSocket.close()

#스레드를 실행시키는 문장
if __name__ == '__main__':
    proc = Thread(target=camfunc, args=())
    proc2 = Thread(target=serverfunc, args=())
    proc.start()
    proc2.start()
