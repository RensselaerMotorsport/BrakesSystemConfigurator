int offset = 0;

void setup() {
  Serial.begin(115200); //Start Serial Monitor to display current read value on Serial monitor
  delay (3000);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.print(millis());
  Serial.print(",");
  Serial.print((2.5 - ((analogRead(A0)) * (5.0 / 1024.0)) )/0.066);
  Serial.println(",");
  delay(2);
}
