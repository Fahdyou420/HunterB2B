from scheduler.agent import agent
from dashboard.app import app
import sys
import os

# Create an empty __init__.py in all subfolders to make them python modules
for folder in ["config", "scrapers", "ai", "outreach", "database", "scheduler", "dashboard"]:
    init_file = os.path.join(os.path.dirname(__file__), folder, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            pass

if __name__ == '__main__':
    print("Starting Hunter Auto 1.0...")
    agent.start()
    try:
        from waitress import serve
        print("Running with Waitress WSGI server on port 5000...")
        serve(app, host="0.0.0.0", port=5000)
    except ImportError:
        print("Waitress not found. Please install it using: pip install waitress")
        print("Falling back to standard Flask dev server...")
        app.run(host="0.0.0.0", port=5000)
