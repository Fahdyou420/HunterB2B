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
    if request.method == 'POST':
        pass # Save logic here
    return render_template('settings.html', sectors=TARGET_SECTORS)

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
    threading.Thread(target=agent.scrape_job).start()
    return "Scraping started...", 200

@app.route('/api/action/trigger_outreach', methods=['POST'])
def trigger_outreach():
    threading.Thread(target=agent.outreach_job).start()
    return "Outreach started...", 200
