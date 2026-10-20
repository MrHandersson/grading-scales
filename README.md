# Grading scales by country (open dataset)

An open, sourced dataset of grading scales: grade bands, percentage cutoffs and grade points for the US, UK, India, Canada, Australia, Germany, France, the Netherlands, Spain, Italy, Sweden and the European ECTS scale. Available as **CSV** and **JSON** with a JSON Schema, plus a browsable site with a percent-to-grade converter.

- **Website:** https://mrhandersson.github.io/grading-scales/
- **CSV:** [`data/grading-scales.csv`](data/grading-scales.csv)
- **JSON:** [`data/grading-scales.json`](data/grading-scales.json)
- **Schema:** [`schema/grading-scales.schema.json`](schema/grading-scales.schema.json) (JSON Schema 2020-12)

Every row links to the public source it came from. No cutoff is invented: where a system has no fixed percentage cutoffs (German 1.0–5.0, CBSE positional grades, ECTS A–E, GCSE 9–1), the percent fields are `null`, and where a scale varies by institution the `notes` field says so.

## What's included

| Country / region | System(s) | Rows |
|---|---|---|
| United States | College letter grades, 4.0 GPA with plus/minus | 13 |
| United Kingdom | Undergraduate degree classes; taught master's; GCSE 9–1 (England) | 19 |
| India | University 10-point CGPA (UGC CBCS); CBSE Class X/XII positional grades | 17 |
| Canada | University of Toronto scale (example; no national scale) | 13 |
| Australia | UNSW grade bands (HD/DN/CR/PS/FL) | 5 |
| Germany | University 1.0–5.0; law degrees 0–18 points | 12 |
| France | Baccalauréat 0–20 and mentions | 7 |
| Netherlands | 1–10 scale (secondary and higher education) | 10 |
| Spain | University 0–10 (Real Decreto 1125/2003) | 5 |
| Italy | University exams 0–30; final degree 0–110 | 5 |
| Sweden | School grades A–F with merit points | 6 |
| Europe (ECTS) | ECTS grading scale A–E (relative, pre-2009) | 5 |

117 rows, 17 systems, 12 countries/regions.

## Schema

One row per grade band. The CSV and JSON contain the same rows in the same order.

| Field | Type | Meaning |
|---|---|---|
| `country` | string | Country or region (e.g. `United Kingdom`, `Europe (ECTS)`). |
| `system` | string | Grading system within the country. |
| `grade` | string | Grade label as written in the system (e.g. `B+`, `2:1`, `Notable (NT)`). |
| `min_percent` | number \| null | Lowest percentage in the band, **inclusive**. `null` if the system has no fixed percentage cutoffs. |
| `max_percent` | number \| null | Highest percentage in the band, **inclusive**. |
| `gpa_points` | number \| null | Grade points on the system's own scale: 4.0 GPA (US, Canada), 10-point CGPA (India), merit points (Sweden). `null` if not applicable. |
| `description` | string | Meaning of the grade, or its native score range for non-percentage systems (e.g. `9.0 to 10`). |
| `source_url` | string (https URI) | Primary public source for the row. |
| `notes` | string | Caveats, institutional variation and secondary sources. |

In the CSV, `null` is an empty cell. Percent bands are whole numbers with gaps between them (e.g. `90–92`, `93–100`); the converter on the site puts a mark in a gap (92.5) into the lower band, without rounding. Your institution may round differently.

## Usage

### JavaScript (browser or Node 18+)

```js
const url = "https://mrhandersson.github.io/grading-scales/data/grading-scales.json";
const rows = await (await fetch(url)).json();

function toGrade(country, system, percent) {
  return rows
    .filter(r => r.country === country && r.system === system && r.min_percent !== null)
    .sort((a, b) => b.min_percent - a.min_percent)
    .find(r => percent >= r.min_percent) ?? null;
}

const band = toGrade("Canada", "University of Toronto (example university scale)", 78);
console.log(band.grade, band.gpa_points); // B+ 3.3
```

### Python

```python
import csv, io, urllib.request

url = "https://mrhandersson.github.io/grading-scales/data/grading-scales.csv"
with urllib.request.urlopen(url) as f:
    rows = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")))

def to_grade(country, system, percent):
    bands = [r for r in rows if r["country"] == country and r["system"] == system and r["min_percent"]]
    bands.sort(key=lambda r: float(r["min_percent"]), reverse=True)
    return next((r for r in bands if percent >= float(r["min_percent"])), None)

print(to_grade("United Kingdom", "University undergraduate degree classification", 68)["grade"])
# Upper second-class honours (2:1)
```

With pandas: `pd.read_csv(url)`.

## Sources

