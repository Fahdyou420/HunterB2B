import sys
sys.path.append('.')
from database.sheets_client import sheets_client

try:
    print("Trying get_all_leads:")
    leads = sheets_client.get_all_leads()
    print("Leads:", len(leads))
    if len(leads) > 0:
        print("First lead:", leads[0])
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    records = sheets_client.leads_ws.get_all_records() if sheets_client.leads_ws else []
    print("Records count:", len(records))
except Exception as e:
    import traceback
    traceback.print_exc()
