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
installer.bat
```

The `FortiEDRDemoTool.exe` file will be generated and automatically copied to your Desktop.
