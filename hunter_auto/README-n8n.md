# 🚀 N8N Integration Guide

We've added N8N to the automation stack! This provides a visual workspace for orchestrating your scraping, enrichment, and outreach processes, giving you complete **visibility and control over the workflow**!

## 1. Starting N8N
N8N is now included in your `docker-compose.yml`. You can start the stack by running:
```bash
docker-compose up -d
```

Once started:
- **HunterAuto Dashboard** is still on `http://localhost:5000`
- **N8N Visual Editor** is running on `http://localhost:5678` 

*(Open N8N in your browser, set up your admin account when it first boots).*

## 2. Setting Up the N8N Workflow
To take advantage of your existing scrapers directly within N8N without breaking them, we have exposed a **Sync API** inside the Python backend.

You can now use simple **HTTP Request Nodes** inside N8N to trigger your scrapers and get data back:

### 📍 Scraping Node (HTTP Request)
- **Method:** `POST`
- **URL:** `http://hunter_auto:5000/api/n8n/scrape`
- **JSON Body:**
```json
{
  "source": "maps",  // or "linkedin"
  "sector": "IT", 
  "limit": 5
}
```
*This returns a list of scraped leads in JSON format.*

### 🧠 Enrichment Node (HTTP Request)
- **Method:** `POST`
- **URL:** `http://hunter_auto:5000/api/n8n/enrich`
- **JSON Body:**
```json
{
  "company": "{{$json.company}}",
  "website": "{{$json.website}}"
}
```

### 🤖 AI Scoring Node (HTTP Request)
- **Method:** `POST`
- **URL:** `http://hunter_auto:5000/api/n8n/ai_score`
- **JSON Body:**
```json
{
  "lead": {
    "company": "{{$json.company}}",
    "sector": "{{$json.sector}}"
  }
}
```

## 3. Recommended Workflow Order in N8N:
1. **Schedule Node**: Run every day at 9 AM.
2. **HTTP Request Node**: Scrape Maps (Output: list of JSON items).
3. **Item Lists Node**: Split the output list into individual items.
4. **Google Sheets Node (N8N Native)**: *Append Row* with your Lead properties.
5. **If Node (Condition)**: Check if Email exists.
6. **Gmail Node (N8N Native)**: Send the initial outreach email directly from N8N.
7. **Telegram Node (Optional)**: Send a notification to your phone!

### Why this is better?
- **Total Visibility**: You can see exactly which leads failed and why.
- **Visual Branching**: Easily drag-and-drop conditions (e.g. `If lead has phone -> Telegram`, `If lead has email -> Email`).
- **Sheets Remain**: You can natively connect your Google Account inside N8N directly and modify your Sheet with pure visual mapping.
- **No Proxy Required**: All the headless scraping runs inside the isolated `hunter_auto` container which bypasses the standard N8N execution limits, taking advantage of your existing Playwright configurations.
