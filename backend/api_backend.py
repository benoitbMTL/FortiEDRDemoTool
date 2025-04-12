import os
import json
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
from dotenv import load_dotenv
import fortiedr

load_dotenv()

DEFAULT_API_URL = os.getenv("API_URL") or ""
DEFAULT_API_USERNAME = os.getenv("API_USERNAME") or ""
DEFAULT_API_PASSWORD = os.getenv("API_PASSWORD") or ""
DEFAULT_API_ORG = os.getenv("API_ORG") or ""

def test_api_authentication(url, username, password, organization):
    try:
        authentication = fortiedr.auth(
            user=username,
            passw=password,
            host=url.replace("https://", "").split("/")[0],
            org=organization
        )

        if not authentication["status"]:
            return {"status": False, "data": authentication["data"]}

        admin = fortiedr.Administrator()
        system_info = admin.list_system_summary(organization=organization)

        return {
            "status": True,
            "data": system_info["data"]
        }

    except Exception as e:
        return {"status": False, "data": str(e)}

def save_api_settings(self):
    self.api_settings = {
        "url": self.url_entry.get(),
        "username": self.username_entry.get(),
        "password": self.password_entry.get(),
        "organization": self.org_entry.get()
    }

def run_event_query(output_format="Table", items="1", action="All", time_range="1 hour"):
    auth = fortiedr.auth(
        user=os.getenv("API_USERNAME"),
        passw=os.getenv("API_PASSWORD"),
        host=os.getenv("API_URL"),
        org=os.getenv("API_ORG")
    )

    if not auth['status']:
        return json.dumps({"error": "Authentication failed.", "details": auth['data']}, indent=2)

    method = fortiedr.Events()

    # Convertir le time_range
    hours = int(time_range.split()[0])
    time_from = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    time_to = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    params = {"firstSeenFrom": time_from, "firstSeenTo": time_to}
    if action != "All":
        params["actions"] = action
    if items != "No limit":
        try:
            params["itemsPerPage"] = int(items)
        except ValueError:
            pass

    response = method.list_events(**params)

    if not response['status']:
        return json.dumps({"error": "Failed to fetch events.", "details": response['data']}, indent=2)

    if output_format.lower() == "json":
        return json.dumps(response['data'], indent=2)

    # Format table avec colonne Rule(s)
    table_data = []
    for i, entry in enumerate(response['data'], start=1):
        process = entry.get("process", "")
        rules = entry.get("rules", [])
        process_display = process if len(process) <= 25 else process[:22] + "..."
        rule_str = "\n".join(rules) if rules else ""

        table_data.append([
            i,
            str(entry.get("eventId", ""))[:10],
            process_display,
            entry.get("firstSeen", "")[:16],
            entry.get("lastSeen", "")[:16],
            entry.get("classification", "")[:13],
            entry.get("collectors", [{}])[0].get("device", "N/A")[:15],
            entry.get("action", ""), 
            rule_str
        ])

    headers = ["#", "Event ID", "Process", "First Seen", "Last Seen", "Classification", "Device", "Action", "Rule(s)"]
    df = pd.DataFrame(table_data, columns=headers)
    return tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False)

def run_threat_query(fmt, items, category, time_range):
    """Fetch FortiEDR threat hunting results."""
    auth = fortiedr.auth(
        user=os.getenv("API_USERNAME"),
        passw=os.getenv("API_PASSWORD"),
        host=os.getenv("API_URL"),
        org=os.getenv("API_ORG")
    )

    if not auth['status']:
        return json.dumps({"error": "Authentication failed.", "details": auth['data']}, indent=2)

    method = fortiedr.ThreatHunting()
    params = {
        "itemsPerPage": int(items),
        "category": None if category == "All" else category,
        "time": time_range
    }

    # Remove empty values
    params = {k: v for k, v in params.items() if v}

    response = method.search(**params)

    if not response['status']:
        return json.dumps({"error": "Failed to fetch threat data.", "details": response['data']}, indent=2)

    if fmt.lower() == "json":
        return json.dumps(response['data'], indent=2)

    table_data = []
    for index, event in enumerate(response['data'], start=1):
        source_process = event['Source'].get('Process', {})
        command_line = source_process.get('CommandLine', 'N/A')
        user_info = source_process.get('User', {})
        username = user_info.get('Username', 'N/A')
        target_path = event['Target'].get('File', {}).get('Path', 'N/A')

        command_line_display = command_line if len(command_line) <= 25 else command_line[:22] + "..."
        target_path_display = target_path if len(target_path) <= 25 else target_path[:22] + "..."

        table_data.append([ 
            index,
            datetime.fromtimestamp(event['Time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            event['Type'],
            event['Device']['Name'],
            source_process.get('Name', 'N/A'),
            command_line_display,
            target_path_display,
            username
        ])

    headers = ["#", "Time", "Type", "Device Name", "Process Name", "Command Line", "Target Path", "User"]
    df = pd.DataFrame(table_data, columns=headers)
    return tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False)
