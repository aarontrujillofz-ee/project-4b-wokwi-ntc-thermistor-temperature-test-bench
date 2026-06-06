# Project 4B - Wokwi NTC Thermistor Temperature Test Bench

## Overview

Project 4B is a simulated embedded temperature validation bench. It extends the Project 4A Wokwi ADC validation workflow from a simple potentiometer input to an NTC thermistor temperature sensor model.

Project 4A workflow:

```text
potentiometer -> Arduino ADC -> voltage -> NORMAL/WARN/FAIL -> Python report
```

Project 4B workflow:

```text
NTC thermistor sensor -> Arduino ADC -> voltage -> resistance -> temperature -> NORMAL/WARN/FAIL -> Python report
```

This project demonstrates a complete engineering workflow: circuit simulation, ADC conversion, thermistor math, serial CSV logging, Python data analysis, plot generation, automated PDF reporting, and GitHub documentation.

## Live Wokwi Simulation

Create a Wokwi project, then copy these files into it:

```text
wokwi/sketch.ino
wokwi/diagram.json
```

After uploading to GitHub, add your public Wokwi simulation link here:

```text
Wokwi Simulation: https://wokwi.com/projects/466046213563687937
```

## Engineering Goal

The goal is to validate whether a simulated temperature sensor is operating inside expected limits:

| Status | Temperature Condition |
| ------ | --------------------- |
| NORMAL | temperature < 40 C |
| WARN | 40 C <= temperature < 50 C |
| FAIL | temperature >= 50 C |

## Circuit Description

The simulation uses:

- Arduino Uno
- Wokwi NTC analog temperature sensor
- Analog pin A0
- 5 V reference
- Ground
- Serial Monitor output

The conceptual divider model is:

```text
5V -> 10k fixed resistor -> A0/OUT -> NTC thermistor -> GND
```

With this orientation, higher temperature lowers the NTC resistance, which lowers the measured A0 voltage.

## NTC Thermistor Theory

An NTC thermistor has resistance that decreases as temperature increases. This project uses a 10k nominal thermistor model at 25 C with beta coefficient 3950.

## ADC Conversion

The Arduino Uno ADC is treated as a 10-bit converter:

```text
voltage = adc_value * 5.0 / 1023.0
```

## Resistance Calculation

For the divider orientation used in this project:

```text
resistance_ntc = fixed_resistor * voltage / (5.0 - voltage)
```

## Temperature Calculation

The Beta equation is used:

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

Then:

```text
temperature_c = temperature_k - 273.15
```

## Pass/Warn/Fail Logic

```text
NORMAL: temperature < 40 C
WARN:   40 C <= temperature < 50 C
FAIL:   temperature >= 50 C
```

## Final Test Results

The included sample run contains all three validation states:

```text
NORMAL, WARN, FAIL
```

The Python script calculates the final result using the worst observed state:

```text
FAIL overrides WARN, and WARN overrides NORMAL.
```

## Evidence Generated

The analyzer generates:

```text
plots/ntc_temperature_plot.png
plots/ntc_voltage_plot.png
plots/ntc_resistance_plot.png
reports/project4b_summary.txt
reports/project4b_ntc_test_report.pdf
evidence/project4b_report_final_run.pdf
evidence/project4b_summary_final_run.txt
evidence/ntc_temperature_plot_final_run.png
evidence/ntc_voltage_plot_final_run.png
evidence/ntc_resistance_plot_final_run.png
```

## How to Run

From PowerShell:

```powershell
cd "C:\Users\fall3\Desktop\Project_4B_Wokwi_NTC_Thermistor_Temperature_Test_Bench"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\python\analyze_ntc_log.py
```

## How to Use Wokwi Files

1. Create a new Arduino Uno project in Wokwi.
2. Replace the default `sketch.ino` with `wokwi/sketch.ino`.
3. Replace the default `diagram.json` with `wokwi/diagram.json`.
4. Run the simulation.
5. Change the NTC temperature value in Wokwi.
6. Copy Serial Monitor CSV output into `data/ntc_serial_log.csv`.
7. Run the Python analyzer again.

## Screenshots to Add

Add these after running the project:

```text
screenshots/wokwi_ntc_circuit.png
screenshots/wokwi_serial_monitor.png
screenshots/python_successful_run.png
screenshots/github_repo.png
```

## What I Learned

- How to model an NTC thermistor temperature sensor in Wokwi
- How to convert Arduino ADC readings into voltage
- How to estimate thermistor resistance from a voltage divider
- How to use the Beta equation to calculate temperature
- How to classify sensor readings against engineering limits
- How to automate CSV analysis, plots, summaries, and PDF reports with Python

## Limitations

- The project is simulated, not physical hardware.
- The Wokwi NTC model is idealized compared with real thermistor tolerance, wiring resistance, ADC noise, and self-heating.
- Real hardware validation should include calibration and measured reference temperatures.

## Next Upgrade

Project 4C should repeat the same workflow using real hardware:

```text
Real Arduino or Tiva-C board -> physical NTC divider -> ADC reading -> Python report
```

## Resume Bullet

Developed a simulated embedded temperature test bench using Wokwi, Arduino Uno ADC logic, NTC thermistor modeling, Python data analysis, CSV logging, threshold validation, and automated PDF reporting to demonstrate a complete hardware test workflow.

## Interview Explanation

After building Project 4A with a potentiometer ADC input, I upgraded the workflow into Project 4B using an NTC thermistor model. The Arduino reads the analog voltage from a thermistor divider, converts ADC counts to voltage, calculates thermistor resistance, converts resistance into temperature using the Beta equation, and classifies the result as NORMAL, WARN, or FAIL. I then analyze the serial CSV data in Python to generate plots and an engineering PDF report. This project connects circuit theory, embedded ADC reading, sensor math, validation limits, and automated reporting.
