/*
  Project 4B - Wokwi NTC Thermistor Temperature Test Bench
  Author: Aaron Trujillo

  Purpose:
  Reads a simulated NTC thermistor voltage divider on Arduino Uno A0,
  converts ADC counts to voltage, resistance, and temperature, then prints
  CSV rows for Python analysis and engineering report generation.

  Circuit model:
  5V -> 10k fixed resistor -> A0/OUT -> NTC thermistor -> GND

  Important: With this divider orientation, higher temperature causes NTC
  resistance to drop, so A0 voltage also drops.
*/

#include <math.h>

const int NTC_PIN = A0;

const float VREF = 5.0;
const float ADC_MAX = 1023.0;
const float FIXED_RESISTOR_OHMS = 10000.0;
const float NOMINAL_RESISTANCE_OHMS = 10000.0;
const float NOMINAL_TEMPERATURE_K = 298.15;   // 25 C
const float BETA_COEFFICIENT = 3950.0;

const float WARN_TEMP_C = 40.0;
const float FAIL_TEMP_C = 50.0;

unsigned long lastSampleMs = 0;
const unsigned long SAMPLE_PERIOD_MS = 1000;

const char* classifyStatus(float temperatureC) {
  if (temperatureC >= FAIL_TEMP_C) {
    return "FAIL";
  }
  if (temperatureC >= WARN_TEMP_C) {
    return "WARN";
  }
  return "NORMAL";
}

float adcToVoltage(int adcValue) {
  return adcValue * VREF / ADC_MAX;
}

float voltageToResistance(float voltage) {
  // Divider: 5V -> fixed resistor -> A0 -> NTC -> GND
  // Vout = VREF * Rntc / (Rfixed + Rntc)
  // Rntc = Rfixed * Vout / (VREF - Vout)
  if (voltage <= 0.0) {
    return 0.0;
  }
  if (voltage >= VREF) {
    return 1e9;
  }
  return FIXED_RESISTOR_OHMS * voltage / (VREF - voltage);
}

float resistanceToTemperatureC(float resistanceOhms) {
  if (resistanceOhms <= 0.0) {
    return NAN;
  }

  float inverseTemperatureK = (1.0 / NOMINAL_TEMPERATURE_K) +
                              (1.0 / BETA_COEFFICIENT) *
                              log(resistanceOhms / NOMINAL_RESISTANCE_OHMS);

  float temperatureK = 1.0 / inverseTemperatureK;
  return temperatureK - 273.15;
}

void printCsvHeader() {
  Serial.println("time_ms,adc_value,voltage,resistance_ohms,temperature_c,status");
}

void setup() {
  Serial.begin(9600);
  delay(1000);
  printCsvHeader();
}

void loop() {
  unsigned long nowMs = millis();

  if (nowMs - lastSampleMs >= SAMPLE_PERIOD_MS) {
    lastSampleMs = nowMs;

    int adcValue = analogRead(NTC_PIN);
    float voltage = adcToVoltage(adcValue);
    float resistanceOhms = voltageToResistance(voltage);
    float temperatureC = resistanceToTemperatureC(resistanceOhms);
    const char* status = classifyStatus(temperatureC);

    Serial.print(nowMs);
    Serial.print(",");
    Serial.print(adcValue);
    Serial.print(",");
    Serial.print(voltage, 3);
    Serial.print(",");
    Serial.print(resistanceOhms, 1);
    Serial.print(",");
    Serial.print(temperatureC, 2);
    Serial.print(",");
    Serial.println(status);
  }
}
