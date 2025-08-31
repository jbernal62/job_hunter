# src/ingest_linkedin.py
import json, os, sqlite3
from urllib.parse import quote_plus
from apify_client import ApifyClient
from dotenv import load_dotenv
from tenacity import retry, wait_fixed, stop_after_attempt

DB = "db.sqlite"
ACTOR_ID = "curious_coder/linkedin-jobs-scraper"  # the actor you’re using which expects input.urls

def ensure_tables():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT, company TEXT, location TEXT, url TEXT,
        description TEXT, source TEXT, posted_at TEXT, raw JSON
    )""")
    con.commit(); con.close()

def build_search_urls(cfg):
    """Build LinkedIn job search URLs from criteria.json"""
    urls = []
    titles = cfg.get("titles", [])
    locs = cfg.get("locations", [])
    # optional filters you can tweak (LinkedIn query params)
    # f_WT=2 (remote), f_E=3,4,5 (senior/principal), sort by most recent
    exp_map = {"Intern":1, "Entry":2, "Associate":3, "Mid-Senior":4, "Director":5, "Executive":6, "Senior":4, "Principal":5}
    f_E = ",".join(str(exp_map.get(x, "")) for x in cfg.get("experience_level", []))
    remote = "2" if cfg.get("remote_first", False) else ""
    for t in titles:
        for loc in locs:
            url = (
                "https://www.linkedin.com/jobs/search/?"
                f"keywords={quote_plus(t)}"
                f"&location={quote_plus(loc)}"
                f"{'&f_WT=' + remote if remote else ''}"
                f"{'&f_E=' + f_E if f_E else ''}"
                "&sortBy=DD"
            )
            urls.append(url)
    # de-dup
    return sorted(set(urls))

@retry(wait=wait_fixed(3), stop=stop_after_attempt(3))
def run():
    load_dotenv()
    ensure_tables()
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    cfg = json.load(open("criteria.json","r",encoding="utf-8"))

    urls = build_search_urls(cfg)
    if not urls:
        raise RuntimeError("No search URLs built from criteria.json (check titles/locations).")

    # This actor expects 'urls' in its input
    input_payload = {
        "urls": urls,
        "maxItems": 200
    }

    run = client.actor(ACTOR_ID).call(run_input=input_payload)
    items = client.dataset(run["defaultDatasetId"]).list_items().items

    con = sqlite3.connect(DB)
    for it in items:
        jid = it.get("jobId") or it.get("id") or it.get("url")
        con.execute(
            "INSERT OR REPLACE INTO jobs (id,title,company,location,url,description,source,posted_at,raw) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                jid,
                it.get("title",""),
                it.get("company",""),
                it.get("location",""),
                it.get("url",""),
                it.get("description",""),
                "linkedin",
                it.get("postedAt",""),
                json.dumps(it, ensure_ascii=False)
            )
        )
    con.commit(); con.close()
    print(f"Ingested {len(items)} LinkedIn jobs from {len(urls)} searches")

if __name__ == "__main__":
    run()