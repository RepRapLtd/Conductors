/* Sells Robot Control Program

   Adrian
   RepRapPro Ltd
   4 January 2015
   
 */


const int ledPin =  11;      // the number of the LED pin

// The motors are each connected to two digital output pins, which
// can then be driven like an H bridge.

const int mLeft_a = A4;
const int mLeft_b = A5;
const int mRight_a = 7;
const int mRight_b = 8;
const int bump = 9;
long time;
const int flash = 10;
const int freq = 500;

// Set the drive direction

void Go(bool forward)
{
  if(forward)
  {
    digitalWrite(mLeft_a, 0);
    digitalWrite(mLeft_b, 1);
    digitalWrite(mRight_a, 0);
    digitalWrite(mRight_b, 1);
  } else
  {
    digitalWrite(mLeft_b, 0);
    digitalWrite(mLeft_a, 1);
    digitalWrite(mRight_b, 0);
    digitalWrite(mRight_a, 1);
  }
}

void Spin(bool anti)
{
  if(anti)
  {
    digitalWrite(mLeft_a, 0);
    digitalWrite(mLeft_b, 1);
    digitalWrite(mRight_b, 0);
    digitalWrite(mRight_a, 1);
  } else
  {
    digitalWrite(mLeft_a, 0);
    digitalWrite(mLeft_b, 1);
    digitalWrite(mRight_b, 0);
    digitalWrite(mRight_a, 1);
  }        
}

void Hit()
{
  digitalWrite(ledPin, true);
  Go(false);
  delay(1000 + random(3000));
  Spin(random(2));
  delay(1000 + random(3000));
  Go(true);
  time = millis()+freq;
  digitalWrite(ledPin, false); 
}

void setup() 
{
  pinMode(ledPin, OUTPUT);  
  pinMode(mLeft_a, OUTPUT); 
  pinMode(mLeft_b, OUTPUT); 
  pinMode(mRight_a, OUTPUT); 
  pinMode(mRight_b, OUTPUT);
  pinMode(bump, INPUT_PULLUP);
  Go(true);
  time = millis()+freq;
  digitalWrite(ledPin, false);
}

void loop()
{
  if(!digitalRead(bump))
    Hit();
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

