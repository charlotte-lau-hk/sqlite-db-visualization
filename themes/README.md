# Themes

Each theme in the tool has two halves:

| Half | Where it lives |
| --- | --- |
| The tool's own colours | CSS custom properties in `index.html` (`body[data-theme="…"]`) |
| The SQL Online colours | one `.themes` file in this folder |

`frost` is the default.

| Key | Name | Origin |
| --- | --- | --- |
| `frost` | Frost | built here |
| `rosewater` | Rosewater Elegance | built here |
| `silver` | Silver | built here |
| `arctic` | Arctic Dawn | built here |
| `aurora` | Aurora | built here — the one dark skin |
| `aqua` | Aqua | from [ylpss-mslau/sql_teaching](https://github.com/ylpss-mslau/sql_teaching) (`color-aqua.themes`) |
| `autumn` | Autumn | from sql_teaching (`color-autumn.themes`; `color.themes` there is an identical copy) |
| `classic` | Classic | from sql_teaching (`color-default.themes`) |
| `green` | Green | from sql_teaching (`color-green.themes`) |
| `noble` | Noble | from sql_teaching (`color-noble.themes`) |
| `sakura` | Sakura | from sql_teaching (`color-sakura.themes`) |

A theme is **pinned to a database** with the `theme` key in
`db/sample-database.json`, and that is the only way one is selected: choosing
that exercise switches both halves at once. There is no theme picker in the
interface, so the colour on screen always identifies the database. See
[`db/README.md`](../db/README.md).

### Readability pass

The imported skins were re-checked for contrast before being added, and the ones
built here were held to the same bar. The backgrounds and body text were already
fine; what needed work were the **code-editor colours**, which were pastel
accents on a near-white editor background — comments, strings and line numbers
sat at roughly 1.3:1 to 2.5:1, well under the 4.5:1 that small text needs, and
the same colours were reused for the Run icon and the object-tree glyphs.

Every foreground was darkened along its own hue until it cleared **4.5:1**
against the surface behind it (**3:1** for icon-sized marks: the Run triangle
and the tree logos). Hue and saturation were left alone, so each palette still
reads as itself — Sakura is still pink, Autumn still amber — but the SQL in the
editor is legible. Re-running that check is just a matter of comparing each
foreground key against the background named in the table below.

## How the SQL Online half works

[sqliteonline.com](https://sqliteonline.com/) reads directives out of its URL
hash. When a student clicks **Practice SQL**, the tool builds a link like:

```
https://sqliteonline.com/#sqltext=<url-encoded editor text>#urlcolor=https://charlotte-lau-hk.github.io/sqlite-db-visualization/themes/frost.themes
```

- `#sqltext=` carries the editor contents. A `#url-sqlite=<url>` line inside it
  tells SQL Online to download that database and open it as a connection.
- `#urlcolor=` points at one of the files in this folder. SQL Online fetches it,
  parses it as JSON, and sets each key as a CSS variable (`--bgc-d`, and so on).

Two details matter if you ever hand-write such a link:

1. **`#sqltext` must come first.** SQL Online URL-decodes the *entire* hash when
   it starts with `#urlcolor` or `#urldb`, which would tear an encoded
   `#sqltext` payload apart.
2. **The `.themes` URL is passed raw**, not URL-encoded, for the same reason.

## The file format

A `.themes` file is a single JSON object of 45 colour keys — the same format
SQL Online's own *Color* dialog exports with its **Save** button, so the easiest
way to build a new one is to tweak the colours there and save. The keys, in the
groups SQL Online itself uses:

| Group | Keys |
| --- | --- |
| Backgrounds | `bgc-c` panel, `bgc-d` main, `bgc-e` editor, `bgc-b` bottom bar, `bgc-a` placeholder, `bgc-z` dialog, `bgc-x` header shadow (a full CSS `box-shadow` value, not a colour) |
| Borders | `bgr-a`, `bgr-b` table cell hover, `bgr-e` error border |
| Fonts | `color-a` main, `color-b` table, `color-c` object/boolean, `color-d` number/function, `color-e` bottom and tooltips, `color-f` dialog bottom, `color-g` error, `color-h` the Run icon |
| Scrollbar | `sb-a` bar, `sb-b` track |
| Code editor | `cm-color`, `cm-keyword`, `cm-type`, `cm-atom`, `cm-property`, `cm-operator`, `cm-builtin`, `cm-number`, `cm-string`, `cm-variable`, `cm-variable-2`, `cm-comment`, `cm-selected`, `cm-bracket`, `cm-line` |
| Object tree | `menu-table`, `menu-column`, `menu-index`, `menu-trigger`, `menu-view`, `menu-key`, `menu-fun`, `menu-ct` |
| Hover | `hover-el-color`, `hover-el-bg` |

## Adding a theme

1. Add a `body[data-theme="<key>"]` block to the token section in `index.html`.
2. Add the key and its Mermaid line/fill colours to the `THEMES` object in the
   same file.
3. Save a `<key>.themes` file here. The name must match the key exactly, because
   the link is built as `themes/<key>.themes`.
   Then reference `<key>` from a database in `db/sample-database.json`.
4. Check the contrast of the new skin before committing it: every colour in the
   *Code editor* group against `bgc-e`, the *Fonts* group against `bgc-d` (or
   `bgc-c` for `color-a`), and the tree logos against `bgc-c`.

## Notes

- A skin loaded this way is **remembered by SQL Online** in the student's
  browser (it is stored as their "user" skin) and stays until another one is
  loaded. <https://sqliteonline.com/#clrcolor> resets it to the site default.
- SQL Online must be able to download the file, so these links only work from
  the published GitHub Pages site — not from `file://` or a local server. The
  tool detects that and skips the skin rather than sending a dead URL.
