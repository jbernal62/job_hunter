import os, pandas as pd, sqlite3, json
from apify_client import ApifyClient
from dotenv import load_dotenv

DB="db.sqlite"

def ensure_tables():
    con=sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS contacts (
      key TEXT PRIMARY KEY,
      job_id TEXT, name TEXT, title TEXT, profile_url TEXT, company TEXT, raw JSON
    )"""); con.commit(); con.close()

def run():
    load_dotenv(); ensure_tables()
    client=ApifyClient(os.environ["APIFY_TOKEN"])
    jobs=pd.read_csv("top_jobs.csv").head(30)
    titles=["Recruiter","Talent Acquisition","Hiring Manager","Director","Head of Solutions Architecture","Engineering Manager"]
    for _,j in jobs.iterrows():
        company=j["company"]
        query=f'{company} ({ " OR ".join(titles) }) site:linkedin.com/in'
        # Actor example: "linkedin-people-scraper"
        run = client.actor("gdelpuppo/linkedin-people-scraper").call(run_input={"query": query, "maxResults": 10})
        people = client.dataset(run["defaultDatasetId"]).list_items().items
        con=sqlite3.connect(DB)
        for p in people:
            key=f'{j["id"]}:{p.get("profileUrl")}'
            con.execute("INSERT OR REPLACE INTO contacts VALUES (?,?,?,?,?,?,?)",
                (key, j["id"], p.get("name"), p.get("headline"), p.get("profileUrl"), company, json.dumps(p)))
        con.commit(); con.close()
    print("Contacts stored → table contacts")
if __name__=="__main__":
    run()
