# RaceEngineer AI — AI Agent Development Assignment

## Overview
RaceEngineer AI is an educational, tool-using motorsport engineering assistant. It routes user requests to purpose-built tools for telemetry analysis, vehicle-dynamics investigation, and race-strategy calculations.

## Features
- CSV telemetry upload and channel statistics
- Telemetry plots for speed, throttle, brake, lateral acceleration and longitudinal acceleration
- Rule-based vehicle-dynamics investigation prompts
- Race time, pit-loss and fuel-use calculator
- Visible tool selection and explanation of why the agent selected a tool
- Synthetic sample dataset included

## Technology
Python, Streamlit, Pandas and Matplotlib.

## Run on Windows
1. Install Python 3.10 or newer and tick **Add Python to PATH** during installation.
2. Extract the ZIP file.
3. Double-click `run_app.bat`, or open CMD in this folder and run:

```bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Agent schema
The agent router selects a tool based on the task:
- `telemetry_tool`: descriptive statistics from numeric telemetry channels.
- `dynamics_tool`: structured engineering checks based on the reported symptom.
- `strategy_tool`: transparent race-time and fuel estimates from user inputs.
- `engineering_knowledge_tool`: general diagnostic workflow.

See `schema.md` for the architecture diagram and limitations.

## Dataset
`sample_telemetry.csv` contains synthetic, illustrative telemetry. It is not data from a real race car or driver. It can be replaced by a CSV with compatible column names.

Expected example columns: `time_s`, `speed_kmh`, `throttle_pct`, `brake_pct`, `lat_g`, `long_g`, `lap_time_s`.

## Limitations
This prototype uses deterministic routing and engineering rules; it does not call a hosted LLM. It is designed to demonstrate agent-style tool selection and transparent calculations without requiring an API key. It does not automatically determine a validated vehicle setup. Real engineering conclusions require verified data, sensor context, and domain review.

## Suggested assignment description
**Title:** RaceEngineer AI: A Tool-Using Motorsport Engineering Agent

**Objective:** To develop an agent that identifies the type of motorsport engineering request, invokes a suitable analytical tool, and returns an interpretable result with assumptions and limitations.

**Outcome:** A working web application that combines telemetry statistics, vehicle-dynamics troubleshooting guidance, and race-strategy calculations in one interface.
