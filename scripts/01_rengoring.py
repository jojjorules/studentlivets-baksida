"""
01_rengoring.py – rengör rådatan och sparar en analysklar CSV.

Kör från projektets rotmapp:
    python scripts/01_rengoring.py

In:  data/raw/student_depression_dataset.csv  (Kaggle, orörd)
Ut:  data/clean/students.csv                  (analysklar)
     data/clean/rengoringslogg.csv            (vad som ändrades och varför)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "student_depression_dataset.csv"
OUT = ROOT / "data" / "clean"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW)
log = []  # (steg, rader_påverkade, beskrivning)


def logga(steg, n, beskrivning):
    log.append({"steg": steg, "rader": int(n), "beskrivning": beskrivning})
    print(f"[{steg}] {n:>6} rader – {beskrivning}")


logga("Inläsning", len(df), "Rådata inläst från Kaggle-filen")

# 1. Kolumnnamn → engelska camelCase ---------------------------------------
df = df.rename(columns={
    "Gender": "gender",
    "Age": "age",
    "City": "city",
    "Profession": "profession",
    "Academic Pressure": "academicPressure",
    "Work Pressure": "workPressure",
    "CGPA": "cgpa",
    "Study Satisfaction": "studySatisfaction",
    "Job Satisfaction": "jobSatisfaction",
    "Sleep Duration": "sleepDuration",
    "Dietary Habits": "dietaryHabits",
    "Degree": "degree",
    "Have you ever had suicidal thoughts ?": "suicidalThoughts",
    "Work/Study Hours": "workStudyHours",
    "Financial Stress": "financialStress",
    "Family History of Mental Illness": "familyHistory",
    "Depression": "depression",
})
logga("Kolumnnamn", 0, "Bytte till camelCase utan mellanslag och frågetecken")

# 2. Ta bort inbakade citattecken ('5-6 hours' → 5-6 hours) ---------------
for col in ["sleepDuration", "profession", "city", "degree"]:
    n = df[col].astype(str).str.contains("'").sum()
    df[col] = df[col].astype(str).str.strip("'").str.strip()
    if n:
        logga("Citattecken", n, f"Tog bort inbakade citattecken i {col}")

# 3. Yes/No → 1/0 ---------------------------------------------------------
for col in ["suicidalThoughts", "familyHistory"]:
    df[col] = df[col].map({"Yes": 1, "No": 0}).astype("Int64")
logga("Binära fält", 0, "suicidalThoughts och familyHistory: Yes/No → 1/0")

# 4. Ogiltiga värden → saknas (NaN) ---------------------------------------
n = (df["financialStress"] == "?").sum()
df["financialStress"] = pd.to_numeric(df["financialStress"], errors="coerce")
logga("Saknade värden", n, "financialStress: '?' → saknas")

n = (df["sleepDuration"] == "Others").sum()
df.loc[df["sleepDuration"] == "Others", "sleepDuration"] = np.nan
logga("Saknade värden", n, "sleepDuration: 'Others' → saknas (går inte att tolka som timmar)")

n = (df["dietaryHabits"] == "Others").sum()
df.loc[df["dietaryHabits"] == "Others", "dietaryHabits"] = np.nan
logga("Saknade värden", n, "dietaryHabits: 'Others' → saknas")

n = (df["cgpa"] == 0).sum()
df.loc[df["cgpa"] == 0, "cgpa"] = np.nan
logga("Saknade värden", n, "cgpa = 0 är troligen felregistrerat → saknas")

# 5. Sömn: text → ordnad kategori + numeriskt mittvärde -------------------
somn_ordning = ["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours"]
df["sleepHours"] = df["sleepDuration"].map(
    {"Less than 5 hours": 4.0, "5-6 hours": 5.5, "7-8 hours": 7.5, "More than 8 hours": 9.0}
)
df["sleepDuration"] = pd.Categorical(df["sleepDuration"], categories=somn_ordning, ordered=True)
logga("Ny kolumn", df["sleepHours"].notna().sum(), "sleepHours: sömnkategori → mittvärde i timmar")

# 6. Ta bort kolumner utan variation --------------------------------------
for col in ["workPressure", "jobSatisfaction"]:
    andel_noll = (df[col] == 0).mean()
    logga("Borttagen kolumn", len(df), f"{col}: {andel_noll:.2%} nollor – ingen användbar variation")
df = df.drop(columns=["workPressure", "jobSatisfaction"])

# 7. Avgränsning: bara studenter ------------------------------------------
n = (df["profession"] != "Student").sum()
df = df[df["profession"] == "Student"].drop(columns=["profession"])
logga("Filtrering", n, "Tog bort rader där yrket inte är 'Student'")

# 8. Dubbletter -----------------------------------------------------------
n = df.duplicated("id").sum()
df = df.drop_duplicates("id")
logga("Dubbletter", n, "Kontroll av dubbla id")

logga("Resultat", len(df), "Rader i den analysklara filen")

df.to_csv(OUT / "students.csv", index=False)
pd.DataFrame(log).to_csv(OUT / "rengoringslogg.csv", index=False)
print(f"\nSparat: {OUT / 'students.csv'}")
