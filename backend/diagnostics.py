"""
diagnostics.py

FortiEDR health-checks and diagnostics for the GUI.
Implements non-blocking checks with per-step timeouts so one slow check won't block the entire sequence.
Comments and output messages are in English.

Usage:
  - Import run_all_diagnostics(result_box) from your GUI code and call it.
  - result_box is expected to be a Tkinter Text-like widget supporting insert(), tag_config(), update_idletasks(), search(), etc.

Security note:
  - The module assumes existence of environment variables for FortiEDR API credentials if used.
  - Do not commit secrets to source control.
"""

import os
import subprocess
import threading
import time
import shutil
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import concurrent.futures

# preserve original imports (may be package-local)
try:
    from backend.ssl_bypass import *  # noqa: F401,F403
except Exception:
    # best-effort import; GUI should still work for local checks even if this import fails
    pass

try:
    import fortiedr
except Exception:
    fortiedr = None  # keep module resilient if fortiedr isn't installed

# Environment-configured API credentials (if used)
API_URL = os.getenv("API_URL")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_ORG = os.getenv("API_ORG")

# -------------------- Configurable constants --------------------
DEFAULT_CMD_TIMEOUT = 8       # seconds for shell commands (powershell)
DEFAULT_API_TIMEOUT = 8       # seconds for FortiEDR API calls
DEFAULT_SHORT_TIMEOUT = 4     # short checks (DNS, netstat)
DIAG_THREAD_POOL_SIZE = 4     # thread pool max workers
# ----------------------------------------------------------------

# Thread pool executor for running blocking or slow calls with timeout
DIAG_EXECUTOR = ThreadPoolExecutor(max_workers=DIAG_THREAD_POOL_SIZE)


def insert_section_title(result_box, title, width=70):
    """
    Insert a section title block to the result_box (Tkinter Text widget).
    Output is English and formatted for readability.
    """
    sep = "─" * width
    result_box.insert("end", f"\n{sep}\n", "section")
    result_box.insert("end", f"{title.center(width)}\n", "section")
    result_box.insert("end", f"{sep}\n", "section")

def run_command(command, result_box, timeout=None):
    """
    Run a shell command with a timeout and write outputs to result_box.
    This variant merges stderr into stdout to preserve original output order
    (helps for tools like nslookup that may write parts to stderr).

    - command: shell command string
    - result_box: Tk Text widget
    - timeout: seconds to wait before aborting the command (None -> DEFAULT_CMD_TIMEOUT)
    """
    import subprocess

    if timeout is None:
        timeout = DEFAULT_CMD_TIMEOUT

    result_box.insert("end", f"\n[COMMAND] {command}\n", "command")
    result_box.update_idletasks()

    try:
        # Use stdout=PIPE and merge stderr into stdout; do NOT use capture_output here.
        completed = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout
        )

        if completed.stdout:
            cleaned_output = clean_tcp_lines_only(completed.stdout.strip())
            result_box.insert("end", cleaned_output + "\n", "stdout")

    except subprocess.TimeoutExpired as te:
        # TimeoutExpired provides .output when stdout was captured
        result_box.insert("end", f"[TIMEOUT] Command timed out after {timeout} seconds: {command}\n", "stderr")
        if getattr(te, "output", None):
            result_box.insert("end", (clean_tcp_lines_only(te.output.strip()) + "\n"), "stdout")

    except Exception as e:
        result_box.insert("end", f"[EXCEPTION] {str(e)}\n", "stderr")

    result_box.insert("end", "\n")
    result_box.update_idletasks()

def safe_call(fn, timeout, *args, **kwargs):
    """
    Execute fn(*args, **kwargs) in a thread and wait at most `timeout` seconds.
    Returns (ok, result_or_exception):
      - ok == True: result_or_exception is the return value
      - ok == False: result_or_exception is an Exception (TimeoutError or other)
    """
    if timeout is None:
        timeout = DEFAULT_API_TIMEOUT

    future = DIAG_EXECUTOR.submit(fn, *args, **kwargs)
    try:
        res = future.result(timeout=timeout)
        return True, res
    except FuturesTimeoutError:
        # best-effort cancel
        future.cancel()
        return False, TimeoutError(f"Operation timed out after {timeout} seconds")
    except Exception as e:
        return False, e


