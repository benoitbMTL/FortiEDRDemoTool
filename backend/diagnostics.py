import os
import subprocess
from dotenv import load_dotenv
from backend.ssl_bypass import *
import fortiedr
import threading

load_dotenv()

API_URL = os.getenv("API_URL")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_ORG = os.getenv("API_ORG")

def insert_section_title(result_box, title, width=70):
    sep = "─" * width
    result_box.insert("end", f"\n{sep}\n", "section")
    result_box.insert("end", f"{title.center(width)}\n", "section")
    result_box.insert("end", f"{sep}\n", "section")

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
    insert_section_title(result_box, "Internet Connectivity")
    run_command('powershell -Command "Test-NetConnection 8.8.8.8 | Select-Object RemoteAddress, PingSucceeded"', result_box)

    insert_section_title(result_box, "DNS Resolution (API_URL)")
    dns_target = API_URL.replace("https://", "").split("/")[0]
    ps_command = f'powershell -Command "Resolve-DnsName {dns_target} | Select-Object Name, IPAddress"'
    run_command(ps_command, result_box)


def get_core_and_aggregator(result_box):
    insert_section_title(result_box, "Fetch Core and Aggregator from API")
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

        aggregator_addr = data.get("aggregators", [{}])[0].get("address", "").split(":")[0]
        core_addr = data.get("cores", [{}])[0].get("address", "").split(":")[0]

        result_box.insert("end", f"Aggregator IP: {aggregator_addr}\n", "stdout")
        result_box.insert("end", f"Core IP: {core_addr}\n", "stdout")
        result_box.update_idletasks()

        return core_addr, aggregator_addr

    except Exception as e:
        result_box.insert("end", f"API Error: {str(e)}\n", "stderr")
        return None, None

def test_net_connection(result_box, hostname, port):
    insert_section_title(result_box, f"Test Network Connection to {hostname}:{port}")
    command = f"powershell -Command \"Test-NetConnection {hostname} -Port {port} -InformationLevel Detailed\""
    run_command(command, result_box)

def check_open_ports(result_box):
    insert_section_title(result_box, "Check Open Connections (netstat)")
    ports = [8081, 555]
    for port in ports:
        command = f"powershell -Command \"netstat -ano | Select-String ':{port}' | ForEach-Object {{ $_.Line }} | Out-String\""
        run_command(command, result_box)

def check_fortiedr_manager_status(result_box):
    insert_section_title(result_box, "FortiEDR Collector Status")
    command = "\"C:\\Program Files\\Fortinet\\FortiEDR\\FortiEDRCollectorService.exe\" --estatus"
    run_command(command, result_box)

def run_all_diagnostics(result_box):
    def task():
        result_box.tag_config("section", foreground="#FFA500")     # Orange
        result_box.tag_config("command", foreground="#00BFFF")     # Light blue
        result_box.tag_config("stdout", foreground="#FFFFFF")      # White
        result_box.tag_config("stderr", foreground="#FF4444")      # Red
        result_box.tag_config("banner", foreground="#00FF00")      # Green

        insert_banner(result_box, "FortiEDR Health Check")

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

        insert_banner(result_box, "Diagnostics Complete")

        result_box.update_idletasks()

    threading.Thread(target=task).start()

def insert_banner(result_box, text):
    result_box.tag_config("banner_simple", foreground="#FFFFFF", background="#145A32")
    result_box.insert("end", "\n{:^70}\n\n".format(text), "banner_simple")
