from flask import Flask, render_template, request, jsonify
from database.sheets_client import sheets_client
from config.settings import TARGET_SECTORS
from scheduler.agent import agent
import threading

app = Flask(__name__)

@app.route('/')
def index():
    from config.settings import TARGET_SECTORS, TARGET_CITIES
    stats = sheets_client.get_stats()
    scheduler_status = agent.get_status()
    return render_template('index.html', stats=stats, scheduler_status=scheduler_status, target_sectors=TARGET_SECTORS, target_cities=TARGET_CITIES)

@app.route('/leads')
def leads():
    all_leads = list(sheets_client.get_all_leads(limit=50))
    all_leads.reverse() # Show newest first
    return render_template('leads.html', leads=all_leads)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    from config.settings import update_settings, OLLAMA_HOST, OLLAMA_MODEL, TARGET_SECTORS, TARGET_CITIES, TIMEZONE, SCRAPE_INTERVAL_HOURS, OUTREACH_DAILY_LIMIT
    
    success = False
    if request.method == 'POST':
        # Retrieve form data
        selected_sectors = request.form.getlist('sectors')
        custom_sectors_str = request.form.get('custom_sectors', '')
        if custom_sectors_str.strip():
            custom_sectors = [s.strip() for s in custom_sectors_str.split(',')]
            selected_sectors.extend(custom_sectors)

        selected_cities = request.form.getlist('cities')
        custom_cities_str = request.form.get('custom_cities', '')
        if custom_cities_str.strip():
            custom_cities = [s.strip() for s in custom_cities_str.split(',')]
            selected_cities.extend(custom_cities)
            
        ollama_host = request.form.get('ollama_host', '').strip()
        ollama_model = request.form.get('ollama_model', '').strip()
        
        timezone = request.form.get('timezone', '').strip()
        scrape_interval = request.form.get('scrape_interval', '').strip()
        outreach_limit = request.form.get('outreach_limit', '').strip()
        
        new_settings = {}
        if selected_sectors: new_settings['TARGET_SECTORS'] = selected_sectors
        if selected_cities: new_settings['TARGET_CITIES'] = selected_cities
        if ollama_host: new_settings['OLLAMA_HOST'] = ollama_host
        if ollama_model: new_settings['OLLAMA_MODEL'] = ollama_model
        if timezone: new_settings['TIMEZONE'] = timezone
        if scrape_interval: new_settings['SCRAPE_INTERVAL_HOURS'] = scrape_interval
        if outreach_limit: new_settings['OUTREACH_DAILY_LIMIT'] = outreach_limit
        
        update_settings(new_settings)
        agent.update_jobs()
        success = True

    # Build custom sectors string (those not in the default list)
    default_sectors = ['Banque', 'Industrie', 'Commerce', 'IT', 'Télécom', 'Assurance', 'Transport', 'Santé']
    current_custom_sectors = [s for s in TARGET_SECTORS if s not in default_sectors]
    custom_sectors_str = ", ".join(current_custom_sectors)

    default_cities = ['Tunis', 'Sfax', 'Sousse', 'Ariana', 'Bizerte', 'Nabeul', 'Monastir']
    current_custom_cities = [c for c in TARGET_CITIES if c not in default_cities]
    custom_cities_str = ", ".join(current_custom_cities)

    return render_template('settings.html', 
                            target_sectors=TARGET_SECTORS, 
                            custom_sectors=custom_sectors_str,
                            target_cities=TARGET_CITIES,
                            custom_cities=custom_cities_str,
                            ollama_host=OLLAMA_HOST,
                            ollama_model=OLLAMA_MODEL,
                            timezone=TIMEZONE,
                            scrape_interval=SCRAPE_INTERVAL_HOURS,
                            outreach_limit=OUTREACH_DAILY_LIMIT,
                            success=success)

@app.route('/api/stats')
def api_stats():
    stats = sheets_client.get_stats()
    return jsonify(stats)

@app.route('/api/stats-html')
def api_stats_html():
    stats = sheets_client.get_stats()
    return render_template('partials/stats.html', stats=stats)

@app.route('/api/action/pause', methods=['POST'])
def pause_scheduler():
    agent.pause()
    return render_template('partials/scheduler_header.html', scheduler_status=agent.get_status())

@app.route('/api/action/resume', methods=['POST'])
def resume_scheduler():
    agent.resume()
    return render_template('partials/scheduler_header.html', scheduler_status=agent.get_status())

@app.route('/api/scheduler_status')
def get_scheduler_status():
    return render_template('partials/scheduler_header.html', scheduler_status=agent.get_status())