def get_core_and_aggregator(result_box):
    """
    Fetch core and aggregator addresses from FortiEDR API.
    Returns (core_addr, aggregator_addr) or (None, None) on failure/timeout.
    """
    insert_section_title(result_box, "Fetch Core and Aggregator from API")

    if fortiedr is None:
        result_box.insert("end", "FortiEDR SDK not available; skipping API checks.\n", "stderr")
        return None, None

    def _do_auth():
        return fortiedr.auth(
            user=API_USERNAME,
            passw=API_PASSWORD,
            host=API_URL.replace("https://", "").split("/")[0] if API_URL else None,
            org=API_ORG
        )

    ok, auth_res = safe_call(_do_auth, DEFAULT_API_TIMEOUT)
    if not ok:
        result_box.insert("end", f"Authentication failed (timeout or error): {auth_res}\n", "stderr")
        return None, None

    try:
        if not auth_res.get('status'):
            result_box.insert("end", f"Authentication failed: {auth_res.get('data')}\n", "stderr")
            return None, None
    except Exception as e:
        result_box.insert("end", f"Authentication unexpected response: {e}\n", "stderr")
        return None, None

    def _fetch_summary():
        admin = fortiedr.Administrator()
        return admin.list_system_summary(organization=API_ORG)

    ok, summary_res = safe_call(_fetch_summary, DEFAULT_API_TIMEOUT)
    if not ok:
        result_box.insert("end", f"Fetching system summary failed (timeout or error): {summary_res}\n", "stderr")
        return None, None

    try:
        data = summary_res.get('data', {})
        aggregator_addr = data.get("aggregators", [{}])[0].get("address", "").split(":")[0]
        core_addr = data.get("cores", [{}])[-1].get("address", "").split(":")[0]

        result_box.insert("end", f"Aggregator IP: {aggregator_addr}\n", "stdout")
        result_box.insert("end", f"Core IP: {core_addr}\n", "stdout")
        result_box.update_idletasks()

        return core_addr, aggregator_addr
    except Exception as e:
        result_box.insert("end", f"API parsing error: {str(e)}\n", "stderr")
        return None, None

def test_net_connection(result_box, hostname, port):
    """
    Test network connection to hostname:port using tcping (from root/tools) if available,
    otherwise fallback to a Python socket check.

    - tcping timeout uses DEFAULT_CMD_TIMEOUT (seconds) converted to milliseconds.
    - Command format: tcping.exe -n 1 -w <ms> <host> <port>
    """
    import shutil
    from pathlib import Path
    import socket

    insert_section_title(result_box, f"Test Network Connection to {hostname}:{port}")

    # compute timeout in milliseconds from DEFAULT_CMD_TIMEOUT (seconds)
    timeout = int(DEFAULT_CMD_TIMEOUT - 6)

    # try PATH first, then project_root/tools/tcping.exe
    tcping_exe = shutil.which("tcping")
    if not tcping_exe:
        project_root = Path(__file__).resolve().parents[1]  # project root (parent of backend)
        candidate = project_root / "tools" / "tcping.exe"
        if candidate.exists():
            tcping_exe = str(candidate)

    if tcping_exe:
        # place -n and -w before host as requested
        cmd = f'"{tcping_exe}" -n 1 -w {timeout} {hostname} {port}'
        # add a small margin to the subprocess timeout
        run_command(cmd, result_box, timeout=DEFAULT_CMD_TIMEOUT - 5)
        return

    # Fallback: Python socket check with DEFAULT_CMD_TIMEOUT seconds
    result_box.insert("end", "[INFO] tcping not found; falling back to Python socket connect\n", "command")
    result_box.update_idletasks()
    try:
        with socket.create_connection((hostname, int(port)), timeout=DEFAULT_CMD_TIMEOUT):
            result_box.insert("end", f"[socket] Success: TCP connect to {hostname}:{port}\n", "stdout")
    except Exception as e:
        result_box.insert("end", f"[socket] Failed: {str(e)}\n", "stderr")

    result_box.update_idletasks()

def check_internet_and_dns(result_box):
    """
    Check internet connectivity and DNS resolution with short timeouts.
    """
    insert_section_title(result_box, "Internet Connectivity (Google DNS)")
    run_command("ping -n 1 8.8.8.8", result_box, timeout=DEFAULT_CMD_TIMEOUT)

    insert_section_title(result_box, "DNS Resolution (Management Console Hostname)")
    dns_target = API_URL.replace("https://", "").split("/")[0] if API_URL else None
    if dns_target:
        ns_command = f'nslookup {dns_target}'
        run_command(ns_command, result_box, timeout=DEFAULT_SHORT_TIMEOUT)
    else:
        result_box.insert("end", "API_URL not configured; skipping DNS check.\n", "stderr")


def check_open_ports(result_box):
    """
    Check for open connections (netstat) for specific ports using short timeouts.
    """
    insert_section_title(result_box, "Check Open Connections (Netstat)")
    ports = [8081, 555]
    for port in ports:
        command = f'netstat -ano | findstr ":{port}" | findstr "ESTABLISHED"'
        run_command(command, result_box, timeout=DEFAULT_SHORT_TIMEOUT)


def check_fortiedr_manager_status(result_box):
    """
    Check the FortiEDR Collector service status with a bounded timeout.
    """
    insert_section_title(result_box, "FortiEDR Collector Status")
    command = "\"C:\\Program Files\\Fortinet\\FortiEDR\\FortiEDRCollectorService.exe\" --estatus"
    run_command(command, result_box, timeout=DEFAULT_CMD_TIMEOUT)


