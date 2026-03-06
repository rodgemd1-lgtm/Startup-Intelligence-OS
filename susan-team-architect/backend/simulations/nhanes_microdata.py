"""CDC NHANES Microdata Ingestor — downloads and processes REAL survey data.

Unlike the existing NHANESIngestor (which uses AI to synthesize profiles),
this module downloads actual XPT (SAS transport) files from the CDC website,
parses them with pandas, computes population-level statistical summaries,
and stores the results as text chunks in the RAG knowledge base.

Data source: NHANES 2017-2018 cycle
URL: https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/
"""
from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# Ensure the backend package root is on sys.path so imports resolve
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from rag_engine.retriever import Retriever
from susan_core.schemas import KnowledgeChunk

# ── Dataset Registry ────────────────────────────────────────────────
_CDC_BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles"

NHANES_DATASETS = {
    "DEMO": {
        "url": f"{_CDC_BASE}/DEMO_J.XPT",
        "description": "Demographics",
    },
    "BMX": {
        "url": f"{_CDC_BASE}/BMX_J.XPT",
        "description": "Body Measures (BMI, weight, height, waist circumference)",
    },
    "PAQ": {
        "url": f"{_CDC_BASE}/PAQ_J.XPT",
        "description": "Physical Activity",
    },
    "BPX": {
        "url": f"{_CDC_BASE}/BPX_J.XPT",
        "description": "Blood Pressure",
    },
    "DBQ": {
        "url": f"{_CDC_BASE}/DBQ_J.XPT",
        "description": "Diet Behavior & Nutrition",
    },
}

CHUNK_SOURCE = "nhanes:microdata_2017_2018"
CHUNK_METADATA = {
    "type": "population_health",
    "survey": "NHANES",
    "cycle": "2017-2018",
}


# ── Helpers ──────────────────────────────────────────────────────────

