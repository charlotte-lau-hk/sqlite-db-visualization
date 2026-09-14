#!/usr/bin/env python3
"""Check the exercise databases in db/ before publishing them.

Run it from the repository root:

    python3 tools/check-db.py            # check every db/*.db and the JSON index
    python3 tools/check-db.py some.db    # check one file anywhere on disk

It reports two kinds of finding:

  ERROR    something that will misbehave in the tool, in SQL Online, or both
  warning  something worth a second look, but legal

The exit status is 1 if any ERROR was reported, so it can be wired into a
pre-commit hook or CI.

Why these particular checks: the ER diagram in index.html is built *only* from
declared FOREIGN KEY constraints, and the PK/NN/UQ badges come only from the
schema - so a database without constraints draws as a set of isolated boxes.
See db/README.md and themes/README.md for the surrounding conventions.
"""

import json
import os
import shutil
import sqlite3
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT, 'db')
THEME_DIR = os.path.join(ROOT, 'themes')
SCHEMA_DIR = os.path.join(ROOT, 'schema')
INDEX = os.path.join(DB_DIR, 'database-list.json')

errors = []
warnings = []

def err(where, msg):
    errors.append('%s: %s' % (where, msg))
    print('  ERROR    %s' % msg)

def warn(where, msg):
    warnings.append('%s: %s' % (where, msg))
    print('  warning  %s' % msg)

def ok(msg):
    print('  ok       %s' % msg)


def check_database(path):
    name = os.path.basename(path)
    print('\n%s' % name)
    print('-' * len(name))

    with open(path, 'rb') as fh:
        if fh.read(16) != b'SQLite format 3\x00':
            err(name, 'not a SQLite 3 database file')
            return

    con = sqlite3.connect('file:%s?mode=ro' % path, uri=True)
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    views = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='view'")]

    if not tables:
        err(name, 'no tables - the tool will refuse it with "No valid tables found"')
        con.close()
        return
    ok('%d table(s): %s' % (len(tables), ', '.join(tables)))
    if views:
        warn(name, 'view(s) %s are ignored by the tool, which reads tables only'
             % ', '.join(views))

    pks, fk_lines, columns = {}, 0, {}
    for table in tables:
        info = list(con.execute('PRAGMA table_info("%s")' % table))
        columns[table] = [r[1] for r in info]
        pks[table] = [r[1] for r in sorted((r for r in info if r[5] > 0), key=lambda r: r[5])]
        if not pks[table]:
            err(name, '%s has no PRIMARY KEY - no PK badge, and entity integrity '
                      'cannot be shown' % table)
        # SQLite keeps a long-standing quirk: a PRIMARY KEY column accepts NULL
        # unless it is declared NOT NULL. The exception is a lone INTEGER
        # PRIMARY KEY, which is the rowid - a NULL there is auto-assigned.
        rowid_alias = len(pks[table]) == 1 and any(
            r[5] > 0 and (r[2] or '').upper() == 'INTEGER' for r in info)
        if not rowid_alias:
            for r in info:
                if r[5] > 0 and not r[3]:
                    warn(name, '%s.%s is part of the primary key but is not NOT NULL, '
                               'so SQLite would accept a NULL there' % (table, r[1]))
        for r in info:
            if not (r[2] or '').strip():
                warn(name, '%s.%s has no declared type; the diagram prints the type '
                           'inside each box' % (table, r[1]))
        fks = list(con.execute('PRAGMA foreign_key_list("%s")' % table))
        fk_lines += len(fks)
        # one FK per (id); a composite FK arrives as several rows sharing an id
        seen = {}
        for fk in fks:
            seen.setdefault(fk[0], []).append((fk[3], fk[2], fk[4]))
        for cols in seen.values():
            if len(cols) == 1 and cols[0][0] in pks[table] and len(pks[table]) > 1:
                pass  # single column of a composite key may legitimately be a FK
        # duplicate declarations: same column -> same table, declared twice
        pairs = [(c[0], c[1]) for c in
                 [(fk[3], fk[2]) for fk in fks]]
        for pair in set(pairs):
            if pairs.count(pair) > 1:
                err(name, '%s.%s -> %s is declared more than once; the diagram draws '
                          'one line per declaration' % (table, pair[0], pair[1]))

    if fk_lines == 0:
        warn(name, 'no FOREIGN KEY is declared anywhere - the ER diagram will be '
                   'isolated boxes with no relationships')
    else:
        ok('%d relationship line(s) will be drawn' % fk_lines)

    # Constraints that SQLite only rejects once enforcement is switched on.
    tmp = tempfile.mkdtemp()
    try:
        copy = os.path.join(tmp, name)
        shutil.copy(path, copy)
        rw = sqlite3.connect(copy)
        rw.execute('PRAGMA foreign_keys=ON')
        try:
            orphans = list(rw.execute('PRAGMA foreign_key_check'))
            for o in orphans:
                err(name, 'orphan row: %s rowid %s references missing %s' % (o[0], o[1], o[2]))
            if not orphans:
                ok('referential integrity clean (PRAGMA foreign_key_check)')
        except sqlite3.Error as exc:
            err(name, 'PRAGMA foreign_key_check fails: %s' % exc)
            err(name, 'a FOREIGN KEY points at columns that are not uniquely indexed - '
                      'a composite key must be referenced by ONE clause naming every '
                      'column, e.g. FOREIGN KEY (a, b) REFERENCES t(a, b)')
        for table in tables:
            try:
                rw.execute('BEGIN')
                rw.execute('DELETE FROM "%s" WHERE 0=1' % table)
                rw.execute('ROLLBACK')
            except sqlite3.Error as exc:
                err(name, 'writes to %s fail with foreign keys on: %s' % (table, exc))
                try:
                    rw.execute('ROLLBACK')
                except sqlite3.Error:
                    pass
        state = rw.execute('PRAGMA integrity_check').fetchone()[0]
        if state != 'ok':
            err(name, 'integrity_check: %s' % state)
        rw.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # Links the schema implies but never declares - the usual reason a diagram
    # comes out empty.
    for table in tables:
        declared = {fk[3] for fk in con.execute('PRAGMA foreign_key_list("%s")' % table)}
        for col in columns[table]:
            for other in tables:
                if other == table or not pks[other]:
                    continue
                if col.lower() == pks[other][0].lower() and col not in declared \
                        and col not in pks[table]:
                    warn(name, '%s.%s looks like a foreign key to %s.%s but none is '
                               'declared' % (table, col, other, pks[other][0]))

    # A key spelled two ways reads as two different columns.
    lowered = {}
    for table in tables:
        for col in columns[table]:
            lowered.setdefault(col.lower(), set()).add(col)
    for spellings in lowered.values():
        if len(spellings) > 1:
            warn(name, 'the same column name is spelled %s in different tables'
                 % ' / '.join(sorted(spellings)))

    con.close()


