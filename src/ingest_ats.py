import pandas as pd, sqlite3, requests, json

DB="db.sqlite"
ATS_ENDPOINTS=[
  "https://boards-api.greenhouse.io/v1/boards/microsoft/jobs",
  "https://boards-api.greenhouse.io/v1/boards/databricks/jobs",
  "https://api.ashbyhq.com/posting-api/job-board/company/openai"  # example
]

def ensure():
    con=sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS jobs
    (id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, url TEXT,
     description TEXT, source TEXT, posted_at TEXT, raw JSON)""")
    con.commit(); con.close()

def run():
    ensure()
    con=sqlite3.connect(DB)
    for url in ATS_ENDPOINTS:
        try:
            r=requests.get(url,timeout=20); r.raise_for_status()
            data=r.json()
            jobs = data.get("jobs") or data.get("data") or []
            for j in jobs:
                title = j.get("title") or j.get("text")
                company = url.split("/")[4]  # rough parse
                loc = (j.get("location") or {}).get("name") if isinstance(j.get("location"),dict) else j.get("location")
                link = j.get("absolute_url") or j.get("applyUrl") or j.get("jobUrl")
                desc = j.get("content") or j.get("description") or ""
                jid  = str(j.get("id") or link)
                con.execute("INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?)",
                            (jid,title,company,loc,link,desc,"ats",j.get("updated_at") or "", json.dumps(j)))
        except Exception as e:
            print("ATS fetch error", url, e)
    con.commit(); con.close()

if __name__=="__main__":
    run()
