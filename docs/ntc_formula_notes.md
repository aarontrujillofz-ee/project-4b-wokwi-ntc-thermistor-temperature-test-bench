# NTC Formula Notes

## ADC to Voltage

```text
voltage = adc_value * 5.0 / 1023.0
```

## Voltage Divider

Conceptual circuit:

```text
5V -> Rfixed -> A0/OUT -> Rntc -> GND
```

Voltage divider equation:

```text
Vout = Vref * Rntc / (Rfixed + Rntc)
```

Solving for thermistor resistance:

```text
Rntc = Rfixed * Vout / (Vref - Vout)
```

## Beta Equation

```text
1/T = 1/T0 + (1/B) * ln(R/R0)
```

Where:

```text
T  = temperature in Kelvin
T0 = 298.15 K
R0 = 10000 ohms
B  = 3950
R  = measured thermistor resistance
```

Convert Kelvin to Celsius:

```text
temperature_c = temperature_k - 273.15
```

## Expected Trend

For an NTC thermistor:

```text
Temperature increases -> resistance decreases
Resistance decreases -> voltage decreases for this divider orientation
ADC reading decreases -> calculated temperature increases
```
