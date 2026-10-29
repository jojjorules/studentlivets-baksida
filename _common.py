"""Gemensamma hjälpfunktioner för alla sidor: data, färger, diagram och statistik."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from scipy import stats

DATA = Path(__file__).resolve().parent / "data" / "clean" / "students.csv"

# Färgtema – samma bruna/gröna palett som originalprojektet
BRUN = "#8B4A2F"      # deprimerade / riskfaktor
GRON = "#4A7C6F"      # ej deprimerade / skyddande
SAND = "#C4824C"
TEXT = "#4A3426"
BAKGRUND = "#F7F3EE"

pio.templates["studentliv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        paper_bgcolor="white",
        plot_bgcolor="white",
        colorway=[BRUN, GRON, SAND, "#2E5E52", "#D9A07A"],
        xaxis=dict(gridcolor="#EEE7DF", linecolor="#CBBBA9"),
        yaxis=dict(gridcolor="#EEE7DF", linecolor="#CBBBA9", zeroline=False),
        legend=dict(orientation="h", y=1.08, x=0),
        margin=dict(l=60, r=20, t=50, b=50),
    )
)
pio.templates.default = "studentliv"


def load() -> pd.DataFrame:
    """Läser den rengjorda filen (skapas av scripts/01_rengoring.py)."""
    df = pd.read_csv(DATA)
    ordning = ["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours"]
    df["sleepDuration"] = pd.Categorical(df["sleepDuration"], categories=ordning, ordered=True)
    return df


def tolka_r(r: float) -> str:
    """Samma tröskelvärden som i originalprojektet."""
    a = abs(r)
    if a < 0.1:
        return "Obetydlig"
    riktning = "positiv" if r > 0 else "negativ"
    if a < 0.2:
        return f"Svag ({riktning})"
    if a < 0.3:
        return f"Måttlig ({riktning})"
    return f"Stark ({riktning})"


def tolka_d(d: float) -> str:
    """Cohens d – effektstorlek enligt Cohens tumregler."""
    a = abs(d)
    if a < 0.2:
        return "Försumbar"
    if a < 0.5:
        return "Liten"
    if a < 0.8:
        return "Medel"
    return "Stor"


def cohens_d(a: pd.Series, b: pd.Series) -> float:
    a, b = a.dropna(), b.dropna()
    pooled = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / pooled


def p_text(p: float) -> str:
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def andel_per_grupp(df: pd.DataFrame, kolumn: str) -> pd.DataFrame:
    """Andel deprimerade per värde i en kolumn."""
    g = df.groupby(kolumn, observed=True)["depression"].agg(["count", "mean"]).reset_index()
    g["andel"] = g["count"] / g["count"].sum() * 100
    g["deprimerade"] = g["mean"] * 100
    g["ej_deprimerade"] = 100 - g["deprimerade"]
    return g.drop(columns="mean")


def stapel_andel(g: pd.DataFrame, kolumn: str, x_titel: str) -> go.Figure:
    """Staplat stapeldiagram: deprimerade vs ej deprimerade per grupp."""
    fig = go.Figure()
    fig.add_bar(x=g[kolumn].astype(str), y=g["deprimerade"], name="Deprimerade (%)", marker_color=BRUN,
                hovertemplate="%{x}: %{y:.1f} %<extra>Deprimerade</extra>")
    fig.add_bar(x=g[kolumn].astype(str), y=g["ej_deprimerade"], name="Ej deprimerade (%)", marker_color=GRON,
                hovertemplate="%{x}: %{y:.1f} %<extra>Ej deprimerade</extra>")
    fig.update_layout(barmode="stack", height=420, xaxis_title=x_titel, yaxis_title="Andel (%)",
                      yaxis_range=[0, 100], legend=dict(traceorder="normal", y=1.12),
                      margin=dict(t=70))
    return fig


def tabell(df: pd.DataFrame):
    """Visar en tabell i sidans stil (motsvarar tableFromData i mallen)."""
    from IPython.display import HTML
    def fmt(x):
        if isinstance(x, float):
            return f"{x:g}".replace(".", ",") if x.is_integer() else f"{x:.2f}".replace(".", ",")
        return x
    df = df.copy()
    for c in df.columns:
        df[c] = df[c].map(fmt)
    return HTML(df.to_html(index=False, classes="table table-sm", border=0, na_rep="–"))


def procent(x: float, dec: int = 1) -> str:
    return f"{x:.{dec}f} %".replace(".", ",")


__all__ = ["load", "tabell", "procent", "tolka_r", "tolka_d", "cohens_d", "p_text", "andel_per_grupp", "stapel_andel",
           "stats", "pd", "np", "go", "BRUN", "GRON", "SAND"]