def run_all_diagnostics(result_box):
    """
    Orchestrate all diagnostics in a background thread.
    Each check has its own timeout and errors are caught so the sequence continues.
    """
    def task():
        # Configure tags for colored output in the Tk textbox
        result_box.tag_config("section", foreground="#FFA500")          # Orange
        result_box.tag_config("command", foreground="#00BFFF")          # Light blue
        result_box.tag_config("stdout", foreground="#FFFFFF")           # White
        result_box.tag_config("stderr", foreground="#FF4444")           # Red
        result_box.tag_config("banner_simple", foreground="#FFFFFF", background="#145A32")
        result_box.tag_config("success_keyword", foreground="#00FF00")  # Green
        result_box.tag_config("fail_keyword", foreground="#FF4444")     # Red

        insert_banner(result_box, "FortiEDR Health Check")
        result_box.update_idletasks()

        # Run checks in sequence; each is wrapped to ensure failures/timeouts don't stop the flow
        try:
            check_internet_and_dns(result_box)
        except Exception as e:
            result_box.insert("end", f"[ERROR] check_internet_and_dns failed: {e}\n", "stderr")

        try:
            core, aggregator = get_core_and_aggregator(result_box)
        except Exception as e:
            result_box.insert("end", f"[ERROR] get_core_and_aggregator failed: {e}\n", "stderr")
            core, aggregator = None, None

        if not core or not aggregator:
            result_box.insert("end", "Skipping net tests: Missing core or aggregator.\n", "stderr")
        else:
            try:
                test_net_connection(result_box, aggregator, 8081)
            except Exception as e:
                result_box.insert("end", f"[ERROR] test_net_connection (aggregator) failed: {e}\n", "stderr")
            try:
                test_net_connection(result_box, core, 555)
            except Exception as e:
                result_box.insert("end", f"[ERROR] test_net_connection (core) failed: {e}\n", "stderr")

        try:
            check_open_ports(result_box)
        except Exception as e:
            result_box.insert("end", f"[ERROR] check_open_ports failed: {e}\n", "stderr")

        try:
            check_fortiedr_manager_status(result_box)
        except Exception as e:
            result_box.insert("end", f"[ERROR] check_fortiedr_manager_status failed: {e}\n", "stderr")

        insert_banner(result_box, "Diagnostics Complete")
        highlight_status_keywords(result_box)
        result_box.update_idletasks()

    threading.Thread(target=task, daemon=True).start()


def insert_banner(result_box, text):
    """
    Insert a simple banner line into the result_box.
    """
    result_box.insert("end", "\n{:^70}\n\n".format(text), "banner_simple")


def clean_tcp_lines_only(text):
    """
    Keep TCP lines aligned similarly to previous behavior; other lines are returned as-is.
    """
    return "\n".join(line.lstrip() if line.lstrip().startswith("TCP") else line for line in text.splitlines())


def highlight_status_keywords(result_box):
    """
    Highlight common success/failure keywords in the result_box for faster scanning.
    """
    green_words = ["True", "Up", "Updated", "Running", "Connected", "ESTABLISHED"]
    red_words = ["False", "Down", "Disconnected", "STOPPED", "ERROR"]

    for word in green_words:
        index = result_box.search(word, "1.0", stopindex="end")
        while index:
            end_index = f"{index}+{len(word)}c"
            result_box.tag_add("success_keyword", index, end_index)
            index = result_box.search(word, end_index, stopindex="end")

    for word in red_words:
        index = result_box.search(word, "1.0", stopindex="end")
        while index:
            end_index = f"{index}+{len(word)}c"
            result_box.tag_add("fail_keyword", index, end_index)
            index = result_box.search(word, end_index, stopindex="end")

def find_tcping():
    """
    Locate tcping executable in this order:
      1) If running bundled by PyInstaller: sys._MEIPASS / 'tools' / 'tcping.exe'
      2) project_root/tools/tcping.exe (development layout)
      3) system PATH (shutil.which("tcping"))
    Returns full path (str) or None if not found.
    """
    # 1) If bundled by PyInstaller, files are extracted to sys._MEIPASS
    base = getattr(sys, "_MEIPASS", None)
    if base:
        candidate = Path(base) / "tools" / "tcping.exe"
        if candidate.exists():
            return str(candidate)

    # 2) Project-root tools folder (when running from source)
    try:
        # this file is expected at backend/diagnostics.py -> parents[1] is project root
        project_root = Path(__file__).resolve().parents[1]
        candidate = project_root / "tools" / "tcping.exe"
        if candidate.exists():
            return str(candidate)
    except Exception:
        pass

    # 3) Finally, check PATH
    exe = shutil.which("tcping")
    if exe:
        return exe

    return None