@app.route('/api/action/trigger_scrape', methods=['POST'])
def trigger_scrape():
    from config.logger import logger
    
    sector = request.form.get('sector', 'IT')
    limit = int(request.form.get('limit', 10))
    source = request.form.get('source', 'both')
    city = request.form.get('city', 'Tunis')
    
    logger.info(f"Manual trigger: Scraping Layer | Source: {source} | Sector: {sector} | City: {city} | Limit: {limit}")
    
    def run_custom_scrape():
        if source in ['maps', 'both']:
            from scrapers.google_maps import google_maps_scraper
            google_maps_scraper.scrape_by_sector(sector, limit=limit, city=city)
        if source in ['linkedin', 'both']:
            from scrapers.linkedin_scraper import linkedin_scraper
            linkedin_scraper.scrape_decision_makers(sector, limit=limit, city=city)
            
    threading.Thread(target=run_custom_scrape).start()
    return jsonify({"success": True, "message": f"Scraping started for {sector} on {source}"}), 200

@app.route('/api/action/trigger_enrich', methods=['POST'])
def trigger_enrich():
    from config.logger import logger
    logger.info("Manual trigger: AI Enrichment Engine")
    from ai.enrichment_engine import enrichment_engine
    threading.Thread(target=enrichment_engine.process_pending_enrichment).start()
    return jsonify({"success": True, "message": "AI Enrichment started"}), 200

@app.route('/api/action/trigger_outreach', methods=['POST'])
def trigger_outreach():
    from config.logger import logger
    logger.info("Manual trigger: Outreach")
    threading.Thread(target=agent.outreach_job).start()
    return jsonify({"success": True, "message": "Outreach started"}), 200

@app.route('/api/action/check_ai', methods=['POST'])
def check_ai():
    from ai.ollama_client import ollama_client
    try:
        response = ollama_client.generate("Say 'AI is ready'", retries=1)
        if response:
            return jsonify({"success": True, "message": "Ollama connection successful!"}), 200
        else:
            return jsonify({"success": False, "message": "Connected but failed to generate text."}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Connection failed: {str(e)}"}), 500

@app.route('/api/n8n/scrape', methods=['POST'])
def n8n_scrape():
    # End point for N8N to trigger scrape and get results synchronously 
    from config.logger import logger
    
    data = request.json or {}
    sector = data.get('sector', 'IT')
    limit = int(data.get('limit', 5))
    source = data.get('source', 'maps') # maps, linkedin
    city = data.get('city', 'Tunis')
    
    logger.info(f"N8N sync trigger: Scrape {source} for {sector} in {city}")
    
    leads = []
    try:
        if source == 'maps':
            from scrapers.google_maps import google_maps_scraper
            leads = google_maps_scraper.scrape_by_sector(sector, limit=limit, sync_mode=True, city=city)
        elif source == 'linkedin':
            from scrapers.linkedin_scraper import linkedin_scraper
            leads = linkedin_scraper.scrape_decision_makers(sector, limit=limit, sync_mode=True, city=city)
            
        return jsonify({"success": True, "leads": leads}), 200
    except Exception as e:
        logger.error(f"N8N Scrape Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/n8n/enrich', methods=['POST'])
def n8n_enrich():
    from config.logger import logger
    from scrapers.web_enricher import web_enricher
    data = request.json or {}
    company = data.get("company", "")
    website = data.get("website", "")
    logger.info(f"N8N sync trigger: Enrich {company} ({website})")
    
    try:
        res = web_enricher.enrich_lead(company, website)
        return jsonify({"success": True, "data": res}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/n8n/ai_score', methods=['POST'])
def n8n_ai_score():
    from config.logger import logger
    from ai.lead_scorer import lead_scorer
    data = request.json or {}
    logger.info(f"N8N sync trigger: AI Score")
    try:
        score_res = lead_scorer.score_lead(data.get("lead", data))
        return jsonify({"success": True, "score": score_res}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/n8n/ai_message', methods=['POST'])
def n8n_ai_message():
    from config.logger import logger
    from ai.message_generator import message_generator
    data = request.json or {}
    logger.info(f"N8N sync trigger: AI Message")
    try:
        msg = message_generator.generate_outreach_message(data.get("lead", data))
        return jsonify({"success": True, "message": msg}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/logs')
def show_logs():
    return render_template('logs.html')

@app.route('/api/live_feed')
def live_feed():
    from config.logger import get_recent_logs
    logs = get_recent_logs(15)
    html_lines = []
    for line in logs.split('\n'):
        if not line.strip(): continue
        color = "#334155" # Default gray
        if "ERROR" in line:
            color = "#EF4444" # red
        elif "INFO" in line:
            color = "#0284C7" # blue
        
        escaped = line.strip().replace('<', '&lt;').replace('>', '&gt;')
        
        # if the step has an arrow, make it pop out
        if "-&gt;" in escaped or "->" in escaped:
            escaped = f"<strong>{escaped}</strong>"
            color = "#059669" # green
            
        html_lines.append(f"<div style='color: {color}; margin-bottom: 6px; font-family: monospace; font-size: 13px; border-bottom: 1px solid #F1F5F9; padding-bottom: 4px;'>{escaped}</div>")
        
    return "".join(html_lines)

@app.route('/api/logs_stream')
def logs_stream():
    from config.logger import get_recent_logs
    logs = get_recent_logs(100)
    return logs

