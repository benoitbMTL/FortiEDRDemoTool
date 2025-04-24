# FortiEDR Demo Tool

A graphical demonstration tool to explore **FortiEDR functionalities** using a user-friendly interface.  
This project helps visualize **MITRE techniques**, simulate **malware analysis**, run **API queries**, and perform **local diagnostics** in a SOC-like context.

---

## 🎬 Demo Video (coming very soon)

---

## 🧪 Requirements

Before running the app, create a `.env` file in the root directory with the following content:

```
API_URL=https://fortiedr-host.example.com
API_USERNAME=username
API_PASSWORD=password
API_ORG=MyOrganization # Case sensitive
```

This file is required to authenticate with the FortiEDR API.



### Additional Setup for Atomic Red Team

To enable MITRE simulation, you must install the Atomic Red Team PowerShell module.  
Follow these steps:

1. Open **PowerShell 5.x as Administrator** and run:

```powershell
Install-Module PowerShellGet -Force -AllowClobber
```

Then, open **PowerShell in normal mode** and run:

```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Install-Module powershell-yaml -Scope CurrentUser -Force -ErrorAction Stop
Invoke-Expression (Invoke-WebRequest 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing).Content
Install-AtomicRedTeam -getAtomics -Force
```

To persist the module for future PowerShell sessions, configure your profile ($PROFILE):

If the file doesn’t exist, you can create it:

```powershell
New-Item -ItemType File -Path $PROFILE -Force
```

Then edit it with:

```powershell
notepad $PROFILE
```
And add the following lines to $PROFILE:

```powershell
Import-Module "C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1" -Force
$PSDefaultParameterValues = @{"Invoke-AtomicTest:PathToAtomicsFolder" = "C:\AtomicRedTeam\atomics"}
```

You can test your setup by running this simple Atomic test (for example, listing system information via T1082):

```powershell
Invoke-AtomicTest T1082 -TestNumbers 1 -Confirm:$false
```

---

## ▶️ How to Run (Development)

1. Clone the repository:

```bash
git clone https://github.com/benoitbMTL/FortiEDRDemoTool.git
cd FortiEDRDemoTool
```

2. (Optional) Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python app.py
```

---

## 🏗️ How to Build the EXE

To generate a portable `.exe` version (Windows only):

1. Make sure you have `pyinstaller` installed:

```bash
pip install pyinstaller
```

2. Run the build script:

```bash
build-fortiedr.bat
```

This script will:

Upgrade pip and install pyinstaller if it's not already installed

```bash
python -m pip install --upgrade pip 
python -m pip install pyinstaller
```

Build the executable using the custom .spec file:

```bash
pyinstaller FortiEDRDemoTool.spec
```

Copy the `FortiEDRDemoTool.exe` file to the Desktop
