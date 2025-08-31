# src/export_csv.py
import argparse, json, sqlite3, sys
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "db.sqlite"

def coalesce(*vals):
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def from_raw(raw):
    try:
        return json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        return {}

def extract_url(raw_json, existing=None):
    r = from_raw(raw_json)
    return coalesce(existing, r.get("url"), r.get("jobUrl"), r.get("applyUrl"), r.get("linkedinUrl"))

def extract_company(raw_json, existing=None):
    r = from_raw(raw_json)
    return coalesce(existing, r.get("company"), r.get("companyName"), r.get("company_label"), r.get("company_link_text"))

def is_http_url(u: str) -> bool:
    if not isinstance(u, str) or not u.strip():
        return False
    p = urlparse(u.strip())
    return p.scheme in ("http", "https") and bool(p.netloc)

def export_jobs(out_csv: Path, out_xlsx: Path, with_description=False,
                filter_title=None, filter_company=None, filter_location=None):
    cols = "id, title, company, location, url, posted_at, source, raw"
    if with_description:
        cols += ", description"

    where = []
    params = {}
    if filter_title:
        where.append("LOWER(title) LIKE :t"); params["t"] = f"%{filter_title.lower()}%"
    if filter_company:
        where.append("LOWER(company) LIKE :c"); params["c"] = f"%{filter_company.lower()}%"
    if filter_location:
        where.append("LOWER(location) LIKE :l"); params["l"] = f"%{filter_location.lower()}%"
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
      SELECT {cols}
      FROM jobs
      {where_sql}
      ORDER BY COALESCE(posted_at,'') DESC, company, title
    """

    con = sqlite3.connect(DB_PATH.as_posix())
    try:
        df = pd.read_sql(sql, con, params=params)
    finally:
        con.close()

    # Backfill URL & company from raw JSON
    df["url"] = df.apply(lambda r: extract_url(r.get("raw"), r.get("url")), axis=1)
    df["company"] = df.apply(lambda r: extract_company(r.get("raw"), r.get("company")), axis=1)

    # Clean output columns
    out_cols = ["id", "title", "company", "location", "url", "posted_at", "source"]
    if with_description:
        out_cols.append("description")
    out = df[out_cols].copy()

    # --- CSV (Excel will usually auto-link http/https)
    out.to_csv(out_csv.as_posix(), index=False, encoding="utf-8-sig")
    print(f"Wrote {out_csv} with {len(out)} rows")

    # --- XLSX with real hyperlinks where valid
    try:
        import xlsxwriter  # noqa: F401
    except ImportError:
        print("xlsxwriter not installed; skipping XLSX export. Run: pip install xlsxwriter", file=sys.stderr)
        return

    # Build a short display label for the link column
    out["Job Link"] = out["title"].fillna("").str.slice(0, 60)

    # Reorder to put clickable text next to URL
    excel_cols = ["id", "title", "company", "location", "posted_at", "source", "Job Link", "url"]
    if with_description:
        excel_cols.append("description")

    with pd.ExcelWriter(out_xlsx, engine="xlsxwriter") as writer:
        out[excel_cols].to_excel(writer, index=False, sheet_name="jobs")
        ws = writer.sheets["jobs"]

        # Column widths
        ws.set_column("A:A", 16)  # id
        ws.set_column("B:B", 48)  # title
        ws.set_column("C:C", 28)  # company
        ws.set_column("D:D", 28)  # location
        ws.set_column("E:E", 20)  # posted_at
        ws.set_column("F:F", 10)  # source
        ws.set_column("G:G", 40)  # Job Link (clickable text)
        ws.set_column("H:H", 80)  # url (full)
        if with_description:
            # Description can be huge; adjust as you like
            ws.set_column("I:I", 100)

        # Write hyperlinks safely: only if valid http(s); otherwise write plain text.
        # Data starts on row 2 in Excel (row 1 is headers).
        for i in range(1, len(out) + 1):
            link_text = out.iloc[i-1]["Job Link"] or "Open"
            url_val = out.iloc[i-1]["url"]
            link_cell = f"G{i+1}"
            if is_http_url(url_val):
                ws.write_url(link_cell, url_val, string=link_text)
            else:
                # Fallback: write plain text if URL is missing/invalid
                ws.write_string(link_cell, link_text)

    print(f"Wrote {out_xlsx} with clickable links where available")

def export_contacts(out_csv: Path):
    con = sqlite3.connect(DB_PATH.as_posix())
    try:
        cdf = pd.read_sql("""
          SELECT job_id, name, title, company, profile_url
          FROM contacts
          ORDER BY company, name
        """, con)
    finally:
        con.close()
    cdf.to_csv(out_csv.as_posix(), index=False, encoding="utf-8-sig")
    print(f"Wrote {out_csv} with {len(cdf)} rows")

def main():
    p = argparse.ArgumentParser(description="Export job-hunter data to CSV/XLSX.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pj = sub.add_parser("jobs", help="Export jobs")
    pj.add_argument("--out", default=str(Path.cwd() / "jobs_all.csv"))
    pj.add_argument("--xlsx", default=str(Path.cwd() / "jobs_all.xlsx"))
    pj.add_argument("--with-description", action="store_true")
    pj.add_argument("--title")
    pj.add_argument("--company")
    pj.add_argument("--location")

    pc = sub.add_parser("contacts", help="Export contacts")
    pc.add_argument("--out", default=str(Path.cwd() / "contacts_all.csv"))

    args = p.parse_args()
    if args.cmd == "jobs":
        export_jobs(Path(args.out), Path(args.xlsx), args.with_description,
                    args.title, args.company, args.location)
    elif args.cmd == "contacts":
        export_contacts(Path(args.out))

if __name__ == "__main__":
    main()
