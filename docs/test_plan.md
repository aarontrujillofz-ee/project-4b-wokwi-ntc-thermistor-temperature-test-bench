# Project 4B Test Plan

## Purpose

Validate the Project 4B Wokwi NTC thermistor temperature test bench across NORMAL, WARN, and FAIL temperature ranges.

## Equipment / Tools

- Wokwi Arduino Uno simulator
- Wokwi NTC analog temperature sensor
- Arduino Serial Monitor
- Python 3
- pandas, matplotlib, reportlab

## Data Output Format

The Arduino Serial Monitor must print:

```csv
time_ms,adc_value,voltage,resistance_ohms,temperature_c,status
```

## Test 1 - Normal Temperature

Set the NTC temperature below 40 C.

Expected status:

```text
NORMAL
```

Expected final result if only normal data is captured:

```text
Final result: NORMAL
```

## Test 2 - Warning Temperature

Set the NTC temperature above or equal to 40 C but below 50 C.

Expected status:

```text
WARN
```

Expected final result if WARN appears and FAIL does not appear:

```text
Final result: WARN
```

## Test 3 - Failure Temperature

Set the NTC temperature above or equal to 50 C.

Expected status:

```text
FAIL
```

Expected final result if any FAIL appears:

```text
Final result: FAIL
```

## Pass Criteria

The project passes if:

1. Arduino prints valid CSV rows.
2. Python loads the CSV without errors.
3. Python generates all three plots.
4. Python generates the text summary.
5. Python generates the PDF report.
6. Status classification matches the thresholds.
