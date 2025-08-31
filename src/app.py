import os, sqlite3, pandas as pd, webbrowser, streamlit as st

DB = "db.sqlite"
st.set_page_config(page_title="Job Hunter", layout="wide")

@st.cache_data
def load_jobs():
    con = sqlite3.connect(DB)
    df = pd.read_sql("""
        SELECT id, title, company, location, url, posted_at, source
        FROM jobs
        ORDER BY posted_at DESC
    """, con)
    con.close()
    return df

df = load_jobs()
st.title("Jobs")
col1, col2, col3 = st.columns(3)
title_f = col1.text_input("Title contains")
company_f = col2.text_input("Company contains")
location_f = col3.text_input("Location contains")

mask = pd.Series([True]*len(df))
if title_f:   mask &= df["title"].str.contains(title_f, case=False, na=False)
if company_f: mask &= df["company"].str.contains(company_f, case=False, na=False)
if location_f:mask &= df["location"].str.contains(location_f, case=False, na=False)

st.caption(f"{mask.sum()} / {len(df)} jobs")
st.dataframe(df[mask], use_container_width=True, height=600)

sel = st.selectbox("Open job URL for…", df[mask]["title"] + " — " + df[mask]["company"])
if st.button("Open in browser"):
    row = df[mask][(df[mask]["title"] + " — " + df[mask]["company"]) == sel].iloc[0]
    webbrowser.open(row["url"])