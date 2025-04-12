import os
import subprocess
import csv
from pathlib import Path
import pandas as pd
from tabulate import tabulate

def run_av_scan(result_box):
    desktop = Path.home() / "Desktop"
    scan_dir = desktop / "MalwareBazaar_Downloads"
    output_dir = desktop / "FortiEDRAvScanner"
    output_csv = desktop / "FortiEDRAvScanner.csv"

    scanner_exe = r'"C:\Program Files\Fortinet\FortiEDR\FortiEDRAvScanner.exe"'
    signatures = r"C:\ProgramData\FortiEDR\Config\Collector\Signatures"
    command = f'{scanner_exe} -d "{scan_dir}" -s {signatures} --output "{output_dir}"'

    result_box.delete("0.0", "end")
    result_box.insert("end", f"[COMMAND] {command}\n\n", "orange")
    result_box.update_idletasks()

    try:
        subprocess.run(command, shell=True, check=True)
        result_box.insert("end", "Scan completed!\n\n", "green")
    except Exception as e:
        result_box.insert("end", f"Scan error: {str(e)}\n", "red")
        return

    if not output_csv.exists():
        result_box.insert("end", "CSV output not found.\n", "red")
        return

    try:
        with open(output_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            result_box.insert("end", "No results found in CSV.\n", "red")
            return

        table_data = []
        for row in rows:
            file_name = os.path.basename(row["File name"])
            virus = row.get("Virus name", "")
            table_data.append([file_name, virus if virus else "No detection"])

        df = pd.DataFrame(table_data, columns=["File name", "Virus name"])
        table_string = tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False)

        result_box.insert("end", table_string + "\n", "white")

    except Exception as e:
        result_box.insert("end", f"Error reading CSV: {str(e)}\n", "red")
