import subprocess

def execute_atomic_test(command):
    """
    Executes the given PowerShell command using subprocess.
    Returns stdout and stderr as a tuple.
    """
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", f"Execution error: {str(e)}"
