
String inString = "";
int timePeriod = 1000;
int ledPin = 13;

void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial)
  {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // send an intro:
  Serial.println("CAM TRIGGER");

  pinMode(ledPin, OUTPUT);
}

void loop()
{
  digitalWrite(ledPin, HIGH);
  delay(timePeriod * 0.1);
  digitalWrite(ledPin, LOW);
  delay(timePeriod * 0.9);

  if (Serial.available() > 0)
  {
    int inChar = Serial.read();
    if (isDigit(inChar))
    {
      // convert the incoming byte to a char and add it to the string:
      inString += (char)inChar;
    }
    // if you get a newline, print the string, then the string's value:
    if (inChar == '\n')
    {
      timePeriod = inString.toInt();
//      Serial.print("Value:");
      Serial.println(timePeriod);
      //      Serial.print("String: ");
      //      Serial.println(inString);
      // clear the string for new input:
      inString = "";
    }
  }
}
