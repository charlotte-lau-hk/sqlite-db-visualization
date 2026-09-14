# SQLite DB Visualization Tool

A professional web-based utility designed for ICT students and teachers to bridge the gap between SQLite implementation and conceptual database design. This tool provides instant visualization of database schemas, relational integrity analysis, and automated ER diagram generation.

## 🚀 Live Demo
Access the tool here: [https://charlotte-lau-hk.github.io/sqlite-db-visualization/](https://charlotte-lau-hk.github.io/sqlite-db-visualization/)

## 🎯 Purposes
- **HKDSE ICT Alignment:** Specifically built to support the HKDSE Information and Communication Technology curriculum, focusing on database management and relational logic.
- **Integrity Analysis:** Helps students visualize Entity Integrity (Primary Keys) and Referential Integrity (Foreign Keys), along with domain constraints (NOT NULL, UNIQUE).
- **Rapid Modeling:** Convert physical `.db` files into conceptual ER diagrams instantly.

## 🛠️ Key Functionalities
- **Integrated Dashboard:** A unified, one-piece interface for exploring table structures and viewing diagrams side-by-side.
- **Schema Explorer:** Drill down into specific tables to see field-level integrity badges (PK, FK, NN, UQ).
- **Vertical ER Diagrams:** Optimized for desktop PC usage with a Top-to-Bottom flow that matches relational hierarchy.
- **DSE Format Schema Text:** Automatically generates relational schema text in the format used in past DSE exam papers (Paper 1B / 2C).
- **Interactive Export:** Export diagrams as high-resolution PNG (1600px) or scalable SVG files for worksheets.
- **Mermaid Live Lab:** One-click integration with the official Mermaid Live Editor to help students learn and experiment with Mermaid DSL syntax.
- **Practice SQL Online:** One click hands the loaded database to [SQLite Online](https://sqliteonline.com/), which downloads it and opens a query tab with a starter `SELECT`, so students can write SQL against the very schema they are looking at.
- **A Colour per Exercise:** Each sample database carries a theme in `db/sample-database.json` — *Frost* (default), *Rosewater Elegance*, *Silver*, *Arctic Dawn*, *Aurora*, *Aqua*, *Autumn*, *Classic*, *Green*, *Noble* or *Sakura*. It re-colours the whole interface, including the ER diagram, and travels with the student: the *Practice SQL* link re-skins SQL Online to match. With no picker to fiddle with, the colour on a student's screen tells you which database they have open.
- **Exercise Repository:** Sample databases live in `db/`, listed in [`db/sample-database.json`](db/sample-database.json) and documented in [`db/README.md`](db/README.md).

## 📂 Repository Layout
```
index.html                   The whole tool - no build step, no dependencies to install
db/sample-database.json      The list of exercise databases, read by the tool (and their themes)
db/*.db                      The exercise databases themselves
db/README.md                 Documents that JSON file and what each database contains
schema/*.sql                 SQL source of each database - rebuilds it exactly
themes/*.themes              SQL Online skins, one per theme
themes/README.md             Documents the skin format and the link SQL Online expects
tools/check-db.py            Validates db/*.db and the JSON index before committing
tools/dump-schema.py         Regenerates schema/*.sql from db/*.db
```

### Adding an exercise database
1. Drop the `.db` file into `db/`.
2. Add a `{ "name": ..., "filename": ..., "theme": ... }` entry to `db/sample-database.json`.
3. `python3 tools/dump-schema.py && python3 tools/check-db.py`

See [`db/README.md`](db/README.md) for the details.

## 💻 Technologies Used
- **SQL.js:** A port of SQLite to WebAssembly, allowing all database processing to happen locally and securely in the browser.
- **Mermaid.js:** A powerful JavaScript-based diagramming and charting tool that renders ER diagrams from text.
- **Tailwind CSS:** For a modern, responsive, and professional "Integrated Development Environment" (IDE) aesthetic, with the theme palettes held in CSS custom properties.
- **SQLite Online:** The external SQL playground the *Practice SQL* button hands the database to, via its `#sqltext=` / `#url-sqlite=` link format, with `#urlcolor=` carrying the matching skin.
- **HTML5/JavaScript:** For reactive UI state management and high-resolution canvas exports.

---

*Created by **Charlotte Lau** with **Gemini**.*
