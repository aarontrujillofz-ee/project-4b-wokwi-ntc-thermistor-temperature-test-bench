# Engineering Notes

## Design Intent

Project 4B upgrades a basic ADC validation bench into a realistic sensor validation bench. Instead of reading a potentiometer, the Arduino reads a thermistor-derived analog voltage and converts it into an engineering quantity: temperature.

## Why This Project Matters

This project is useful for hardware test, embedded test, and validation roles because it demonstrates:

- ADC measurement
- Sensor modeling
- Voltage divider calculations
- Temperature conversion
- Threshold validation
- CSV logging
- Python-based automated reporting

## Key Correction

For the divider orientation used here:

```text
5V -> 10k fixed resistor -> A0/OUT -> NTC -> GND
```

higher temperature means lower NTC resistance, which means lower measured A0 voltage.

If a data table shows temperature rising while voltage rises using this same equation, the table is inverted and wrong.

## Final Result Rule

Use worst-case logic:

```text
FAIL > WARN > NORMAL
```

That means one FAIL sample makes the whole run FAIL.
