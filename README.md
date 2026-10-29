# Studentlivets baksida – studentdepression analyserad i Python

Ett eget projekt där jag återskapar min kursanalys *Bakom betyget* (Statistik och dataanalys, TUC Yrkeshögskola) i Python. Målet är att komma så nära originalet som möjligt, fast med pandas, SciPy och Plotly i stället för kursens mall. Projektet är pågående. Just nu är första sidan publicerad.

Datan är ca 28 000 enkätsvar från [Student Depression Dataset (Kaggle)](https://www.kaggle.com/datasets/hopesb/student-depression-dataset).

**Live:** https://jojjorules.github.io/studentlivets-baksida/

## Vad projektet visar
**Publicerat nu**
- **Datarengöring med logg:** varje ändring i rådatan dokumenteras med antal rader och motivering.
- **Startsidan:** hur stor andel av studenterna som uppger depression, med ett interaktivt diagram (Plotly).

**Under arbete** (i `_utkast/`)
- **Beskrivande statistik:** andelar per grupp, till exempel sömntid.
- **Samband:** Pearson r med p-värde och tolkning av styrka.
- **Hypotesprövning:** Welch t-test med effektstorlek (Cohens d).

## Projektstruktur
```
data/raw/            Orörd rådata från Kaggle
data/clean/          Analysklar fil + rengöringslogg (skapas av skriptet)
scripts/             01_rengoring.py
_common.py           Gemensamma funktioner: färger, diagram, statistik
index.qmd            Startsidan (publicerad)
_utkast/             Fler sidor under arbete – byggs inte
_quarto.yml          Meny och inställningar
styles.scss          Färgtema
```

## Kör projektet
Kräver Python 3.10+ och [Quarto](https://quarto.org/docs/get-started/).

```bash
# 1. Installera paket
pip install -r requirements.txt

# 2. Rengör datan
python scripts/01_rengoring.py

# 3. Förhandsgranska sajten (uppdateras när du sparar)
quarto preview

# 4. Bygg den färdiga sajten till mappen docs/
quarto render
```

## Publicera
`quarto render` bygger sajten till mappen `docs/`, som GitHub Pages publicerar (Settings → Pages → Branch: main, mapp: /docs).

## Begränsningar
Alla samband är korrelationer i tvärsnittsdata och självrapporterade svar. De visar *att* saker hänger ihop, inte *varför*.

---
Johanna Markskog · Data Management-student, TUC Yrkeshögskola
