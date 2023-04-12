#include <Servo.h>

Servo myservo;  // create servo object to control a servo

void setup() {
  myservo.attach(9);  // (pin, min, max)
}

void loop() {

  int i;

  for(i=0;i<=180;i++)
  {
     myservo.write(i);
     delay(50);
  }
  delay(30000);
  for(i=180;i>=0;i--)
  {
     myservo.write(i);
     delay(50);
  }
  delay(30000);
  
                  
}
