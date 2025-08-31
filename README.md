# Job Hunter

A comprehensive job application management system that automates job discovery, ranking, and outreach for Solutions Architect roles. This tool helps streamline your job search by scraping job postings, scoring them against your criteria, and generating personalized outreach messages.

## Features

- **Multi-Source Job Ingestion**: Scrapes jobs from LinkedIn and ATS systems
- **Intelligent Job Ranking**: Scores jobs based on customizable criteria
- **People Matching**: Identifies key contacts at target companies
- **Automated Outreach**: Generates personalized connection and InMail templates
- **Web Interface**: Streamlit-based dashboard for job browsing and management
- **Data Export**: CSV export functionality for external analysis

## Project Structure

```
job_hunter/
├── src/
│   ├── app.py              # Streamlit web interface
│   ├── cli.py              # Command-line orchestration script
│   ├── config.py           # Configuration and path management
│   ├── ingest_linkedin.py  # LinkedIn job scraping
│   ├── ingest_ats.py       # ATS system job scraping
│   ├── rank.py             # Job scoring and ranking
│   ├── people_match.py     # Contact identification
│   ├── draft_outreach.py   # Outreach message generation
│   └── export_csv.py       # Data export utilities
├── templates/
│   ├── connection_300c.j2  # LinkedIn connection message template
│   └── inmail_long.j2      # LinkedIn InMail template
├── criteria.json           # Job scoring criteria configuration
├── db.sqlite              # SQLite database for job storage
└── .env                   # Environment variables (API tokens)
```

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jbernal62/job_hunter.git
   cd job_hunter
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas sqlite3 jinja2
   ```

3. **Configure environment variables**:
   Copy `.env.example` to `.env` and add your API tokens:
   ```
   APIFY_TOKEN=your_apify_token_here
   HOME_COUNTRY=Netherlands
   ```

4. **Customize job criteria**:
   Edit `criteria.json` to match your preferences:
   ```json
   {
     "titles": ["Solutions Architect", "AI Solutions Architect"],
     "must_have": ["Azure", "AWS", "MLOps"],
     "nice_to_have": ["Kubernetes", "Databricks"],
     "exclude": ["Intern", "Junior"],
     "locations": ["Netherlands", "Remote Europe"],
     "salary_min_eur": 90000
   }
   ```

## Usage

### Full Pipeline (Automated)

Run the complete job hunting pipeline:

```bash
python src/cli.py
```

This executes all steps in sequence:
1. Ingest jobs from LinkedIn
2. Ingest jobs from ATS systems
3. Rank jobs based on criteria
4. Match people at target companies
5. Draft personalized outreach messages

### Individual Components

**Web Interface**:
```bash
streamlit run src/app.py
```

**Job Ingestion**:
```bash
python src/ingest_linkedin.py
python src/ingest_ats.py
```

**Job Ranking**:
```bash
python src/rank.py
```

**Generate Outreach**:
```bash
python src/draft_outreach.py
```

### Outputs

- `top_jobs.csv`: Ranked list of best-matching jobs
- `outbox.csv`: Generated outreach messages ready to send
- Web interface: Interactive job browser and filtering

## Configuration

### Job Criteria (`criteria.json`)

- `titles`: Target job titles to prioritize
- `must_have`: Required skills/technologies (weighted heavily)
- `nice_to_have`: Preferred skills/technologies (bonus points)
- `exclude`: Keywords that disqualify jobs
- `locations`: Preferred work locations
- `salary_min_eur`: Minimum salary requirement
- `visa_sponsor_ok`: Whether visa sponsorship is acceptable
- `remote_first`: Preference for remote work

### Templates

Customize outreach messages in the `templates/` directory:
- `connection_300c.j2`: LinkedIn connection request (300 char limit)
- `inmail_long.j2`: Longer LinkedIn InMail template

## Database Schema

The SQLite database stores job information with the following structure:
- Job details (title, company, location, description, URL)
- Source information (LinkedIn, ATS)
- Timestamps and metadata
- Scoring results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for personal use in job searching and career development.

## Disclaimer

This tool is designed for legitimate job searching activities. Please respect the terms of service of job platforms and use responsibly. Always follow ethical scraping practices and rate limits.