| Country / system | Source |
|---|---|
| US letter grades and 4.0 GPA | Percent cutoffs: [Columbia University SPS](https://sps.columbia.edu/students/student-advising/academic-policies-procedures/grades) and [University of the Incarnate Word](https://my.uiw.edu/registrar/academics/grading-scale.html); grade points: [George Washington University](https://advising.columbian.gwu.edu/gpa-calculator); A+ conventions: [Arizona State](https://registrar.asu.edu/grades). Compiled in the [mygradecalculator.net GPA scale guide](https://mygradecalculator.net/gpa-scale). |
| UK degree classes, taught master's | [Prospects: understanding university grades in the UK](https://www.prospects.ac.uk/applying-for-university/university-life/understanding-university-grades-in-the-uk/) |
| UK GCSE 9–1 | [GOV.UK / Ofqual: GCSE 9 to 1 grade scale explained](https://www.gov.uk/government/publications/gcse-9-to-1-grade-scale-explained/gcse-9-to-1-grade-scale-explained) |
| India CGPA (CBCS) | [UGC guidelines for the Choice Based Credit System](https://www.ugc.gov.in/pdfnews/8023719_Guidelines-for-CBCS.pdf); common percentage cutoffs: [Leverage Edu](https://leverageedu.com/blog/grading-system-in-india/) |
| India CBSE X/XII | [CBSE: Grading System in CBSE for 10th & 12th](https://www.cbse.gov.in/cbsenew/correction/grading.pdf) |
| Canada | [University of Toronto Arts & Science Calendar: academic record](https://artsci.calendar.utoronto.ca/academic-record); [U of T registrar grading scales](https://www.registrar.utoronto.ca/records-academics/transcripts/grading-scales-notations/) |
| Australia | [UNSW guide to grades](https://www.unsw.edu.au/student/managing-your-studies/academic-life/grades-results-academic-standing/guide) |
| Germany | [Studying in Germany: German grading system](https://www.studying-in-germany.org/german-grading-system/) |
| France | [SIEC (Maison des examens): résultats du baccalauréat général](https://siec.education.fr/candidats/examens/BCG/resultats/resultats-12) |
| Netherlands | [Nuffic: grading systems in the Netherlands](https://www.nuffic.nl/en/education-systems/the-netherlands/grading-systems) |
| Spain | [BOE: Real Decreto 1125/2003, art. 5](https://www.boe.es/buscar/act.php?id=BOE-A-2003-17643) |
| Italy | [MUR: Study in Italy, evaluation scales](https://miur.mur.gov.it/studiare-in-italia/studying/index.html); [Politecnico di Torino](https://www.polito.it/en/education/applying-studying-graduating/studying-abroad/the-ects-system/the-grading-system) |
| Sweden | [Skolverket: betygsskalan](https://www.skolverket.se/prov-och-bedomning/betyg/betygsskalan); merit points: [Skolverket Utbildningsguiden](https://utbildningsguiden.skolverket.se/gymnasieskolan/gymnasievalet/rakna-ut-ditt-meritvarde) |
| ECTS | [ECTS Users' Guide 2009, European Commission (via EHEA)](https://ehea.info/media.ehea.info/file/ECTS_Guide/77/4/ects-guide_en_595774.pdf) |

The US, UK, India, Canada, Australia and Germany scales follow the [grading scales by country guide](https://mygradecalculator.net/grading-scales-by-country) on mygradecalculator.net, checked against the primary sources above. Sources were last checked on 2026-10-19.

**Important:** grading policies differ between schools and change over time. Use this dataset for comparison and tooling, and confirm with the institution for anything official. Credential evaluators use their own conversion tables.

## Calculators

Free calculators by [mygradecalculator.net](https://mygradecalculator.net/), no sign-up:

- [Grade calculator](https://mygradecalculator.net/): grade a test or assignment, with US, UK and India college scales built in
- [Final grade calculator](https://mygradecalculator.net/final-grade-calculator): the score you need on your final exam
- [Weighted grade calculator](https://mygradecalculator.net/weighted-grade-calculator): course grade from weighted categories
- [GPA calculator](https://mygradecalculator.net/gpa-calculator): credit-weighted GPA on the 4.0 scale

Guides: [grading scales by country](https://mygradecalculator.net/grading-scales-by-country), [GPA scale](https://mygradecalculator.net/gpa-scale), [how college grading works](https://mygradecalculator.net/college-grading-system), [grading on a curve](https://mygradecalculator.net/grading-on-a-curve).

## Repository layout

```
data/        canonical dataset (JSON is the source of truth; CSV is generated)
schema/      JSON Schema for the dataset
docs/        GitHub Pages site (served from /docs on main), with copies of the data
scripts/     build.py (JSON -> CSV, docs copies, pre-rendered tables), validate.py
tests/       converter test (Node + jsdom)
```

To change the data, edit `data/grading-scales.json`, then:

```sh
python3 scripts/build.py      # regenerate CSV, docs/data and docs/index.html
pip install jsonschema
python3 scripts/validate.py   # schema, CSV/JSON parity, band sanity, docs sync
```

Corrections are welcome: open an issue or pull request with a link to an official source.

## License

- **Data** (`data/`, `docs/data/`): [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DATA). Attribution: "Grading Scales Dataset by Martin Larsson, https://mrhandersson.github.io/grading-scales/".
- **Code** (scripts, site HTML/CSS/JS, schema): [MIT](LICENSE).

## Citation

> Larsson, M. (2026). *Grading Scales by Country* (Version 1.0.0) [Data set]. https://mrhandersson.github.io/grading-scales/

See also [`CITATION.cff`](CITATION.cff).
