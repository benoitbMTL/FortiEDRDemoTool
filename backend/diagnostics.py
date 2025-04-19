import os
import subprocess
from dotenv import load_dotenv
import fortiedr
import threading

load_dotenv()

API_URL = os.getenv("API_URL")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_ORG = os.getenv("API_ORG")

# Override SSL verification by monkey patching requests inside fortiedr
import requests
orig_post = requests.post
orig_get = requests.get
requests.post = lambda *args, **kwargs: orig_post(*args, verify=False, **kwargs)
requests.get = lambda *args, **kwargs: orig_get(*args, verify=False, **kwargs)

# Optional: suppress InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_command(command, result_box):
    result_box.insert("end", f"\n[COMMAND] {command}\n", "command")
    result_box.update_idletasks()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            result_box.insert("end", result.stdout.strip() + "\n", "stdout")
        if result.stderr:
            result_box.insert("end", result.stderr.strip() + "\n", "stderr")
    except Exception as e:
        result_box.insert("end", f"[EXCEPTION] {str(e)}\n", "stderr")
    result_box.insert("end", "\n")
    result_box.update_idletasks()

def check_internet_and_dns(result_box):
    result_box.insert("end", "\n─── Internet Connectivity ───\n", "section")
    run_command("ping 8.8.8.8 -n 2", result_box)

    result_box.insert("end", "\n─── DNS Resolution (API_URL) ───\n", "section")
    dns_target = API_URL.replace("https://", "").split("/")[0]
    run_command(f"nslookup {dns_target}", result_box)

def get_core_and_aggregator(result_box):
    result_box.insert("end", "\n─── Fetch Core and Aggregator from API ───\n", "section")
    try:
        auth = fortiedr.auth(
            user=API_USERNAME,
            passw=API_PASSWORD,
            host=API_URL.replace("https://", "").split("/")[0],
            org=API_ORG
        )

        if not auth['status']:
            result_box.insert("end", f"Authentication failed: {auth['data']}\n", "stderr")
            return None, None

        admin = fortiedr.Administrator()
        data = admin.list_system_summary(organization=API_ORG)['data']

        core_addr = data.get("cores", [{}])[0].get("address", "").split(":")[0]
        aggregator_addr = data.get("aggregators", [{}])[0].get("address", "").split(":")[0]

        result_box.insert("end", f"Core IP: {core_addr}\n", "stdout")
        result_box.insert("end", f"Aggregator IP: {aggregator_addr}\n", "stdout")
        result_box.update_idletasks()

        return core_addr, aggregator_addr

    except Exception as e:
        result_box.insert("end", f"API Error: {str(e)}\n", "stderr")
        return None, None

def test_net_connection(result_box, hostname, port):
    result_box.insert("end", f"\n─── Test Network Connection to {hostname}:{port} ───\n", "section")
    command = f"powershell -Command \"Test-NetConnection {hostname} -Port {port} -InformationLevel Detailed\""
    run_command(command, result_box)

def check_open_ports(result_box):
    result_box.insert("end", "\n─── Check Open Connections (NETSTAT) ───\n", "section")
    run_command("netstat -an | findstr 8081", result_box)
    run_command("netstat -an | findstr 555", result_box)

def check_fortiedr_manager_status(result_box):
    result_box.insert("end", "\n─── FortiEDR Collector Status ───\n", "section")
    command = "\"C:\\Program Files\\Fortinet\\FortiEDR\\FortiEDRCollectorService.exe\" --estatus"
    run_command(command, result_box)

def run_all_diagnostics(result_box):
    def task():
        result_box.tag_config("section", foreground="#FFA500")     # Orange
        result_box.tag_config("command", foreground="#00BFFF")     # Light blue
        result_box.tag_config("stdout", foreground="#FFFFFF")      # White
        result_box.tag_config("stderr", foreground="#FF4444")      # Red
        result_box.tag_config("banner", foreground="#00FF00")      # Green

        result_box.insert("end", "\n" + "="*40 + "\n", "banner")
        result_box.insert("end", "  FortiEDR Health Check\n", "banner")
        result_box.insert("end", "="*40 + "\n\n", "banner")
        result_box.update_idletasks()

        check_internet_and_dns(result_box)

        core, aggregator = get_core_and_aggregator(result_box)
        if not core or not aggregator:
            result_box.insert("end", "Skipping net tests: Missing core or aggregator.\n", "stderr")
        else:
            test_net_connection(result_box, aggregator, 8081)
            test_net_connection(result_box, core, 555)

        check_open_ports(result_box)
        check_fortiedr_manager_status(result_box)

        result_box.insert("end", "\n" + "="*40 + "\n", "banner")
        result_box.insert("end", "  Diagnostics complete\n", "banner")
        result_box.insert("end", "="*40 + "\n", "banner")
        result_box.update_idletasks()

    threading.Thread(target=task).start()
