# JSON data for MITRE tests
tests = [
    {
        "id": "T1027.007",
        "title": "Obfuscated Files or Information: Dynamic API Resolution",
        "test": "Dynamic API Resolution - Ninja-syscall",
        "description": "This test calls NtCreateFile via API hashing and dynamic syscall resolution. I have dubbed this particular combination of techniques 'Ninja-syscall'. When successful, a new file named 'hello.log' will be created in the default user's temporary folder, which is a common location for a dropper.",
        "rules": [
            "Execution Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1027.007 -TestNumbers 1"
    },
    {
        "id": "T1036.003",
        "title": "Masquerading: Rename System Utilities",
        "test": "Masquerading - non-windows exe running as windows exe",
        "description": "Copies an exe, renames it as a windows exe, and launches it to masquerade as a real windows exe. Upon successful execution, powershell will execute T1036.003.exe as svchost.exe from on a non-standard path.",
        "rules": [
            "Exfiltration Prevention",
            "- Fake Critical Program - Attempted to Hide as a Service"
        ],
        "command": "Invoke-AtomicTest T1036.003 -TestNumbers 6"
    },
    {
        "id": "T1055",
        "title": "Process Injection",
        "test": "Dirty Vanity process Injection",
        "description": "This test uses the Windows undocumented remote-fork API RtlCreateProcessReflection to create a cloned process of the parent process with shellcode written in its memory. The shellcode is executed after being forked to the child process. The technique was first presented at BlackHat Europe 2022. Shellcode will open a message box and a notepad.",
        "rules": [
            "Exfiltration Prevention",
            "- Injected Process - Process Created from an Injected Thread",
            "- Injected Thread - Connection from an Injected Thread",
            "- Malicious File Detected",
            "- PUP - Potentially Unwanted Program",
            "- Process Injection - Entry Point Modification Detected",
            "Ransomware Prevention",
            "- Injected Process - Process Created from an Injected Thread",
            "- Injected Thread - Connection from an Injected Thread",
            "- Malicious File Detected",
            "- PUP - Potentially Unwanted Program",
            "- Process Injection - Entry Point Modification Detected"
        ],
        "command": "Invoke-AtomicTest T1055 -TestNumbers 4"
    },
    {
        "id": "T1059.001",
        "title": "Command and Scripting Interpreter: PowerShell",
        "test": "Download Mimikatz and dump credentials",
        "description": "Download Mimikatz and dump credentials. Upon execution, Mimikatz dump details and password hashes will be displayed.",
        "rules": [
            "Exfiltration Prevention",
            "- Suspicious Application - Connection Attempt from a Suspicious Application",
            "- Unmapped Executable - Executable File Without a Corresponding File System Reference"
        ],
        "command": "Invoke-AtomicTest T1059.001 -TestNumbers 1"
    },
    {
        "id": "T1105",
        "title": "Ingress Tool Transfer",
        "test": "Download a file using wscript",
        "description": "Use wscript to run a local VisualBasic file to download a remote file.",
        "rules": [
            "Exfiltration Prevention",
            "- Suspicious Application - Connection Attempt from a Suspicious Application"
        ],
        "command": "Invoke-AtomicTest T1105 -TestNumbers 26"
    },
    {
        "id": "T1106",
        "title": "Native API",
        "test": "Run Shellcode via Syscall in Go",
        "description": "Runs shellcode in the current running process via a syscall. This technique involves allocating memory for the shellcode using VirtualAlloc with Read/Write permissions, copying the shellcode to the allocated space with the RtlCopyMemory macro, modifying the memory page permissions to Execute/Read using VirtualProtect, and finally executing the shellcode entry point via a syscall.",
        "rules": [
            "Execution Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1106 -TestNumbers 5"
    },
    {
        "id": "T1134.001",
        "title": "Access Token Manipulation: Token Impersonation/Theft",
        "test": "Utilizes Juicy Potato to obtain privilege escalation",
        "description": "This Atomic utilizes Juicy Potato to obtain privilege escalation. Upon successful execution of this test, a vulnerable CLSID will be used to execute a process with system permissions. This tactic has been previously observed in SnapMC Ransomware, amongst numerous other campaigns.",
        "rules": [
            "Execution Prevention",
            "- Malicious File Detected",
            "- PUP - Potentially Unwanted Program"
        ],
        "command": "Invoke-AtomicTest T1134.001 -TestNumbers 5"
    },
    {
        "id": "T1555.003",
        "title": "Credentials from Password Stores: Credentials from Web Browsers",
        "test": "WebBrowserPassView - Credentials from Browser",
        "description": "The following Atomic test utilizes WebBrowserPassView to extract passwords from browsers on a Windows system. WebBrowserPassView is an open-source application used to retrieve passwords stored on a local computer. Recently noticed as a tool used in the BlackCat Ransomware.",
        "rules": [
            "Exfiltration Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1555.003 -TestNumbers 15"
    },
    {
        "id": "T1562.002",
        "title": "Impair Defenses: Disable Windows Event Logging",
        "test": "Makes Eventlog blind with Phant0m",
        "description": "Use Phant0m to disable Eventlog.",
        "rules": [
            "Exfiltration Prevention",
            "- Malicious File Detected"
        ],
        "command": "Invoke-AtomicTest T1562.002 -TestNumbers 7"
    }
]