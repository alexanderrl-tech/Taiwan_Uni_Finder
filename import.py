import sqlite3
from datetime import date

import pandas as pd

EXCEL_FILE = "data/Programs_90860a.xlsx"     # the file downloaded from the site
DB_FILE = "sql/TwUni_Finder.db"     # or use a separate file, e.g. sql/universities.db

# Left side = column names in YOUR Excel file (edit these after checking them).
# Right side = database fields. Columns missing from the file are simply left empty.
COLUMN_MAP = {
    "School Name": "university",
    "Program Name": "program_name",
    "Field of Study": "field",
    "Level of Study": "level",
    "Scholarship": "scholarship",
    "region": "region",
    "Institution Type": "university_type",
    "Website": "website_url",
    "CONTACT": "contact",
}

df = pd.read_excel(EXCEL_FILE)
print("Columns found in the file:", list(df.columns))

df = df.rename(columns=COLUMN_MAP)

before = len(df)
df = df.dropna(subset=["university", "program_name"])
df["program_name"] = df["program_name"].astype(str).str.strip()
df = df[df["program_name"] != ""]
print(f"Skipped {before - len(df)} rows with no program name")
df = df.fillna("")

if (df["university"] == "").all() or (df["program_name"] == "").all():
    raise SystemExit("Edit COLUMN_MAP so it matches the column names printed above.")

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.executescript(open("sql/schema.sql", encoding="utf-8").read())

today = date.today().isoformat()

for row in df.itertuples(index=False):
    cur.execute("""
        INSERT INTO universities (name, type, region) VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            type = COALESCE(NULLIF(excluded.type, ''), type),
            region = COALESCE(NULLIF(excluded.region, ''), region)
    """, (row.university, row.university_type, row.region))

    uni_id = cur.execute(
        "SELECT id FROM universities WHERE name = ?", (row.university,)
    ).fetchone()[0]

    cur.execute("""
        INSERT INTO programs
            (university_id, program_name, field, levels, scholarship, website_url, contact, last_checked)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(university_id, program_name, levels) DO UPDATE SET
            field = excluded.field,
            website_url = excluded.website_url,
            last_checked = excluded.last_checked
    """, (uni_id, row.program_name, row.field, row.level,
          row.scholarship, row.website_url, row.contact, today))

conn.commit()
print("Universities:", cur.execute("SELECT COUNT(*) FROM universities").fetchone()[0])
print("Programs:", cur.execute("SELECT COUNT(*) FROM programs").fetchone()[0])
conn.close()