#!/usr/bin/env python3
"""
Project 4B - NTC Thermistor CSV Analyzer

Loads Arduino/Wokwi serial CSV data, cleans it, calculates engineering summary
statistics, generates plots, and creates a PDF report.

Run from the project root:
    python python/analyze_ntc_log.py

Optional:
    python python/analyze_ntc_log.py --input data/ntc_serial_log.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import pandas as pd
import matplotlib.pyplot as plt

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing reportlab. Install dependencies with: pip install -r requirements.txt"
    ) from exc

PROJECT_TITLE = "Project 4B - Wokwi NTC Thermistor Temperature Test Bench"
EXPECTED_COLUMNS = [
    "time_ms",
    "adc_value",
    "voltage",
    "resistance_ohms",
    "temperature_c",
    "status",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_and_clean_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Handles accidental repeated Serial Monitor headers copied into the CSV.
    df = df[df["time_ms"].astype(str).str.lower() != "time_ms"].copy()

    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    numeric_cols = ["time_ms", "adc_value", "voltage", "resistance_ohms", "temperature_c"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["status"] = df["status"].astype(str).str.strip().str.upper()
    df = df.dropna(subset=numeric_cols + ["status"])
    df = df.sort_values("time_ms").reset_index(drop=True)

    if df.empty:
        raise ValueError("No valid data rows found after cleaning CSV.")

    return df


def status_counts(df: pd.DataFrame) -> Dict[str, int]:
    counts = df["status"].value_counts().to_dict()
    return {status: int(counts.get(status, 0)) for status in ["NORMAL", "WARN", "FAIL"]}


def final_result(df: pd.DataFrame) -> str:
    """Return worst-case result across the run."""
    statuses = set(df["status"].astype(str).str.upper())
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "NORMAL"


def make_single_plot(df: pd.DataFrame, y_col: str, ylabel: str, title: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    time_s = df["time_ms"] / 1000.0
    ax.plot(time_s, df[y_col], marker="o")
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)

    if y_col == "temperature_c":
        ax.axhline(40, linestyle="--", linewidth=1, label="WARN threshold: 40 C")
        ax.axhline(50, linestyle="--", linewidth=1, label="FAIL threshold: 50 C")
        ax.legend()

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def generate_plots(df: pd.DataFrame, plots_dir: Path) -> Dict[str, Path]:
    plots = {
        "temperature": plots_dir / "ntc_temperature_plot.png",
        "voltage": plots_dir / "ntc_voltage_plot.png",
        "resistance": plots_dir / "ntc_resistance_plot.png",
    }
    make_single_plot(df, "temperature_c", "Temperature (C)", "NTC Temperature vs Time", plots["temperature"])
    make_single_plot(df, "voltage", "Voltage (V)", "NTC Divider Voltage vs Time", plots["voltage"])
    make_single_plot(df, "resistance_ohms", "Resistance (ohms)", "NTC Resistance vs Time", plots["resistance"])
    return plots


def make_summary_text(df: pd.DataFrame) -> str:
    counts = status_counts(df)
    result = final_result(df)
    return f"""{PROJECT_TITLE}

Purpose:
Validate a simulated NTC thermistor temperature measurement workflow using Arduino ADC data, sensor conversion math, threshold classification, Python analysis, plots, and automated report generation.

Circuit Description:
The simulated circuit uses an Arduino Uno analog input connected to a Wokwi NTC temperature sensor. The model represents a 10k NTC thermistor behavior with a beta coefficient of 3950 and a 10k nominal resistance at 25 C.

Formula Summary:
voltage = adc_value * 5.0 / 1023.0
resistance_ntc = fixed_resistor * voltage / (5.0 - voltage)
1/T = 1/T0 + (1/B) * ln(R/R0)
temperature_c = temperature_k - 273.15

Test Limits:
NORMAL: temperature < 40 C
WARN: 40 C <= temperature < 50 C
FAIL: temperature >= 50 C

Status Counts:
NORMAL: {counts['NORMAL']}
WARN: {counts['WARN']}
FAIL: {counts['FAIL']}

Engineering Summary:
Samples analyzed: {len(df)}
Minimum temperature: {df['temperature_c'].min():.2f} C
Maximum temperature: {df['temperature_c'].max():.2f} C
Average temperature: {df['temperature_c'].mean():.2f} C
Minimum voltage: {df['voltage'].min():.3f} V
Maximum voltage: {df['voltage'].max():.3f} V
Minimum resistance: {df['resistance_ohms'].min():.1f} ohms
Maximum resistance: {df['resistance_ohms'].max():.1f} ohms

Final Result:
{result}

