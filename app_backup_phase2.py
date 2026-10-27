from pathlib import Path
import re
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "f1_data"

FILES = {
    "Driver pace": "driver_pace.csv",
    "Sector analysis": "sector_analysis.csv",
    "Tyre performance": "tire_performance.csv",
    "Pit stops": "fact_pit_stops.csv",
    "Race results": "fact_race_results.csv",
    "Weather": "fact_weather_snapshots.csv",
    "Drivers": "dim_drivers.csv",
    "Circuits": "dim_circuits.csv",
    "Races": "dim_races.csv",
}

st.set_page_config(page_title="RaceEngineer AI", page_icon="🏁", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.4rem;}
.hero {padding: 1.25rem 1.5rem; border: 1px solid #303746; border-radius: 15px;
background: linear-gradient(115deg,#151a23,#222b3b); margin-bottom: 1rem;}
.hero h1 {color: #f4f6fa; margin: 0;}
.hero p {color: #bac4d3; margin: .4rem 0 0 0;}
</style>
<div class="hero">
<h1>🏁 RaceEngineer AI</h1>
<p>F1 Performance Intelligence · Local data analysis · Engineering tool router</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_datasets():
    result = {}
    for label, filename in FILES.items():
        path = DATA_DIR / filename
        if path.exists():
            try:
                result[label] = pd.read_csv(path)
            except Exception as exc:
                result[label] = pd.DataFrame()
                st.warning(f"Could not read {filename}: {exc}")
    return result

data = load_datasets()

with st.sidebar:
    st.title("Control Room")
    st.caption("F1 Performance Intelligence")
    st.markdown("**Available tools**")
    st.write("• Driver pace")
    st.write("• Sector performance")
    st.write("• Tyre performance")
    st.write("• Pit-stop records")
    st.write("• Race results")
    st.write("• Weather analysis")
    st.divider()
    st.caption("Local CSV datasets · No API key required")

if not data:
    st.error("No datasets were found. Make sure the f1_data folder is next to app.py.")
    st.stop()

nonempty = {k: v for k, v in data.items() if not v.empty}
total_rows = sum(len(df) for df in nonempty.values())
c1, c2, c3 = st.columns(3)
c1.metric("Datasets loaded", len(nonempty))
c2.metric("Combined rows", f"{total_rows:,}")
c3.metric("Data location", "Local CSV")

st.markdown("### Select an analysis")
task = st.selectbox(
    "Agent task",
    [
        "Driver pace comparison",
        "Sector performance",
        "Tyre performance",
        "Pit-stop analysis",
        "Race results",
        "Weather analysis",
        "Explore datasets",
    ],
)
question = st.text_input(
    "Engineering question",
    "Which drivers have the fastest average lap times?",
)

def apply_filters(df):
    view = df.copy()
    # Add filters only when corresponding fields exist, keeping this robust across CSV schemas.
    if "race_year" in view.columns:
        years = sorted(view["race_year"].dropna().unique().tolist())
        if len(years) > 1:
            year = st.selectbox("Season", years, index=len(years) - 1, key="filter_year")
            view = view[view["race_year"] == year]
    if "race_round" in view.columns:
        rounds = sorted(view["race_round"].dropna().unique().tolist())
        if len(rounds) > 1:
            rnd = st.selectbox("Race round", rounds, key="filter_round")
            view = view[view["race_round"] == rnd]
    if "session" in view.columns:
        sessions = sorted(view["session"].dropna().astype(str).unique().tolist())
        if len(sessions) > 1:
            sess = st.selectbox("Session", sessions, key="filter_session")
            view = view[view["session"].astype(str) == sess]
    return view

def to_seconds(series):
    return pd.to_numeric(series, errors="coerce") / 1000.0

def pick_column(df, candidates):
    lowered = {str(col).lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    for col in df.columns:
        if any(candidate.lower() in str(col).lower() for candidate in candidates):
            return col
    return None

def show_df(df):
    st.dataframe(df, use_container_width=True, hide_index=True)

if task == "Driver pace comparison":
    df = nonempty.get("Driver pace")
    if df is None:
        st.warning("driver_pace.csv was not found.")
    else:
        df = apply_filters(df)
        driver_col = pick_column(df, ["driver", "full_name", "driver_name", "abbreviation"])
        avg_col = pick_column(df, ["avg_lap_time_ms", "average_lap_time_ms", "avg_lap_time", "average_lap_time"])
        fast_col = pick_column(df, ["fastest_lap_ms", "fastest_lap_time_ms", "fastest_lap"])
        if avg_col:
            df["Average lap (s)"] = to_seconds(df[avg_col])
        if fast_col:
            df["Fastest lap (s)"] = to_seconds(df[fast_col])
        st.subheader("Driver pace")
        if driver_col and "Average lap (s)" in df:
            df = df.sort_values("Average lap (s)", ascending=True, na_position="last")
            show_df(df)
            chart = df.dropna(subset=["Average lap (s)"])
            if not chart.empty:
                st.plotly_chart(px.bar(chart, x=driver_col, y="Average lap (s)", title="Average lap time by driver"), use_container_width=True)
                best = chart.iloc[0]
                st.success(f"Lowest average lap time in the filtered records: {best[driver_col]} — {best['Average lap (s)']:.3f} s.")
        else:
            st.warning(f"Could not identify expected driver and average-lap columns. Available columns: {list(df.columns)}")
            show_df(df)
        st.caption("Lower average lap time means faster average pace only when records are comparable. Session type, traffic, tyre age, fuel load and lap count may differ.")

elif task == "Sector performance":
    df = nonempty.get("Sector analysis")
    if df is None:
        st.warning("sector_analysis.csv was not found.")
    else:
        df = apply_filters(df)
        driver_col = pick_column(df, ["driver", "full_name", "driver_name", "abbreviation"])
        sector_cols = [pick_column(df, [f"avg_sector{i}_ms", f"sector{i}_avg_ms", f"sector_{i}_ms"]) for i in (1, 2, 3)]
        sector_cols = [c for c in sector_cols if c]
        for col in sector_cols:
            df[f"{col} (s)"] = to_seconds(df[col])
        st.subheader("Sector performance")
        show_df(df)
        sec_display = [f"{c} (s)" for c in sector_cols]
        if driver_col and sec_display:
            long = df.melt(id_vars=[driver_col], value_vars=sec_display, var_name="Sector metric", value_name="Time (s)")
            st.plotly_chart(px.bar(long, x=driver_col, y="Time (s)", color="Sector metric", barmode="group", title="Average sector time comparison"), use_container_width=True)
        else:
            st.info("The dataset's sector column names differ from common patterns; inspect the table to confirm available fields.")
        st.caption("Sector times show where performance differs, but do not by themselves establish the cause of time loss.")

elif task == "Tyre performance":
    df = nonempty.get("Tyre performance")
    if df is None:
        st.warning("tire_performance.csv was not found.")
    else:
        df = apply_filters(df)
        avg_col = pick_column(df, ["avg_lap_time_ms", "average_lap_time_ms", "avg_lap_time"])
        compound_col = pick_column(df, ["tire_compound", "tyre_compound", "compound"])
        if avg_col:
            df["Average lap (s)"] = to_seconds(df[avg_col])
        st.subheader("Tyre performance")
        show_df(df)
        if avg_col and compound_col:
            chart = df.dropna(subset=["Average lap (s)"])
            if not chart.empty:
                grouped = chart.groupby(compound_col, dropna=False)["Average lap (s)"].mean().reset_index()
                st.plotly_chart(px.bar(grouped, x=compound_col, y="Average lap (s)", color=compound_col, title="Average lap time by compound"), use_container_width=True)
        st.caption("Compound comparisons are descriptive, not a controlled tyre-degradation test. Tyre age, track evolution, fuel load and session conditions may differ.")

elif task == "Pit-stop analysis":
    df = nonempty.get("Pit stops")
    if df is None:
        st.warning("fact_pit_stops.csv was not found.")
    else:
        df = apply_filters(df)
        st.subheader("Pit-stop records")
        show_df(df)
        time_col = pick_column(df, ["pit_duration_ms", "pit_stop_duration_ms", "duration_ms", "pit_in_ms"])
        driver_col = pick_column(df, ["driver", "full_name", "driver_name", "abbreviation"])
        if time_col:
            numeric = pd.to_numeric(df[time_col], errors="coerce")
            # pit_in_ms may be a timestamp/offset rather than stationary duration; do not label it as duration without metadata.
            if "duration" in time_col.lower():
                st.metric("Longest recorded pit duration", f"{numeric.max()/1000:.3f} s")
                if driver_col and numeric.notna().any():
                    plot = df.assign(**{"Pit time (s)": numeric / 1000}).dropna(subset=["Pit time (s)"])
                    st.plotly_chart(px.bar(plot, x=driver_col, y="Pit time (s)", title="Recorded pit duration by driver"), use_container_width=True)
            else:
                st.info(f"Found `{time_col}`, but its meaning needs confirmation from the data dictionary before interpreting it as pit-stop duration.")
        else:
            st.info("No obvious pit-stop duration column was found. The records are shown above for inspection.")

elif task == "Race results":
    df = nonempty.get("Race results")
    if df is None:
        st.warning("fact_race_results.csv was not found.")
    else:
        df = apply_filters(df)
        st.subheader("Race results")
        show_df(df)
        pos_col = pick_column(df, ["position", "finish_position", "position_order"])
        driver_col = pick_column(df, ["full_name", "driver", "driver_name", "abbreviation"])
        if pos_col and driver_col:
            chart = df.copy()
            chart[pos_col] = pd.to_numeric(chart[pos_col], errors="coerce")
            chart = chart.dropna(subset=[pos_col]).sort_values(pos_col)
            if not chart.empty:
                st.plotly_chart(px.bar(chart, x=driver_col, y=pos_col, title="Finishing position (lower is better)"), use_container_width=True)
        else:
            st.caption("No familiar driver/position column pair was detected; use the table to inspect the available fields.")

elif task == "Weather analysis":
    df = nonempty.get("Weather")
    if df is None:
        st.warning("fact_weather_snapshots.csv was not found.")
    else:
        df = apply_filters(df)
        st.subheader("Weather snapshots")
        show_df(df)
        time_col = pick_column(df, ["time_offset_ms", "elapsed_ms", "timestamp_ms"])
        track_col = pick_column(df, ["track_temp_c", "track_temperature_c"])
        air_col = pick_column(df, ["air_temp_c", "air_temperature_c"])
        if time_col and (track_col or air_col):
            chart = df.copy()
            chart["Elapsed time (min)"] = pd.to_numeric(chart[time_col], errors="coerce") / 60000
            ycols = [c for c in [track_col, air_col] if c]
            st.plotly_chart(px.line(chart.sort_values("Elapsed time (min)"), x="Elapsed time (min)", y=ycols, title="Track and air temperature"), use_container_width=True)
        st.caption("Weather observations provide context; they do not alone prove why lap times changed.")

elif task == "Explore datasets":
    name = st.selectbox("Dataset", list(nonempty.keys()))
    df = nonempty[name]
    st.subheader(name)
    a, b = st.columns(2)
    a.metric("Rows", f"{len(df):,}")
    b.metric("Columns", len(df.columns))
    show_df(df)
    st.markdown("**Column types and missing values**")
    details = pd.DataFrame({"Column": df.columns, "Type": [str(df[c].dtype) for c in df.columns], "Missing": [int(df[c].isna().sum()) for c in df.columns]})
    show_df(details)

st.divider()
with st.expander("Agent architecture / schema"):
    st.code("""User question
    ↓
Task router (selects an analysis tool)
    ↓
Load relevant local F1 CSV
    ↓
Check available columns and filter records
    ↓
Calculate metrics / prepare charts
    ↓
Display findings, assumptions and limitations""", language="text")
    st.write("This version is a deterministic tool-using agent prototype. It selects an analysis tool from the chosen task; it does not yet use an LLM for autonomous tool selection.")

with st.expander("Data provenance and engineering limitations"):
    st.write("The app reads the local curated CSV files copied into f1_data. The downloaded repository documentation describes a 2024 Round 1 example bundle; do not assume this is the entire 2024 season.")
    st.write("Lap times stored in milliseconds are displayed in seconds where recognised. Verify the data dictionary before interpreting fields whose meanings are ambiguous.")
    st.write("This data is primarily curated session/lap-level data. Do not infer raw steering, brake-pressure, throttle-position or high-frequency GPS telemetry unless those channels are actually present.")

st.caption("RaceEngineer AI · Educational motorsport analysis prototype · Verify findings before engineering or strategy decisions.")
