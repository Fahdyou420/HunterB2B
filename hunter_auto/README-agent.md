# Hunter Auto 1.0 (AI Smart Agent)

The system has been transformed into an autonomous **AI Smart Agent** tailored precisely for Human Cold Calling. 

Instead of arbitrarily sending emails or messages, the proxy-free automation stack now behaves as your personal SDR (Sales Development Representative) that researches, scores, and prepares a daily queue of high-intent leads for you to dial.

## Workflow Overview

1. **Scraping Layer (Continuous)**
   - Autonomously researches target sectors on Google Maps and LinkedIn.
   - Extracts raw target company data and decision makers.
   - Appends to Google Sheets as `pending_enrichment`.

2. **Local AI Layer (Enrichment & Scoring)**
   - Pings companies' websites using headless Playwright to locate Phone Numbers & Emails.
   - Passes data to **Ollama AI** to score the lead (0 to 10) based on firmographics.
   - Marks leads as `pending` alongside their AI rationale.

3. **Cold Call Matchmaker (The "Outreach" Engine)**
   - Evaluates fully enriched leads.
   - If a Phone Number is found AND AI Score >= 7: Marks as `cold_call_queue` (High Priority).
   - If a Phone Number is found BUT Score < 7: Marks as `secondarycallqueue`.
   - If NO Phone Number is found: Marks as `skipped` (cannot be cold called).

## The Dashboard View
All of these can be managed autonomously or triggered manually via `http://localhost:5000`.
- The **Stats view** now dynamically shows "Total Leads", "High Score (7+)", "Ready to Call", and "Skipped".
- The **Leads view** now clearly lists Phone Numbers, Contact Names, and the AI Score logic side-by-side!

### How to use?
You can view your leads on `http://localhost:5000/leads` or just open the attached Google Sheet, filter by `Status: cold_call_queue`, pick up the phone, and start dialing!
