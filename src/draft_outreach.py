import sqlite3, pandas as pd, jinja2

YOU = {"name": "Yeferson Bernal", "title": "Senior Cloud & AI Solutions Architect", "years": 12}

def run():
    con = sqlite3.connect("db.sqlite")
    jobs = pd.read_csv("top_jobs.csv").head(30)
    contacts = pd.read_sql_query("SELECT * FROM contacts", con)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"), autoescape=False)
    t_conn = env.get_template("connection_300c.j2")   # uses: first_name, you, job_title, company, location
    t_mail = env.get_template("inmail_long.j2")       # uses: name, you, job_title, company, location

    rows = []
    for _, j in jobs.iterrows():
        cts = contacts[contacts["job_id"] == j["id"]].head(3)
        if cts.empty:
            continue
        for _, c in cts.iterrows():
            first = (c.get("name") or "").split(" ")[0]
            conn = t_conn.render(
                first_name=first,
                company=j.get("company", ""),
                job_title=j.get("title", ""),
                location=j.get("location", ""),
                you=YOU,
            )
            mail = t_mail.render(
                name=c.get("name", ""),
                company=j.get("company", ""),
                job_title=j.get("title", ""),
                location=j.get("location", ""),
                you=YOU,
            )
            rows.append({
                "job_title": j.get("title",""),
                "company": j.get("company",""),
                "job_url": j.get("url",""),
                "contact_name": c.get("name",""),
                "contact_title": c.get("title",""),
                "profile": c.get("profile_url",""),
                "connection_note": conn[:300],
                "inmail": mail.strip(),
            })

    pd.DataFrame(rows).to_csv("outbox.csv", index=False)
    con.close()
    print(f"Drafted outreach for {len(rows)} contacts → outbox.csv")

if __name__ == "__main__":
    run()