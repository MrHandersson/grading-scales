#!/usr/bin/env python3
"""Regenerate data/grading-scales.csv from data/grading-scales.json, copy the data
and schema into docs/, and pre-render the tables in docs/index.html from
scripts/index.template.html. Standard library only; GitHub Pages serves the
committed output as-is (no build step on Pages)."""
import csv, datetime, html, json, pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIELDS = ["country", "system", "grade", "min_percent", "max_percent",
          "gpa_points", "description", "source_url", "notes"]


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return repr(v)
    return str(v)


UPDATED = "2026-10-19"
SITE = "https://mrhandersson.github.io/grading-scales/"

# Short context paragraphs shown above specific systems on the Pages site.
INTROS = {
    ("United States", "College letter grades (4.0 GPA, plus/minus)"):
        'Plus/minus grades sit 0.3 above or below the plain letter. Some schools use thirds '
        '(3.67, 3.33) or give an A+ 4.33; the <a href="https://mygradecalculator.net/gpa-scale">'
        'GPA scale guide</a> compares the conventions.',
}


def esc(v):
    return html.escape(str(v), quote=True)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def num(v):
    if v is None:
        return "&ndash;"
    return esc(int(v) if float(v).is_integer() else v)


def pct(r):
    lo, hi = r["min_percent"], r["max_percent"]
    if lo is None:
        return "&ndash;"
    return f"{num(lo)}&ndash;{num(hi)}%"


def render(rows):
    systems = {}
    for r in rows:
        systems.setdefault(r["country"], {}).setdefault(r["system"], []).append(r)
    toc = ["<ul>"]
    out = []
    for country, sysmap in systems.items():
        cid = slug(country)
        toc.append(f'<li><a href="#{cid}">{esc(country)}</a>: '
                   + ", ".join(f'<a href="#{slug(country + "-" + s)}">{esc(s)}</a>' for s in sysmap)
                   + "</li>")
        out.append(f'<article class="country" id="{cid}">\n<h2>{esc(country)}</h2>')
        for system, bands in sysmap.items():
            sid = slug(country + "-" + system)
            has_pct = any(b["min_percent"] is not None for b in bands)
            has_pts = any(b["gpa_points"] is not None for b in bands)
            out.append(f'<section class="system" id="{sid}">\n<h3>{esc(system)}</h3>')
            if (country, system) in INTROS:
                out.append(f"<p>{INTROS[(country, system)]}</p>")
            head = "<th scope=\"col\">Grade</th>"
            if has_pct:
                head += "<th scope=\"col\">Percent</th>"
            if has_pts:
                head += "<th scope=\"col\">Points</th>"
            head += "<th scope=\"col\">Description</th>"
            out.append(f'<div class="table-wrap"><table>\n<thead><tr>{head}</tr></thead>\n<tbody>')
            row_notes = []
            for b in bands:
                cells = f'<th scope="row">{esc(b["grade"])}</th>'
                if has_pct:
                    cells += f"<td>{pct(b)}</td>"
                if has_pts:
                    cells += f'<td>{num(b["gpa_points"])}</td>'
                cells += f'<td>{esc(b["description"])}</td>'
                out.append(f"<tr>{cells}</tr>")
            out.append("</tbody></table></div>")
            notes = []
            for b in bands:
                if b["notes"] and b["notes"] not in notes:
                    notes.append(b["notes"])
            srcs = []
            for b in bands:
                if b["source_url"] not in srcs:
                    srcs.append(b["source_url"])
            for n in notes:
                out.append(f'<p class="notes">{esc(n)}</p>')
            out.append('<p class="source">Source: ' + ", ".join(
                f'<a href="{esc(u)}">{esc(re.sub(r"^https://(www\.)?", "", u).split("/")[0])}</a>' for u in srcs) + "</p>")
            out.append("</section>")
        out.append("</article>")
    toc.append("</ul>")
    return "\n".join(toc), "\n".join(out), len(systems)


def jsonld(rows, n_countries):
    sources = sorted({r["source_url"] for r in rows})
    data = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Grading Scales by Country",
        "description": "Open, sourced dataset of grading scales by country: grade bands, percentage "
                       "cutoffs and grade points for the US, UK, India, Canada, Australia, Germany, "
                       "France, the Netherlands, Spain, Italy, Sweden and the ECTS scale.",
        "url": SITE,
        "sameAs": "https://github.com/MrHandersson/grading-scales",
        "keywords": ["grading scale", "grading system", "GPA", "letter grades", "grade conversion",
                     "education", "percentage to GPA", "international grades"],
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "isAccessibleForFree": True,
        "creator": {"@type": "Person", "name": "Martin Larsson", "url": "https://mygradecalculator.net/"},
        "publisher": {"@type": "Organization", "name": "My Grade Calculator", "url": "https://mygradecalculator.net/"},
        "dateModified": UPDATED,
        "version": "1.0.0",
        "inLanguage": "en",
        "variableMeasured": ["grade", "min_percent", "max_percent", "gpa_points"],
        "spatialCoverage": sorted({r["country"] for r in rows}),
        "isBasedOn": sources,
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE + "data/grading-scales.csv"},
            {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "data/grading-scales.json"},
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def build_html(rows):
    tpl = (ROOT / "scripts/index.template.html").read_text(encoding="utf-8")
    toc, tables, n = render(rows)
    page = (tpl.replace("<!-- TOC -->", toc).replace("<!-- TABLES -->", tables)
               .replace("<!-- COUNTRY_COUNT -->", str(n)).replace("<!-- UPDATED -->", UPDATED)
               .replace("<!-- JSONLD -->", jsonld(rows, n)))
    (ROOT / "docs/index.html").write_text(page, encoding="utf-8")


def main():
    rows = json.loads((ROOT / "data/grading-scales.json").read_text(encoding="utf-8"))
    with open(ROOT / "data/grading-scales.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(FIELDS)
        for r in rows:
            w.writerow([fmt(r[k]) for k in FIELDS])
    (ROOT / "docs/data").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/schema").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "data/grading-scales.json", ROOT / "docs/data/grading-scales.json")
    shutil.copyfile(ROOT / "data/grading-scales.csv", ROOT / "docs/data/grading-scales.csv")
    shutil.copyfile(ROOT / "schema/grading-scales.schema.json", ROOT / "docs/schema/grading-scales.schema.json")
    build_html(rows)
    print(f"wrote {len(rows)} rows, docs/index.html")


if __name__ == "__main__":
    main()
