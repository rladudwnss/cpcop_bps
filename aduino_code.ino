//GPIO
#define PIEZO 2 // 피에조 부저
#define Relay 3 // 릴레이
#define motorR1 4
#define motorR2 5
#define motorL1 6
#define motorL2 7
#define LED 8
#define PWM 9

#define leftLineSensor A0
#define rightLineSensor A1
#define centerLineSensor A2
#define TRIG 12 //TRIG 핀 설정 (초음파 보내는 핀)
#define ECHO 13 //ECHO 핀 설정 (초음파 받는 핀)

int Brakeflag =0;
int i;
int select_mode = 0; //mode = 1-> auto mode, mode = 2 -> manual mode
int serial_num = 0;  //serial_number = serial.read
void setup() 
{
  //connect
  Serial.begin(9600);
  Serial.setTimeout(50);
  //line sensor 
  pinMode(leftLineSensor, INPUT);
  pinMode(rightLineSensor, INPUT);  
  pinMode(centerLineSensor, INPUT);  
  //choumpa sensor
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  //motor
  pinMode(motorR1, OUTPUT);             // 모터1사용 가능 제어핀 출력으로 설정
  pinMode(motorR2, OUTPUT);               // 방향제어를 위한 핀1 출력으로 설정
  pinMode(motorL1, OUTPUT);              // 방향제어를 위한 핀2 출력으로 설정
  pinMode(motorL2, OUTPUT);              // 방향제어를 위한 핀2 출력으로 설정
  digitalWrite(PWM, LOW);         // 일단 모터가 작동하지 않도록 초기화
  //SONG
  pinMode(PIEZO, OUTPUT);
  //Relay
  pinMode(Relay,OUTPUT); // 릴레이를 출력으로 설정
  //LED
  pinMode(LED, OUTPUT);
  
  analogWrite(PWM, 150);
}

void loop()
{
  serial_num = Serial.read();   //시리얼 넘버를 변수로 loop문 맨 처음에서 받아와 시리얼 넘버를 문제없이 받아낸다.
  if(serial_num==7)             //7번은 자동주행 모드
  {
    select_mode = 1;
    
  }
  else if(serial_num==8)         //8번은 수동주행 모드
  {
    select_mode = 2;
    //Serial.println(Serial.read());
  }
  
  //direction_num = Serial.read();
  switch (select_mode){          
    case 1:                     //1번(자동주행 모드)인 경우 원을 인식하면 분사하고 주행하는 과정이 case 1이다.
      LineTracer();
      if(serial_num==5)
      {
         Stop();
         digitalWrite(Relay,HIGH);//분사 동작하기
         delay(1000);
         digitalWrite(Relay,LOW);
         delay(1000);
         Forward();
         delay(1000); 
         LineTracer();
        Serial.end();
        Serial.begin(9600);
      }
      else if(serial_num==2)
      {
        Serial.println("0");
        //LineTracer();
      }
      break;
    case 2:                      //수동주행 모드에서 의 모든 수행 과정을 담은  case2 이다.
      if(serial_num==3)
       {       
         Forward();
        }
      else if(serial_num==4)
      {
        Back();
      }
      else if(serial_num==1)
      {
        Right();
      }
      else if(serial_num==6)
      {
        Left();
        Serial.println(Serial.read());
      }
      else if(serial_num==9)
      {
        Stop();
        Serial.println(Serial.read());
      }
      else if(serial_num==10)
      {
        digitalWrite(Relay,HIGH);//분사 동작하기
      }
      break;
  }
  
}

void Forward()
{
    digitalWrite(motorR1, HIGH);
    digitalWrite(motorR2, LOW);
    digitalWrite(motorL1, HIGH);
    digitalWrite(motorL2, LOW);
}
void Back()
{   
    digitalWrite(motorR1, LOW);
    digitalWrite(motorR2, HIGH);
    digitalWrite(motorL1, LOW);
    digitalWrite(motorL2, HIGH);
}
void Stop()
{
    digitalWrite(motorR1, LOW);
    digitalWrite(motorR2, LOW);
    digitalWrite(motorL1, LOW);
    digitalWrite(motorL2, LOW);
}
void Right()
{
    digitalWrite(motorR1, LOW);
    digitalWrite(motorR2, HIGH);
    digitalWrite(motorL1, HIGH);
    digitalWrite(motorL2, LOW);
}
void Left()
{
    digitalWrite(motorR1, HIGH);
    digitalWrite(motorR2, LOW);
    digitalWrite(motorL1, LOW);
    digitalWrite(motorL2, HIGH);
}

void LineTracer()
{
  if(analogRead(centerLineSensor<100)) // 중간 센서가 검정색을 읽을때(반사x)
  {
    if (analogRead(leftLineSensor)>100 && analogRead(rightLineSensor)>100) 
    {
      Forward();  
    }  
// 만약 왼쪽 센서만 ‘선감지(반사신호X)’ 경우 :  좌회전
    else if (analogRead(leftLineSensor)<100 && analogRead(rightLineSensor)>100) 
    {
      Left(); 
    }   
// 만약 오른쪽 센서만 ‘선감지(반사신호X)’ 경우 :  우회전
    else if (analogRead(leftLineSensor)>100 && !analogRead(rightLineSensor) < 100) 
    {
      Right();
    } 
// 만약 양쪽 센서 모두 ‘선감지(반사신호X)’ 경우 :  정지
    else if (analogRead(leftLineSensor)<100 && analogRead(rightLineSensor)<100) 
    {
      Stop();
    }  
  }
  else  // 중간 센서가 흰색을 읽을때(반사o)
  {
    if(analogRead(leftLineSensor)>100 && analogRead(rightLineSensor)>100)
    {
     Right(); 
    }
  }
}

//////////////////////////////////////////////////////////////////
//Crush Brake
void CrushBrake()
{
    long duration, distance;
    
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);
    duration = pulseIn (ECHO, HIGH); //물체에 반사되어돌아온 초음파의 시간을 변수에 저장합니다.

    //34000*초음파가 물체로 부터 반사되어 돌아오는시간 /1000000 / 2(왕복값이아니라 편도값이기때문에 나누기2를 해줍니다.
    //초음파센서의 거리값이 위 계산값과 동일하게 Cm로 환산되는 계산공식 입니다. 수식이 간단해지도록 적용했습니다.
    distance = duration * 17 / 1000;
    
    if(distance <= 10)
    {
      Stop();
    }
    
}