Conclusion:
The Project 4B test bench demonstrates a complete simulated embedded sensor validation workflow: analog sensing, ADC conversion, thermistor resistance calculation, temperature conversion, threshold classification, CSV logging, Python analysis, and automated engineering report generation.
"""


def write_summary(summary_text: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary_text, encoding="utf-8")


def generate_pdf_report(df: pd.DataFrame, plots: Dict[str, Path], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6))
    story = []
    story.append(Paragraph(PROJECT_TITLE, styles["Title"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Purpose", styles["Section"]))
    story.append(Paragraph("Validate a simulated NTC thermistor temperature measurement workflow using Arduino ADC data, sensor conversion math, threshold classification, Python analysis, plots, and automated report generation.", styles["BodyText"]))
    story.append(Paragraph("Circuit Description", styles["Section"]))
    story.append(Paragraph("The Wokwi simulation uses an Arduino Uno analog input connected to an NTC temperature sensor model. The Arduino reads A0, converts ADC counts to voltage, estimates thermistor resistance, converts resistance to temperature using the Beta equation, and prints CSV data to the serial monitor.", styles["BodyText"]))
    story.append(Paragraph("Formula Summary", styles["Section"]))
    formulas = [
        ["ADC to voltage", "voltage = adc_value * 5.0 / 1023.0"],
        ["Voltage to resistance", "resistance_ntc = fixed_resistor * voltage / (5.0 - voltage)"],
        ["Beta equation", "1/T = 1/T0 + (1/B) * ln(R/R0)"],
        ["Kelvin to Celsius", "temperature_c = temperature_k - 273.15"],
    ]
    formula_table = Table(formulas, colWidths=[1.8 * inch, 4.7 * inch])
    formula_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(formula_table)
    story.append(Paragraph("Test Limits", styles["Section"]))
    limits = [["Status", "Temperature Condition"], ["NORMAL", "temperature < 40 C"], ["WARN", "40 C <= temperature < 50 C"], ["FAIL", "temperature >= 50 C"]]
    limits_table = Table(limits, colWidths=[1.5 * inch, 5.0 * inch])
    limits_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(limits_table)
    counts = status_counts(df)
    result = final_result(df)
    story.append(Paragraph("Engineering Summary", styles["Section"]))
    summary_rows = [
        ["Metric", "Value"],
        ["Samples analyzed", str(len(df))],
        ["NORMAL count", str(counts["NORMAL"])],
        ["WARN count", str(counts["WARN"])],
        ["FAIL count", str(counts["FAIL"])],
        ["Min temperature", f"{df['temperature_c'].min():.2f} C"],
        ["Max temperature", f"{df['temperature_c'].max():.2f} C"],
        ["Average temperature", f"{df['temperature_c'].mean():.2f} C"],
        ["Min voltage", f"{df['voltage'].min():.3f} V"],
        ["Max voltage", f"{df['voltage'].max():.3f} V"],
        ["Min resistance", f"{df['resistance_ohms'].min():.1f} ohms"],
        ["Max resistance", f"{df['resistance_ohms'].max():.1f} ohms"],
        ["Final result", result],
    ]
    summary_table = Table(summary_rows, colWidths=[2.3 * inch, 4.2 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(summary_table)
    story.append(PageBreak())
    story.append(Paragraph("Generated Plots", styles["Heading1"]))
    for label, path in [("Temperature Plot", plots["temperature"]), ("Voltage Plot", plots["voltage"]), ("Resistance Plot", plots["resistance"])]:
        story.append(Paragraph(label, styles["Section"]))
        story.append(Image(str(path), width=6.5 * inch, height=3.6 * inch))
        story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Conclusion", styles["Section"]))
    story.append(Paragraph("This project connects circuit theory, embedded ADC reading, thermistor sensor math, threshold validation, data logging, Python automation, plot generation, and PDF reporting. It is stronger portfolio evidence than a simple potentiometer ADC demo because it models a realistic sensor validation workflow.", styles["BodyText"]))
    doc.build(story)


def copy_final_evidence(project_root_path: Path, plots: Dict[str, Path]) -> None:
    evidence_dir = project_root_path / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    copies = {
        project_root_path / "reports" / "project4b_ntc_test_report.pdf": evidence_dir / "project4b_report_final_run.pdf",
        project_root_path / "reports" / "project4b_summary.txt": evidence_dir / "project4b_summary_final_run.txt",
        plots["temperature"]: evidence_dir / "ntc_temperature_plot_final_run.png",
        plots["voltage"]: evidence_dir / "ntc_voltage_plot_final_run.png",
        plots["resistance"]: evidence_dir / "ntc_resistance_plot_final_run.png",
    }
    for src, dst in copies.items():
        if src.exists():
            dst.write_bytes(src.read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Project 4B NTC thermistor CSV data.")
    parser.add_argument("--input", default="data/ntc_serial_log.csv", help="Path to input CSV file.")
    args = parser.parse_args()
    root = project_root()
    csv_path = (root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    df = load_and_clean_csv(csv_path)
    plots = generate_plots(df, root / "plots")
    summary_text = make_summary_text(df)
    summary_path = root / "reports" / "project4b_summary.txt"
    pdf_path = root / "reports" / "project4b_ntc_test_report.pdf"
    write_summary(summary_text, summary_path)
    generate_pdf_report(df, plots, pdf_path)
    copy_final_evidence(root, plots)
    print("Project 4B analysis complete.")
    print(f"Input CSV: {csv_path}")
    print(f"Summary: {summary_path}")
    print(f"PDF report: {pdf_path}")
    print(f"Final result: {final_result(df)}")
    print("Status counts:", status_counts(df))


if __name__ == "__main__":
    main()
