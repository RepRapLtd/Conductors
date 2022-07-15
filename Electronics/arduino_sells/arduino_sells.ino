/* Sells Robot Control Program

   Adrian
   RepRapPro Ltd
   4 January 2015

   ATTiny version
   29 June 2016

   Bump switch resets the processor
   
 */


const int ledPin =  3;      // the number of the LED pin

// The motors are each connected to two digital output pins, which
// can then be driven like an H bridge.

const int mLeft_a = 4;
const int mLeft_b = 0;
const int mRight_a = 1;
const int mRight_b = 2;
const int tick = 100;
//const int bump = 9;
long time;
const int flash = 10;
const int freq = 500;
const int leftPWM = 170;
const int rightPWM = 255;

// Set the drive direction

void Go(bool forward)
{
  if(forward)
  {
    digitalWrite(mLeft_a, 0);
    //digitalWrite(mLeft_b, 1);
    analogWrite(mLeft_b, leftPWM);
    //digitalWrite(mRight_a, 0);
    analogWrite(mRight_a, 255 - rightPWM);
    digitalWrite(mRight_b, 1);
  } else
  {
    //digitalWrite(mLeft_b, 0);
    analogWrite(mLeft_b, 255 - leftPWM);
    digitalWrite(mLeft_a, 1);
    digitalWrite(mRight_b, 0);
    //digitalWrite(mRight_a, 1);
    analogWrite(mRight_a, rightPWM);
  }
}

void Spin(bool anti)
{
  if(anti)
  {
    digitalWrite(mLeft_a, 0);
    //digitalWrite(mLeft_b, 1);
    analogWrite(mLeft_b, leftPWM);
    digitalWrite(mRight_b, 0);
    //digitalWrite(mRight_a, 1);
    analogWrite(mRight_a, rightPWM);
  } else
  {
    //digitalWrite(mLeft_b, 1);
    analogWrite(mLeft_b, 255 - leftPWM);
    digitalWrite(mLeft_a, 1);
    //digitalWrite(mRight_a, 1);
    analogWrite(mRight_a, 255 - rightPWM);
    digitalWrite(mRight_b, 1);
  }        
}

void Hit()
{
  digitalWrite(ledPin, true);
  Go(false);
  delay(tick + random(3*tick));
  Spin(random(2));
  delay(tick + random(3*tick));
  Go(true);
  time = millis()+freq;
  digitalWrite(ledPin, false); 
}

void setup() 
{
  randomSeed(analogRead(A0));
  pinMode(ledPin, OUTPUT);  
  pinMode(mLeft_a, OUTPUT); 
  pinMode(mLeft_b, OUTPUT); 
  pinMode(mRight_a, OUTPUT); 
  pinMode(mRight_b, OUTPUT);
//  pinMode(bump, INPUT_PULLUP);
//  Go(true);
  time = millis()+freq;
  digitalWrite(ledPin, false);
  Hit();
}

void loop()
{
//  if(!digitalRead(bump))
//    Hit();
  if(millis() > time)
  {
     if(digitalRead(ledPin))
     {
       digitalWrite(ledPin, false);
       time += freq;
     } else
     {
       digitalWrite(ledPin, true);
       time += flash;       
     }
  }
}

