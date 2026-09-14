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

Things to watch for:

- It must be **valid JSON** — double quotes around every key and value, commas
  between objects, **no trailing comma** after the last one. A syntax error
  makes the whole list unreadable and the drop-down comes up empty (the browser
  console says why).
- Keep the file name free of spaces and non-ASCII characters; it travels inside
  a URL when a student clicks **Practice SQL**.
- An unknown `theme` value is ignored and the tool falls back to `frost`.
- Give two databases the same `theme` only if you do not mind them looking
  identical — the colour is what distinguishes them on screen.
- The file must actually be committed and pushed, or the drop-down entry will
  fail with "File not found" when chosen.

## What is in this folder

| Database | File | Theme | Tables | Notes |
| --- | --- | --- | --- | --- |
| Student Club DB v1 | `db2a-student_club_v1.db` | Green | Clubs, Students | One-to-many: each student joins at most one club. Starting point for normalisation. |
| Student Club DB v2 | `db2b-student_club_v2.db` | Aqua | Clubs, Students, ClubReg | Many-to-many resolved with the `ClubReg` link table (composite primary key). |
| Student Club DB v3 | `db2c-student_club_v3.db` | Noble | Club, ClubInfo, Student, ClubReg | Adds a school year to the registration, giving a three-column composite key. |
| Stationery Shop DB | `db3_stationery_shop.db` | Autumn | Category, Customer, Product, Orders, Order_Item | A small sales database: customers place orders, orders contain products. |

This table is documentation only — the tool reads `sample-database.json`, not
this README.
