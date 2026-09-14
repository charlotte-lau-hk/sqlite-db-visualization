# Sample Databases

This folder is the **exercise repository** for the
[SQLite DB Visualization tool](https://charlotte-lau-hk.github.io/sqlite-db-visualization/):
the `.db` files themselves, plus `sample-database.json`, which lists them.

## `sample-database.json`

The tool fetches this file on start-up and fills the **Samples** drop-down from
it. It is a JSON array of objects:

```json
[
  {
    "name": "Student Club DB v1",
    "filename": "db2a-student_club_v1.db",
    "theme": "green"
  },
  {
    "name": "Stationery Shop DB",
    "filename": "db3_stationery_shop.db",
    "theme": "autumn"
  }
]
```

| Key | Required | Meaning |
| --- | --- | --- |
| `name` | yes | The label shown in the drop-down. Any text; keep it short enough to read in the header. |
| `filename` | yes | The file name **relative to this `db/` folder**. No leading `db/`, no path. |
| `theme` | no | Colour theme to switch to when this database is chosen — for the tool *and* for SQL Online. One of the keys in [`themes/`](../themes/README.md): `frost`, `rosewater`, `silver`, `arctic`, `aurora`, `aqua`, `autumn`, `classic`, `green`, `noble`, `sakura`. |

The order of the array is the order of the drop-down.

### About `theme`

This is the **only** way a theme is chosen — the tool has no theme picker. Each
exercise therefore carries its own colour, so a glance across the room tells you
who is on which database, and you can say "open the green one" in class.

Leave the key out (or give an unknown value) and that database opens in `frost`,
the default. A database the student loads from their own disk with **Load File**
also falls back to `frost`, so an exercise colour never lingers on something that
is not that exercise.

## Adding an exercise database

1. Put the `.db` file in this folder.
2. Add an object to the array in `sample-database.json`.
3. Add a row to the table below, so the folder documents itself.
4. Run `python3 tools/dump-schema.py` to write its SQL source to `schema/`,
   and commit that alongside the database.
5. Run `python3 tools/check-db.py` from the repository root before committing.
   It reads every database here and this JSON file, and reports anything that
   would misbehave in the tool: a table with no primary key, a schema with no
   foreign keys (the ER diagram would be isolated boxes), a broken or duplicated
   foreign key, orphan rows, a listed file that is missing, a theme that does
   not exist. It exits non-zero when it finds an error.

Things to watch for:

- It must be **valid JSON** — double quotes around every key and value, commas
  between objects, **no trailing comma** after the last one. A syntax error
  makes the whole list unreadable and the drop-down comes up empty (the browser
  console says why).
- Keep the file name free of spaces and non-ASCII characters; it travels inside
  a URL when a student clicks **Practice SQL**.
- An unknown `theme` value is ignored and the tool falls back to `frost`
  (`tools/check-db.py` reports it as an error).
- Give two databases the same `theme` only if you do not mind them looking
  identical — the colour is what distinguishes them on screen.
- The file must actually be committed and pushed, or the drop-down entry will
  fail with "File not found" when chosen.

## What is in this folder

| Database | File | Theme | Tables | Notes |
| --- | --- | --- | --- | --- |
| Student Club DB v1 (2 tables) | `db2a-student_club_v1.db` | Green | Clubs, Students | One-to-many: each student joins at most one club. Starting point for normalisation. |
| Student Club DB v2 (3 tables) | `db2b-student_club_v2.db` | Aqua | Clubs, Students, ClubReg | Many-to-many resolved with the `ClubReg` link table, whose primary key is the pair `(SID, CID)`. |
| Student Club DB v3 (4 tables) | `db2c-student_club_v3.db` | Noble | Club, ClubInfo, Student, ClubReg | Adds a school year to the registration, giving a three-column composite key. Also carries a `ClubRecord` view (the tool shows tables only). |
| Stationery Shop DB | `db3_stationery_shop.db` | Autumn | Category, Customer, Product, Orders, Order_Item | A small sales database: customers place orders, orders contain products. |
| Book Loan DB (4 tables) | `db4-book_loan.db` | Classic | READER, BOOK, BKCOPY, LOAN | A library: a title (`BOOK`) has physical copies (`BKCOPY`), and a loan is a copy borrowed by a reader on a date. Composite primary key on `LOAN`, 8 of the 12 loans still open. |

This table is documentation only — the tool reads `sample-database.json`, not
this README.

## How these files are built

Every database here has its SQL source in [`schema/`](../schema), written by
`tools/dump-schema.py` - the `CREATE` statements followed by the rows as
`INSERT`s, so the file rebuilds the database exactly:

```bash
sqlite3 db/db2b-student_club_v2.db < schema/db2b-student_club_v2.sql
python3 tools/check-db.py
```

That text is what makes a change reviewable: a diff of the `.sql` shows which
constraint moved, where a diff of the `.db` shows only that some bytes changed.
Edit the SQL, rebuild, check - or edit the database and re-run
`tools/dump-schema.py` to bring the SQL back in step. `tools/check-db.py`
rebuilds each database from its `.sql` and compares, so the two cannot drift
apart unnoticed.

### Two conventions these files follow

**`PRAGMA foreign_keys = ON;` at the top, before `BEGIN TRANSACTION`.** SQLite
does not enforce foreign keys unless a connection asks for it, and the pragma
is *ignored inside a transaction* - so the line has to come first, and the
tables are written parents before children so the rows load under enforcement.
The setting lives in the connection, never in the `.db` file: whatever opens
the database afterwards decides for itself, which is why the file is loaded
with foreign keys on again in `tools/check-db.py`.

**`NOT NULL` on every primary-key column.** SQLite keeps a long-standing quirk:
a `PRIMARY KEY` column still accepts `NULL` unless it is declared `NOT NULL`,
which would quietly contradict the entity integrity the exercise is teaching.
The one exception is a lone `INTEGER PRIMARY KEY` - that column *is* the rowid,
a `NULL` inserted there is replaced by the next number, and declaring it
`NOT NULL` would only break that. `Category.Category_ID` in the stationery shop
database is the single case; `tools/check-db.py` knows to skip it and warns
about every other nullable key column.

Write the `CREATE TABLE` statements by hand, with table-level `FOREIGN KEY`
clauses. A composite foreign key must be **one** clause naming every column:

```sql
CREATE TABLE ClubReg (
  CID   CHAR(4),
  Syear INT,
  SID   CHAR(4),
  PRIMARY KEY (CID, Syear, SID),
  FOREIGN KEY (CID, Syear) REFERENCES ClubInfo(CID, Syear),
  FOREIGN KEY (SID)        REFERENCES Student(SID)
);
```

Graphical editors are fine for typing in data, but their table designers tend to
write a column-level `REFERENCES` next to each column *in addition* to the
clause you wrote. When one of those points at a single column of a composite
key, SQLite rejects every later write with `foreign key mismatch`, and the ER
diagram grows duplicate lines. Re-run `tools/check-db.py` after any save from a
GUI - that is exactly the fault it was written to catch.
