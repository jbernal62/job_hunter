import json, re, sqlite3, pandas as pd

DB="db.sqlite"; cfg=json.load(open("criteria.json","r",encoding="utf-8"))

def score(row):
    t=(row["title"] or "").lower(); d=(row["description"] or "").lower()
    loc=(row["location"] or "").lower()
    s=0
    if any(k.lower() in t for k in cfg["titles"]): s+=3
    s+=sum(1 for k in cfg["must_have"] if k.lower() in d)*2
    s+=sum(1 for k in cfg["nice_to_have"] if k.lower() in d)*1
    if any(x.lower() in loc for x in [l.lower() for l in cfg["locations"]]): s+=2
    if any(e.lower() in t for e in [x.lower() for x in cfg["exclude"]]): s-=5
    return s

def run(topn=40):
    con=sqlite3.connect(DB)
    df=pd.read_sql_query("SELECT * FROM jobs",con)
    if df.empty: 
        print("No jobs"); return
    df["score"]=df.apply(score,axis=1)
    df=df.sort_values("score",ascending=False).head(topn)
    df.to_csv("top_jobs.csv",index=False)
    con.close()
    print("Wrote top_jobs.csv")
if __name__=="__main__":
    run()
