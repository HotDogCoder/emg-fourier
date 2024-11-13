#include <Arduino.h>

#define MUSCLE_SENSOR_PIN 26  // Pin donde está conectado el sensor EMG

void setup()
{
  Serial.begin(9600);         // High baud rate for fast communication
  pinMode(MUSCLE_SENSOR_PIN, INPUT);
}

void loop()
{
  int emg_value = analogRead(MUSCLE_SENSOR_PIN);  // Read sensor value
  Serial.println(emg_value);  // Send value via serial
  delay(100);  // Throttle to 100 samples per second
}