def _download_xpt(url: str, label: str) -> pd.DataFrame:
    """Download a SAS transport (.XPT) file and return a DataFrame."""
    print(f"  Downloading {label} from {url} ...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    buf = io.BytesIO(resp.content)
    df = pd.read_sas(buf, format="xport")
    print(f"    -> {len(df):,} rows, {len(df.columns)} columns")
    return df


def _age_bucket(age: float) -> str:
    """Map a continuous age to a labeled bucket."""
    if age < 18:
        return "<18"
    elif age < 30:
        return "18-29"
    elif age < 40:
        return "30-39"
    elif age < 50:
        return "40-49"
    elif age < 60:
        return "50-59"
    elif age < 70:
        return "60-69"
    else:
        return "70+"


def _bmi_category(bmi: float) -> str:
    """CDC BMI classification."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    elif bmi < 35:
        return "Obese Class I"
    elif bmi < 40:
        return "Obese Class II"
    else:
        return "Obese Class III"


def _bp_category(systolic: float, diastolic: float) -> str:
    """AHA blood pressure classification."""
    if systolic < 120 and diastolic < 80:
        return "Normal"
    elif systolic < 130 and diastolic < 80:
        return "Elevated"
    elif systolic < 140 or diastolic < 90:
        return "Hypertension Stage 1"
    elif systolic >= 140 or diastolic >= 90:
        return "Hypertension Stage 2"
    else:
        return "Unknown"


def _sex_label(code: float) -> str:
    """NHANES RIAGENDR: 1=Male, 2=Female."""
    if code == 1:
        return "Male"
    elif code == 2:
        return "Female"
    return "Unknown"


def _pct(part: int, total: int) -> str:
    """Format a percentage."""
    if total == 0:
        return "0.0%"
    return f"{100 * part / total:.1f}%"


# ── Statistical Summaries ──────────────────────────────────────────

def _summarize_bmi_by_age_sex(merged: pd.DataFrame) -> list[str]:
    """BMI distribution by age group and sex."""
    chunks = []
    df = merged.dropna(subset=["BMXBMI", "RIDAGEYR", "RIAGENDR"]).copy()
    df["age_group"] = df["RIDAGEYR"].apply(_age_bucket)
    df["sex"] = df["RIAGENDR"].apply(_sex_label)
    df["bmi_cat"] = df["BMXBMI"].apply(_bmi_category)

    # Overall BMI summary
    overall_mean = df["BMXBMI"].mean()
    overall_median = df["BMXBMI"].median()
    overall_std = df["BMXBMI"].std()
    n = len(df)

    # Category distribution
    cat_counts = df["bmi_cat"].value_counts()
    cat_pcts = df["bmi_cat"].value_counts(normalize=True) * 100

    cat_lines = []
    for cat in ["Underweight", "Normal", "Overweight", "Obese Class I", "Obese Class II", "Obese Class III"]:
        if cat in cat_counts.index:
            cat_lines.append(f"  - {cat}: {cat_counts[cat]:,} ({cat_pcts[cat]:.1f}%)")

    chunk = (
        f"NHANES 2017-2018 BMI Distribution (Overall)\n"
        f"Source: CDC NHANES microdata, Body Measures (BMX_J)\n"
        f"Sample size: {n:,} respondents with valid BMI data.\n"
        f"Mean BMI: {overall_mean:.1f}, Median BMI: {overall_median:.1f}, Std Dev: {overall_std:.1f}\n"
        f"BMI Category Distribution:\n" + "\n".join(cat_lines) + "\n"
        f"Key finding: {cat_pcts.get('Overweight', 0) + cat_pcts.get('Obese Class I', 0) + cat_pcts.get('Obese Class II', 0) + cat_pcts.get('Obese Class III', 0):.1f}% "
        f"of the sample is overweight or obese (BMI >= 25)."
    )
    chunks.append(chunk)

    # By age group and sex
    for sex in ["Male", "Female"]:
        sex_df = df[df["sex"] == sex]
        for ag in ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]:
            sub = sex_df[sex_df["age_group"] == ag]
            if len(sub) < 10:
                continue
            mean_bmi = sub["BMXBMI"].mean()
            median_bmi = sub["BMXBMI"].median()
            pct_obese = (sub["BMXBMI"] >= 30).mean() * 100
            pct_overweight = ((sub["BMXBMI"] >= 25) & (sub["BMXBMI"] < 30)).mean() * 100
            pct_normal = ((sub["BMXBMI"] >= 18.5) & (sub["BMXBMI"] < 25)).mean() * 100

            chunk = (
                f"NHANES 2017-2018 BMI: {sex}, Age {ag}\n"
                f"Source: CDC NHANES microdata, Body Measures (BMX_J)\n"
                f"N = {len(sub):,}\n"
                f"Mean BMI: {mean_bmi:.1f}, Median BMI: {median_bmi:.1f}\n"
                f"Normal weight (18.5-24.9): {pct_normal:.1f}%\n"
                f"Overweight (25-29.9): {pct_overweight:.1f}%\n"
                f"Obese (30+): {pct_obese:.1f}%\n"
                f"Fitness app relevance: This demographic segment represents a key target "
                f"for {'weight management' if pct_obese > 35 else 'general fitness'} features."
            )
            chunks.append(chunk)

    return chunks


def _summarize_physical_activity(merged: pd.DataFrame) -> list[str]:
    """Physical activity levels by demographic."""
    chunks = []

    # PAQ605: Vigorous recreational activities (1=Yes, 2=No)
    # PAQ620: Moderate recreational activities (1=Yes, 2=No)
    # PAD680: Total minutes of sedentary activity per day
    # PAQ650: Minutes of vigorous recreational activities per week
    # PAQ665: Minutes of moderate recreational activities per week

    activity_cols = ["PAQ605", "PAQ620", "PAD680", "PAQ650", "PAQ665"]
    available_cols = [c for c in activity_cols if c in merged.columns]

    df = merged.dropna(subset=["RIDAGEYR", "RIAGENDR"]).copy()
    df["age_group"] = df["RIDAGEYR"].apply(_age_bucket)
    df["sex"] = df["RIAGENDR"].apply(_sex_label)

    # Overall activity summary
    if "PAQ605" in df.columns:
        vig_df = df[df["PAQ605"].isin([1, 2])]
        n_vigorous_yes = (vig_df["PAQ605"] == 1).sum()
        n_vigorous_total = len(vig_df)

        mod_df = df[df["PAQ620"].isin([1, 2])] if "PAQ620" in df.columns else pd.DataFrame()
        n_moderate_yes = (mod_df["PAQ620"] == 1).sum() if len(mod_df) > 0 else 0
        n_moderate_total = len(mod_df)

        chunk = (
            f"NHANES 2017-2018 Physical Activity Prevalence (Overall)\n"
            f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
            f"Vigorous recreational activity: {_pct(n_vigorous_yes, n_vigorous_total)} "
            f"of respondents report doing vigorous recreational activities "
            f"({n_vigorous_yes:,} of {n_vigorous_total:,}).\n"
            f"Moderate recreational activity: {_pct(n_moderate_yes, n_moderate_total)} "
            f"of respondents report doing moderate recreational activities "
            f"({n_moderate_yes:,} of {n_moderate_total:,}).\n"
            f"Fitness app opportunity: {_pct(n_vigorous_total - n_vigorous_yes, n_vigorous_total)} "
            f"of the population does NOT do vigorous activity — a large addressable market."
        )
        chunks.append(chunk)

    # Sedentary time
    if "PAD680" in df.columns:
        sed_df = df[df["PAD680"].between(0, 1440)]  # valid minutes in a day
        if len(sed_df) > 0:
            mean_sed = sed_df["PAD680"].mean()
            median_sed = sed_df["PAD680"].median()
            pct_8plus = (sed_df["PAD680"] >= 480).mean() * 100

            chunk = (
                f"NHANES 2017-2018 Sedentary Behavior\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"N = {len(sed_df):,} respondents with valid sedentary time data.\n"
                f"Mean daily sedentary time: {mean_sed:.0f} minutes ({mean_sed / 60:.1f} hours)\n"
                f"Median daily sedentary time: {median_sed:.0f} minutes ({median_sed / 60:.1f} hours)\n"
                f"{pct_8plus:.1f}% of respondents are sedentary 8+ hours per day.\n"
                f"Product insight: Movement reminders and micro-workout features could target "
                f"the {pct_8plus:.0f}% who sit 8+ hours daily."
            )
            chunks.append(chunk)

    # Activity by age group
    if "PAQ605" in df.columns:
        for ag in ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]:
            sub = df[(df["age_group"] == ag) & df["PAQ605"].isin([1, 2])]
            if len(sub) < 10:
                continue
            pct_vig = (sub["PAQ605"] == 1).mean() * 100

            mod_sub = sub[sub["PAQ620"].isin([1, 2])] if "PAQ620" in sub.columns else pd.DataFrame()
            pct_mod = (mod_sub["PAQ620"] == 1).mean() * 100 if len(mod_sub) > 0 else 0

            sed_sub = sub[sub["PAD680"].between(0, 1440)] if "PAD680" in sub.columns else pd.DataFrame()
            avg_sed = sed_sub["PAD680"].mean() if len(sed_sub) > 0 else 0

            chunk = (
                f"NHANES 2017-2018 Physical Activity: Age {ag}\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"N = {len(sub):,}\n"
                f"Vigorous activity participation: {pct_vig:.1f}%\n"
                f"Moderate activity participation: {pct_mod:.1f}%\n"
                f"Mean daily sedentary time: {avg_sed:.0f} minutes\n"
                f"Age-group insight: {'Younger adults are more active but still have high sedentary time.' if ag in ['18-29', '30-39'] else 'Activity levels decline with age, presenting opportunities for accessible fitness programming.'}"
            )
            chunks.append(chunk)

    # Activity by sex
    if "PAQ605" in df.columns:
        for sex in ["Male", "Female"]:
            sub = df[(df["sex"] == sex) & df["PAQ605"].isin([1, 2])]
            if len(sub) < 10:
                continue
            pct_vig = (sub["PAQ605"] == 1).mean() * 100
            mod_sub = sub[sub["PAQ620"].isin([1, 2])] if "PAQ620" in sub.columns else pd.DataFrame()
            pct_mod = (mod_sub["PAQ620"] == 1).mean() * 100 if len(mod_sub) > 0 else 0

            chunk = (
                f"NHANES 2017-2018 Physical Activity: {sex}\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"N = {len(sub):,}\n"
                f"Vigorous recreational activity: {pct_vig:.1f}%\n"
                f"Moderate recreational activity: {pct_mod:.1f}%\n"
                f"Gender insight: {'Men report higher vigorous activity rates.' if sex == 'Male' else 'Women may prefer moderate-intensity programming; app should offer varied intensity options.'}"
            )
            chunks.append(chunk)

    return chunks


def _summarize_blood_pressure(merged: pd.DataFrame) -> list[str]:
    """Blood pressure categories by age."""
    chunks = []

    # BPXOSY1: Systolic (1st reading oscillometric)
    # BPXODI1: Diastolic (1st reading oscillometric)
    # Fall back to BPXSY1/BPXDI1 (manual) if oscillometric not available
    sys_col = "BPXOSY1" if "BPXOSY1" in merged.columns else "BPXSY1" if "BPXSY1" in merged.columns else None
    dia_col = "BPXODI1" if "BPXODI1" in merged.columns else "BPXDI1" if "BPXDI1" in merged.columns else None

    if sys_col is None or dia_col is None:
        # Try alternative column names from the 2017-2018 cycle
        bp_cols = [c for c in merged.columns if c.startswith("BPX") or c.startswith("BPD")]
        if bp_cols:
            chunks.append(
                f"NHANES 2017-2018 Blood Pressure Data\n"
                f"Available BP columns: {', '.join(bp_cols)}\n"
                f"Note: Standard systolic/diastolic column names not found in expected format."
            )
        return chunks

    df = merged.dropna(subset=[sys_col, dia_col, "RIDAGEYR"]).copy()
    df["age_group"] = df["RIDAGEYR"].apply(_age_bucket)
    df["sex"] = df["RIAGENDR"].apply(_sex_label) if "RIAGENDR" in df.columns else "Unknown"
    df["bp_cat"] = df.apply(lambda r: _bp_category(r[sys_col], r[dia_col]), axis=1)

    # Overall BP summary
    n = len(df)
    mean_sys = df[sys_col].mean()
    mean_dia = df[dia_col].mean()
    bp_dist = df["bp_cat"].value_counts(normalize=True) * 100

    bp_lines = []
    for cat in ["Normal", "Elevated", "Hypertension Stage 1", "Hypertension Stage 2"]:
        if cat in bp_dist.index:
            bp_lines.append(f"  - {cat}: {bp_dist[cat]:.1f}%")

    chunk = (
        f"NHANES 2017-2018 Blood Pressure Distribution (Overall)\n"
        f"Source: CDC NHANES microdata, Blood Pressure Examination (BPX_J)\n"
        f"N = {n:,} respondents with valid BP readings.\n"
        f"Mean systolic: {mean_sys:.1f} mmHg, Mean diastolic: {mean_dia:.1f} mmHg\n"
        f"BP Category Distribution (AHA classification):\n" + "\n".join(bp_lines) + "\n"
        f"Health app relevance: BP tracking and cardiovascular health features "
        f"are relevant to the {bp_dist.get('Hypertension Stage 1', 0) + bp_dist.get('Hypertension Stage 2', 0):.1f}% "
        f"with hypertension."
    )
    chunks.append(chunk)

    # By age group
    for ag in ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]:
        sub = df[df["age_group"] == ag]
        if len(sub) < 10:
            continue
        avg_sys = sub[sys_col].mean()
        avg_dia = sub[dia_col].mean()
        pct_hyper = ((sub["bp_cat"] == "Hypertension Stage 1") | (sub["bp_cat"] == "Hypertension Stage 2")).mean() * 100
        pct_normal = (sub["bp_cat"] == "Normal").mean() * 100

        chunk = (
            f"NHANES 2017-2018 Blood Pressure: Age {ag}\n"
            f"Source: CDC NHANES microdata, Blood Pressure Examination (BPX_J)\n"
            f"N = {len(sub):,}\n"
            f"Mean systolic: {avg_sys:.1f} mmHg, Mean diastolic: {avg_dia:.1f} mmHg\n"
            f"Normal BP: {pct_normal:.1f}%, Hypertension (any stage): {pct_hyper:.1f}%\n"
            f"Age trend: {'BP risk increases significantly in this age group.' if pct_hyper > 40 else 'Moderate hypertension prevalence in this age group.'}"
        )
        chunks.append(chunk)

    return chunks


def _summarize_diet_behavior(merged: pd.DataFrame) -> list[str]:
    """Diet quality indicators from DBQ."""
    chunks = []
    df = merged.dropna(subset=["RIDAGEYR"]).copy()
    df["age_group"] = df["RIDAGEYR"].apply(_age_bucket)
    df["sex"] = df["RIAGENDR"].apply(_sex_label) if "RIAGENDR" in df.columns else "Unknown"

    # DBQ700: How healthy is the diet (1=Excellent, 2=Very good, 3=Good, 4=Fair, 5=Poor)
    if "DBQ700" in df.columns:
        diet_df = df[df["DBQ700"].isin([1, 2, 3, 4, 5])]
        if len(diet_df) > 0:
            n = len(diet_df)
            dist = diet_df["DBQ700"].value_counts(normalize=True).sort_index() * 100
            labels = {1: "Excellent", 2: "Very good", 3: "Good", 4: "Fair", 5: "Poor"}
            dist_lines = [f"  - {labels.get(k, k)}: {v:.1f}%" for k, v in dist.items()]

            pct_good_plus = dist.get(1, 0) + dist.get(2, 0) + dist.get(3, 0)
            pct_poor = dist.get(4, 0) + dist.get(5, 0)

            chunk = (
                f"NHANES 2017-2018 Self-Rated Diet Quality\n"
                f"Source: CDC NHANES microdata, Diet Behavior & Nutrition (DBQ_J)\n"
                f"Question: 'How healthy is your overall diet?' (DBQ700)\n"
                f"N = {n:,}\n"
                f"Distribution:\n" + "\n".join(dist_lines) + "\n"
                f"{pct_good_plus:.1f}% rate their diet as Good or better.\n"
                f"{pct_poor:.1f}% rate their diet as Fair or Poor.\n"
                f"Nutrition feature opportunity: {pct_poor:.0f}% of users self-identify as having "
                f"poor/fair diets — prime audience for meal planning and nutrition guidance."
            )
            chunks.append(chunk)

            # By age group
            for ag in ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]:
                sub = diet_df[diet_df["age_group"] == ag]
                if len(sub) < 10:
                    continue
                sub_dist = sub["DBQ700"].value_counts(normalize=True).sort_index() * 100
                pct_good = sub_dist.get(1, 0) + sub_dist.get(2, 0) + sub_dist.get(3, 0)

                chunk = (
                    f"NHANES 2017-2018 Diet Quality: Age {ag}\n"
                    f"Source: CDC NHANES microdata, Diet Behavior & Nutrition (DBQ_J)\n"
                    f"N = {len(sub):,}\n"
                    f"Good or better diet: {pct_good:.1f}%\n"
                    f"Fair or poor diet: {100 - pct_good:.1f}%\n"
                    f"Mean self-rating: {sub['DBQ700'].mean():.2f} (1=Excellent to 5=Poor)"
                )
                chunks.append(chunk)

    # DBD895: Number of meals not prepared at home (past 7 days)
    if "DBD895" in df.columns:
        meals_df = df[df["DBD895"].between(0, 21)]  # reasonable range
        if len(meals_df) > 0:
            mean_meals_out = meals_df["DBD895"].mean()
            median_meals_out = meals_df["DBD895"].median()
            pct_high = (meals_df["DBD895"] >= 7).mean() * 100

            chunk = (
                f"NHANES 2017-2018 Eating Out Frequency\n"
                f"Source: CDC NHANES microdata, Diet Behavior & Nutrition (DBQ_J)\n"
                f"Question: Meals not prepared at home in past 7 days (DBD895)\n"
                f"N = {len(meals_df):,}\n"
                f"Mean: {mean_meals_out:.1f} meals/week, Median: {median_meals_out:.0f} meals/week\n"
                f"{pct_high:.1f}% eat out 7+ times per week (1+ per day).\n"
                f"Meal planning opportunity: High frequency of eating out suggests strong demand "
                f"for healthy meal prep guidance and restaurant menu navigation features."
            )
            chunks.append(chunk)

    # DBD900: Number of meals from fast food (past 7 days)
    if "DBD900" in df.columns:
        ff_df = df[df["DBD900"].between(0, 21)]
        if len(ff_df) > 0:
            mean_ff = ff_df["DBD900"].mean()
            pct_daily_ff = (ff_df["DBD900"] >= 7).mean() * 100

            chunk = (
                f"NHANES 2017-2018 Fast Food Consumption\n"
                f"Source: CDC NHANES microdata, Diet Behavior & Nutrition (DBQ_J)\n"
                f"Question: Meals from fast food in past 7 days (DBD900)\n"
                f"N = {len(ff_df):,}\n"
                f"Mean: {mean_ff:.1f} fast food meals/week\n"
                f"{pct_daily_ff:.1f}% eat fast food daily (7+ times/week).\n"
                f"Health coaching opportunity: Fast food frequency is a modifiable behavior "
                f"that fitness apps can target through nutritional awareness features."
            )
            chunks.append(chunk)

    return chunks


def _summarize_exercise_frequency(merged: pd.DataFrame) -> list[str]:
    """Exercise frequency distributions from PAQ data."""
    chunks = []
    df = merged.dropna(subset=["RIDAGEYR"]).copy()
    df["age_group"] = df["RIDAGEYR"].apply(_age_bucket)
    df["sex"] = df["RIAGENDR"].apply(_sex_label) if "RIAGENDR" in df.columns else "Unknown"

    # PAD645: Minutes vigorous recreational per day (on days when active)
    # PAD660: Minutes moderate recreational per day
    # PAQ610: Days of vigorous recreational per week
    # PAQ625: Days of moderate recreational per week

    # Vigorous exercise frequency
    if "PAQ610" in df.columns:
        vig_df = df[df["PAQ610"].between(1, 7)]
        if len(vig_df) > 0:
            mean_days = vig_df["PAQ610"].mean()
            dist = vig_df["PAQ610"].value_counts(normalize=True).sort_index() * 100

            dist_lines = [f"  - {int(k)} days/week: {v:.1f}%" for k, v in dist.items()]

            chunk = (
                f"NHANES 2017-2018 Vigorous Exercise Frequency\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"Among those who DO vigorous recreational activity (PAQ610):\n"
                f"N = {len(vig_df):,}\n"
                f"Mean: {mean_days:.1f} days/week\n"
                f"Distribution:\n" + "\n".join(dist_lines) + "\n"
                f"Workout scheduling insight: Most vigorous exercisers train {mean_days:.0f} days/week. "
                f"App workout plans should default to this frequency."
            )
            chunks.append(chunk)

    # Moderate exercise frequency
    if "PAQ625" in df.columns:
        mod_df = df[df["PAQ625"].between(1, 7)]
        if len(mod_df) > 0:
            mean_days = mod_df["PAQ625"].mean()

            chunk = (
                f"NHANES 2017-2018 Moderate Exercise Frequency\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"Among those who DO moderate recreational activity (PAQ625):\n"
                f"N = {len(mod_df):,}\n"
                f"Mean: {mean_days:.1f} days/week\n"
                f"Moderate exercisers are active {mean_days:.0f} days/week on average. "
                f"This aligns with WHO recommendation of 150+ min/week of moderate activity."
            )
            chunks.append(chunk)

    # Duration of vigorous activity
    if "PAD645" in df.columns:
        dur_df = df[df["PAD645"].between(1, 480)]  # 1 min to 8 hours
        if len(dur_df) > 0:
            mean_dur = dur_df["PAD645"].mean()
            median_dur = dur_df["PAD645"].median()
            pct_30plus = (dur_df["PAD645"] >= 30).mean() * 100
            pct_60plus = (dur_df["PAD645"] >= 60).mean() * 100

            chunk = (
                f"NHANES 2017-2018 Vigorous Workout Duration\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"Duration of vigorous activity per session (PAD645):\n"
                f"N = {len(dur_df):,}\n"
                f"Mean: {mean_dur:.0f} min, Median: {median_dur:.0f} min\n"
                f"30+ minutes per session: {pct_30plus:.1f}%\n"
                f"60+ minutes per session: {pct_60plus:.1f}%\n"
                f"Workout design insight: Typical vigorous session is {median_dur:.0f} minutes. "
                f"App should offer workouts in 15/30/45/60 minute brackets to match real behavior."
            )
            chunks.append(chunk)

    # Duration of moderate activity
    if "PAD660" in df.columns:
        dur_df = df[df["PAD660"].between(1, 480)]
        if len(dur_df) > 0:
            mean_dur = dur_df["PAD660"].mean()
            median_dur = dur_df["PAD660"].median()

            chunk = (
                f"NHANES 2017-2018 Moderate Workout Duration\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"Duration of moderate activity per session (PAD660):\n"
                f"N = {len(dur_df):,}\n"
                f"Mean: {mean_dur:.0f} min, Median: {median_dur:.0f} min\n"
                f"Design insight: Moderate activity sessions tend to be "
                f"{'longer' if mean_dur > 45 else 'similar in length to'} vigorous ones."
            )
            chunks.append(chunk)

    # Combined weekly exercise volume estimate
    has_vig = "PAQ610" in df.columns and "PAD645" in df.columns
    has_mod = "PAQ625" in df.columns and "PAD660" in df.columns

    if has_vig or has_mod:
        vol_df = df.copy()
        vol_df["vig_min_week"] = 0.0
        vol_df["mod_min_week"] = 0.0

        if has_vig:
            mask = vol_df["PAQ610"].between(1, 7) & vol_df["PAD645"].between(1, 480)
            vol_df.loc[mask, "vig_min_week"] = vol_df.loc[mask, "PAQ610"] * vol_df.loc[mask, "PAD645"]

        if has_mod:
            mask = vol_df["PAQ625"].between(1, 7) & vol_df["PAD660"].between(1, 480)
            vol_df.loc[mask, "mod_min_week"] = vol_df.loc[mask, "PAQ625"] * vol_df.loc[mask, "PAD660"]

        # WHO equivalent: vigorous counts double
        vol_df["total_equiv_min"] = vol_df["mod_min_week"] + 2 * vol_df["vig_min_week"]

        adults = vol_df[vol_df["RIDAGEYR"] >= 18]
        if len(adults) > 0:
            pct_meets_who = (adults["total_equiv_min"] >= 150).mean() * 100
            pct_inactive = (adults["total_equiv_min"] == 0).mean() * 100

            chunk = (
                f"NHANES 2017-2018 WHO Physical Activity Guidelines Adherence\n"
                f"Source: CDC NHANES microdata, Physical Activity (PAQ_J)\n"
                f"WHO recommends >= 150 min/week of moderate-equivalent activity.\n"
                f"N = {len(adults):,} adults (18+)\n"
                f"Meets WHO guidelines: {pct_meets_who:.1f}%\n"
                f"Completely inactive (no recreational activity): {pct_inactive:.1f}%\n"
                f"Market sizing insight: {pct_inactive:.0f}% of adults are completely inactive, "
                f"representing the largest potential user base but highest activation challenge. "
                f"The {pct_meets_who:.0f}% who already meet guidelines are easiest to retain."
            )
            chunks.append(chunk)

    return chunks


def _summarize_demographics(merged: pd.DataFrame) -> list[str]:
    """Demographic overview of the NHANES sample."""
    chunks = []
    df = merged.dropna(subset=["RIDAGEYR"]).copy()
    df["age_group"] = df["RIDAGEYR"].apply(_age_bucket)
    df["sex"] = df["RIAGENDR"].apply(_sex_label) if "RIAGENDR" in df.columns else "Unknown"

    n = len(df)
    age_dist = df["age_group"].value_counts(normalize=True).sort_index() * 100
    sex_dist = df["sex"].value_counts(normalize=True) * 100

    age_lines = [f"  - {k}: {v:.1f}%" for k, v in age_dist.items()]
    sex_lines = [f"  - {k}: {v:.1f}%" for k, v in sex_dist.items()]

    chunk = (
        f"NHANES 2017-2018 Sample Demographics\n"
        f"Source: CDC NHANES microdata, Demographics (DEMO_J)\n"
        f"Total respondents in merged dataset: {n:,}\n"
        f"Age distribution:\n" + "\n".join(age_lines) + "\n"
        f"Sex distribution:\n" + "\n".join(sex_lines) + "\n"
        f"Mean age: {df['RIDAGEYR'].mean():.1f} years\n"
        f"Note: NHANES is designed to be nationally representative of the "
        f"US civilian non-institutionalized population."
    )
    chunks.append(chunk)

    # Race/ethnicity if available (RIDRETH3)
    if "RIDRETH3" in df.columns:
        race_map = {
            1: "Mexican American",
            2: "Other Hispanic",
            3: "Non-Hispanic White",
            4: "Non-Hispanic Black",
            6: "Non-Hispanic Asian",
            7: "Other/Multi-Racial",
        }
        race_df = df[df["RIDRETH3"].isin(race_map.keys())].copy()
        race_df["race_label"] = race_df["RIDRETH3"].map(race_map)
        race_dist = race_df["race_label"].value_counts(normalize=True) * 100

        race_lines = [f"  - {k}: {v:.1f}%" for k, v in race_dist.items()]

        chunk = (
            f"NHANES 2017-2018 Race/Ethnicity Distribution\n"
            f"Source: CDC NHANES microdata, Demographics (DEMO_J)\n"
            f"N = {len(race_df):,}\n"
            f"Distribution:\n" + "\n".join(race_lines) + "\n"
            f"Diversity consideration: Fitness app content and imagery should reflect "
            f"the diversity of the target market. Health disparities exist across groups."
        )
        chunks.append(chunk)

    return chunks


def _generate_cross_cutting_insights(merged: pd.DataFrame) -> list[str]:
    """Cross-cutting insights combining multiple data domains."""
    chunks = []
    df = merged.copy()

    # BMI vs Physical Activity
    if "BMXBMI" in df.columns and "PAQ605" in df.columns:
        cross_df = df.dropna(subset=["BMXBMI"]).copy()
        cross_df = cross_df[cross_df["PAQ605"].isin([1, 2])]
        cross_df["bmi_cat"] = cross_df["BMXBMI"].apply(_bmi_category)

        if len(cross_df) > 0:
            active = cross_df[cross_df["PAQ605"] == 1]
            inactive = cross_df[cross_df["PAQ605"] == 2]

            active_bmi = active["BMXBMI"].mean() if len(active) > 0 else 0
            inactive_bmi = inactive["BMXBMI"].mean() if len(inactive) > 0 else 0

            active_obese = (active["BMXBMI"] >= 30).mean() * 100 if len(active) > 0 else 0
            inactive_obese = (inactive["BMXBMI"] >= 30).mean() * 100 if len(inactive) > 0 else 0

            chunk = (
                f"NHANES 2017-2018 BMI vs Physical Activity (Cross-Analysis)\n"
                f"Source: CDC NHANES microdata, BMX_J + PAQ_J merged\n"
                f"Vigorously active respondents: Mean BMI = {active_bmi:.1f}, "
                f"Obesity rate = {active_obese:.1f}% (N={len(active):,})\n"
                f"Inactive respondents: Mean BMI = {inactive_bmi:.1f}, "
                f"Obesity rate = {inactive_obese:.1f}% (N={len(inactive):,})\n"
                f"BMI difference: {inactive_bmi - active_bmi:.1f} points higher among inactive.\n"
                f"Retention insight: Users who are already active have lower BMI and may engage "
                f"differently than sedentary users starting their fitness journey. "
                f"Onboarding should adapt to both populations."
            )
            chunks.append(chunk)

    # BMI vs Blood Pressure
    sys_col = "BPXOSY1" if "BPXOSY1" in df.columns else "BPXSY1" if "BPXSY1" in df.columns else None
    if "BMXBMI" in df.columns and sys_col:
        cross_df = df.dropna(subset=["BMXBMI", sys_col]).copy()
        cross_df["bmi_cat"] = cross_df["BMXBMI"].apply(_bmi_category)

        if len(cross_df) > 0:
            cat_bp = cross_df.groupby("bmi_cat")[sys_col].mean()
            lines = [f"  - {cat}: {bp:.1f} mmHg" for cat, bp in cat_bp.items()]

            chunk = (
                f"NHANES 2017-2018 BMI vs Blood Pressure (Cross-Analysis)\n"
                f"Source: CDC NHANES microdata, BMX_J + BPX_J merged\n"
                f"Mean systolic blood pressure by BMI category:\n" + "\n".join(lines) + "\n"
                f"Clinical insight: Higher BMI is associated with higher blood pressure. "
                f"Fitness apps targeting weight loss can position cardiovascular health benefits."
            )
            chunks.append(chunk)

    # Age vs BMI vs Activity (three-way)
    if "BMXBMI" in df.columns and "PAQ605" in df.columns:
        three_df = df.dropna(subset=["BMXBMI", "RIDAGEYR"]).copy()
        three_df = three_df[three_df["PAQ605"].isin([1, 2])]
        three_df["age_group"] = three_df["RIDAGEYR"].apply(_age_bucket)

        summary_lines = []
        for ag in ["18-29", "30-39", "40-49", "50-59", "60-69"]:
            ag_df = three_df[three_df["age_group"] == ag]
            if len(ag_df) < 20:
                continue
            active_pct = (ag_df["PAQ605"] == 1).mean() * 100
            mean_bmi = ag_df["BMXBMI"].mean()
            summary_lines.append(
                f"  - Age {ag}: {active_pct:.1f}% vigorous activity, mean BMI {mean_bmi:.1f}"
            )

        if summary_lines:
            chunk = (
                f"NHANES 2017-2018 Age-Activity-BMI Profile\n"
                f"Source: CDC NHANES microdata, DEMO_J + BMX_J + PAQ_J merged\n"
                f"Combined profile by age group:\n" + "\n".join(summary_lines) + "\n"
                f"Lifecycle insight: Activity rates generally decline while BMI increases with age. "
                f"Fitness app features should adapt to this lifecycle pattern."
            )
            chunks.append(chunk)

    return chunks


# ── Main Pipeline ──────────────────────────────────────────────────

def download_and_merge() -> pd.DataFrame:
    """Download all NHANES datasets and merge on SEQN."""
    print("=" * 60)
    print("NHANES 2017-2018 Microdata Download")
    print("=" * 60)

    frames = {}
    for key, info in NHANES_DATASETS.items():
        frames[key] = _download_xpt(info["url"], info["description"])

    # Start with demographics as the base table
    merged = frames["DEMO"]
    for key in ["BMX", "PAQ", "BPX", "DBQ"]:
        if key in frames:
            merged = merged.merge(frames[key], on="SEQN", how="left")
            print(f"  Merged {key}: {len(merged):,} rows")

    print(f"\nFinal merged dataset: {len(merged):,} rows, {len(merged.columns)} columns")
    return merged


def generate_chunks(merged: pd.DataFrame) -> list[str]:
    """Generate all statistical summary text chunks."""
    print("\n" + "=" * 60)
    print("Generating Statistical Summaries")
    print("=" * 60)

    all_chunks = []

    print("  [1/6] Demographics overview...")
    demo_chunks = _summarize_demographics(merged)
    all_chunks.extend(demo_chunks)
    print(f"      -> {len(demo_chunks)} chunks")

    print("  [2/6] BMI by age and sex...")
    bmi_chunks = _summarize_bmi_by_age_sex(merged)
    all_chunks.extend(bmi_chunks)
    print(f"      -> {len(bmi_chunks)} chunks")

    print("  [3/6] Physical activity levels...")
    pa_chunks = _summarize_physical_activity(merged)
    all_chunks.extend(pa_chunks)
    print(f"      -> {len(pa_chunks)} chunks")

    print("  [4/6] Blood pressure categories...")
    bp_chunks = _summarize_blood_pressure(merged)
    all_chunks.extend(bp_chunks)
    print(f"      -> {len(bp_chunks)} chunks")

    print("  [5/6] Diet quality indicators...")
    diet_chunks = _summarize_diet_behavior(merged)
    all_chunks.extend(diet_chunks)
    print(f"      -> {len(diet_chunks)} chunks")

    print("  [6/6] Exercise frequency distributions...")
    freq_chunks = _summarize_exercise_frequency(merged)
    all_chunks.extend(freq_chunks)
    print(f"      -> {len(freq_chunks)} chunks")

    print("\n  [BONUS] Cross-cutting insights...")
    cross_chunks = _generate_cross_cutting_insights(merged)
    all_chunks.extend(cross_chunks)
    print(f"      -> {len(cross_chunks)} chunks")

    print(f"\nTotal text chunks generated: {len(all_chunks)}")
    return all_chunks


def store_chunks(text_chunks: list[str]) -> int:
    """Store text chunks in the RAG knowledge base via Retriever."""
    print("\n" + "=" * 60)
    print("Storing in RAG Knowledge Base")
    print("=" * 60)

    retriever = Retriever()

    knowledge_chunks = [
        KnowledgeChunk(
            content=text,
            company_id="shared",
            data_type="user_research",
            source=CHUNK_SOURCE,
            metadata=CHUNK_METADATA,
        )
        for text in text_chunks
    ]

    stored = retriever.store_chunks(knowledge_chunks)
    print(f"  Stored {stored} chunks in Supabase pgvector")
    print(f"  company_id='shared', data_type='user_research'")
    print(f"  source='{CHUNK_SOURCE}'")
    return stored


def run() -> dict:
    """Full pipeline: download -> merge -> analyze -> store."""
    # 1. Download and merge
    merged = download_and_merge()

    # 2. Generate statistical summaries
    text_chunks = generate_chunks(merged)

    # 3. Store in RAG
    stored = store_chunks(text_chunks)

    # Print sample chunks
    print("\n" + "=" * 60)
    print("Sample Chunks (first 3)")
    print("=" * 60)
    for i, chunk in enumerate(text_chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(chunk[:500])
        print("...")

    summary = {
        "rows_merged": len(merged),
        "columns_merged": len(merged.columns),
        "chunks_generated": len(text_chunks),
        "chunks_stored": stored,
        "source": CHUNK_SOURCE,
        "datasets": list(NHANES_DATASETS.keys()),
    }

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    for k, v in summary.items():
        print(f"  {k}: {v}")

    return summary


if __name__ == "__main__":
    run()
