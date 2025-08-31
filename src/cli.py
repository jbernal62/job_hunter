import os, subprocess
steps=[
 ("Ingest LinkedIn", "python src/ingest_linkedin.py"),
 ("Ingest ATS", "python src/ingest_ats.py"),
 ("Rank", "python src/rank.py"),
 ("Match people", "python src/people_match.py"),
 ("Draft outreach", "python src/draft_outreach.py")
]
for name,cmd in steps:
    print(f"== {name} =="); code=os.system(cmd); 
    if code!=0: print("Step failed:", name); break
print("Done → check top_jobs.csv and outbox.csv")
