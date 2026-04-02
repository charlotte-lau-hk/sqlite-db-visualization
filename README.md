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
- **Exercise Repository:** Load pre-configured sample databases directly from a `sample-database.json` file hosted in the repository.

## 💻 Technologies Used
- **SQL.js:** A port of SQLite to WebAssembly, allowing all database processing to happen locally and securely in the browser.
- **Mermaid.js:** A powerful JavaScript-based diagramming and charting tool that renders ER diagrams from text.
- **Tailwind CSS:** For a modern, responsive, and professional "Integrated Development Environment" (IDE) aesthetic.
- **HTML5/JavaScript:** For reactive UI state management and high-resolution canvas exports.

---

*Created by **Charlotte Lau** with **Gemini**.*
