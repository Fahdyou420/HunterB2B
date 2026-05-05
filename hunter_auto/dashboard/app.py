from flask import Flask, render_template, request, jsonify
from database.sheets_client import sheets_client
from config.settings import TARGET_SECTORS
from scheduler.agent import agent
import threading

app = Flask(__name__)

@app.route('/')
def index():
    stats = sheets_client.get_stats()
    scheduler_status = agent.get_status()
    return render_template('index.html', stats=stats, scheduler_status=scheduler_status)

@app.route('/leads')
def leads():
    all_leads = list(sheets_client.get_all_leads(limit=50))
    all_leads.reverse() # Show newest first
    return render_template('leads.html', leads=all_leads)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    from config.settings import update_settings, OLLAMA_HOST, OLLAMA_MODEL, TARGET_SECTORS, TIMEZONE, SCRAPE_INTERVAL_HOURS, OUTREACH_DAILY_LIMIT
    
    success = False
    if request.method == 'POST':
        # Retrieve form data
        selected_sectors = request.form.getlist('sectors')
        custom_sectors_str = request.form.get('custom_sectors', '')
        if custom_sectors_str.strip():
            custom_sectors = [s.strip() for s in custom_sectors_str.split(',')]
            selected_sectors.extend(custom_sectors)
            
        ollama_host = request.form.get('ollama_host', '').strip()
        ollama_model = request.form.get('ollama_model', '').strip()
        
        timezone = request.form.get('timezone', '').strip()
        scrape_interval = request.form.get('scrape_interval', '').strip()
        outreach_limit = request.form.get('outreach_limit', '').strip()
        
        new_settings = {}
        if selected_sectors: new_settings['TARGET_SECTORS'] = selected_sectors
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

    return render_template('settings.html', 
                            target_sectors=TARGET_SECTORS, 
                            custom_sectors=custom_sectors_str,
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
    return render_template('partials/controls.html', scheduler_status=agent.get_status())

@app.route('/api/action/resume', methods=['POST'])
def resume_scheduler():
    agent.resume()
    return render_template('partials/controls.html', scheduler_status=agent.get_status())

@app.route('/api/action/trigger_scrape', methods=['POST'])
def trigger_scrape():
    from config.logger import logger
    logger.info("Manual trigger: Scraping Layer (Maps & LinkedIn)")
    threading.Thread(target=agent.scrape_job).start()
    return jsonify({"success": True, "message": "Scraping Layer started"}), 200

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

@app.route('/logs')
def show_logs():
    return render_template('logs.html')

@app.route('/api/logs_stream')
def logs_stream():
    from config.logger import get_recent_logs
    logs = get_recent_logs(100)
    return logs

