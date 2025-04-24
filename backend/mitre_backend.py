import subprocess
import os

def execute_atomic_test(command):
    module_path = "C:\\AtomicRedTeam\\invoke-atomicredteam\\Invoke-AtomicRedTeam.psd1"
    import_module = f'Import-Module "{module_path}" -Force'

    try:
        # Try without import first (if PROFILE is configured)
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=90
        )
        if "Invoke-AtomicTest" in result.stderr:
            # Retry with manual import
            full_command = f"{import_module}; {command}"
            result = subprocess.run(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", full_command],
                capture_output=True,
                text=True,
                timeout=90
            )
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", f"Execution error: {str(e)}"
