# Enable TLS 1.2 for secure connection
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Define Python installer URL (latest 64-bit version from official site)
$pythonPage = Invoke-WebRequest -Uri "https://www.python.org/downloads/windows/" -UseBasicParsing
$matches = Select-String -InputObject $pythonPage.Content -Pattern 'https://www\.python\.org/ftp/python/([\d.]+)/python-([\d.]+)-amd64\.exe' -AllMatches

# Extract latest version and URL
$latestUrl = $matches.Matches[0].Value
$version = $matches.Matches[0].Groups[1].Value

# Download installer to temp folder
$installerPath = "$env:TEMP\python-$version-amd64.exe"
Write-Host "Downloading Python $version..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $latestUrl -OutFile $installerPath

# Install silently with default settings and add to PATH
Write-Host "Installing Python $version..." -ForegroundColor Cyan
Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait

# Confirm installation
Write-Host "Python $version installed. Verifying installation..." -ForegroundColor Green
python --version

# Upgrade pip to the latest version
Write-Host "Upgrading pip to the latest version..." -ForegroundColor Cyan
python -m pip install --upgrade pip