def check_schema_source(path):
    """schema/<name>.sql must rebuild exactly the database it stands for."""
    name = os.path.basename(path)
    stem = os.path.splitext(name)[0]
    source = os.path.join(SCHEMA_DIR, stem + '.sql')
    if not os.path.exists(source):
        warn(name, 'schema/%s.sql is missing - run tools/dump-schema.py' % stem)
        return
    tmp = tempfile.mkdtemp()
    try:
        rebuilt = sqlite3.connect(os.path.join(tmp, name))
        try:
            rebuilt.executescript(open(source, encoding='utf-8').read())
            rebuilt.commit()
        except sqlite3.Error as exc:
            err(name, 'schema/%s.sql does not load: %s' % (stem, exc))
            return
        original = sqlite3.connect('file:%s?mode=ro' % path, uri=True)
        want = sorted((n, sql) for n, sql in original.execute(
            'SELECT name, sql FROM sqlite_master WHERE sql IS NOT NULL'))
        got = sorted((n, sql) for n, sql in rebuilt.execute(
            'SELECT name, sql FROM sqlite_master WHERE sql IS NOT NULL'))
        if want != got:
            err(name, 'schema/%s.sql is out of step with the database - '
                      'run tools/dump-schema.py' % stem)
        else:
            tables = [r[0] for r in original.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            for table in tables:
                if sorted(original.execute('SELECT * FROM "%s"' % table)) != \
                        sorted(rebuilt.execute('SELECT * FROM "%s"' % table)):
                    err(name, 'schema/%s.sql rebuilds %s with different rows - '
                              'run tools/dump-schema.py' % (stem, table))
                    break
            else:
                ok('schema/%s.sql rebuilds it exactly' % stem)
        original.close()
        rebuilt.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_index():
    print('\n%s' % os.path.basename(INDEX))
    print('-' * len(os.path.basename(INDEX)))
    if not os.path.exists(INDEX):
        err('index', 'db/database-list.json is missing - the Samples list will be empty')
        return
    try:
        with open(INDEX, encoding='utf-8') as fh:
            entries = json.load(fh)
    except ValueError as exc:
        err('index', 'invalid JSON (%s) - the Samples list will be empty' % exc)
        return
    if not isinstance(entries, list):
        err('index', 'the file must hold a JSON array')
        return

    listed = set()
    for entry in entries:
        label = entry.get('name') or entry.get('filename') or '?'
        if not entry.get('name'):
            err('index', '%s has no "name"' % label)
        filename = entry.get('filename')
        if not filename:
            err('index', '%s has no "filename"' % label)
            continue
        listed.add(filename)
        if '/' in filename:
            err('index', '%s: "filename" is relative to db/, drop the path' % label)
        if not os.path.exists(os.path.join(DB_DIR, filename)):
            err('index', '%s points at db/%s, which does not exist' % (label, filename))
        if filename != filename.encode('ascii', 'replace').decode() or ' ' in filename:
            warn('index', '%s travels inside a URL; keep it ASCII and space-free' % filename)
        theme = entry.get('theme')
        if theme is None:
            warn('index', '%s has no "theme"; it will open in the default (frost)' % label)
        elif not os.path.exists(os.path.join(THEME_DIR, '%s.themes' % theme)):
            err('index', '%s uses theme "%s" but themes/%s.themes is missing'
                % (label, theme, theme))

    on_disk = {f for f in os.listdir(DB_DIR) if f.endswith(('.db', '.sqlite', '.sqlite3'))}
    for extra in sorted(on_disk - listed):
        warn('index', 'db/%s is not listed, so no one can open it' % extra)
    if not [e for e in errors if e.startswith('index:')]:
        ok('%d database(s) listed, all present' % len(listed))

    used = [e.get('theme') for e in entries if e.get('theme')]
    for theme in sorted(set(used)):
        if used.count(theme) > 1:
            warn('index', 'theme "%s" is used by %d databases, so they look identical'
                 % (theme, used.count(theme)))


def main():
    targets = sys.argv[1:]
    if targets:
        for path in targets:
            check_database(path)
            if os.path.dirname(os.path.abspath(path)) == DB_DIR:
                check_schema_source(path)
    else:
        files = sorted(f for f in os.listdir(DB_DIR)
                       if f.endswith(('.db', '.sqlite', '.sqlite3')))
        if not files:
            print('No databases found in %s' % DB_DIR)
            return 1
        for f in files:
            path = os.path.join(DB_DIR, f)
            check_database(path)
            check_schema_source(path)
        check_index()

    print('\n%s' % ('=' * 60))
    print('%d error(s), %d warning(s)' % (len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
