# Step 1: Ensure TLS 1.2 for downloads
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Step 2: Install powershell-yaml in current user scope
if (-not (Get-Module -ListAvailable powershell-yaml)) {
    Write-Host "Installing powershell-yaml..." -ForegroundColor Cyan
    Install-Module powershell-yaml -Scope CurrentUser -Force -ErrorAction Stop
} else {
    Write-Host "powershell-yaml already installed." -ForegroundColor Green
}

# Step 3: Run AtomicRedTeam installer script from GitHub
try {
    Invoke-Expression (Invoke-WebRequest 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing).Content
    Install-AtomicRedTeam -getAtomics -Force
    Write-Host "Atomic Red Team installed." -ForegroundColor Green
} catch {
    Write-Error "Failed to install Atomic Red Team. Check SSL inspection or internet access."
    exit 1
}

# Step 4: Configure $PROFILE for future sessions
$moduleLine = 'Import-Module "C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1" -Force'
$defaultParamLine = '$PSDefaultParameterValues = @{"Invoke-AtomicTest:PathToAtomicsFolder" = "C:\AtomicRedTeam\atomics"}'

# Ensure profile file exists
if (-not (Test-Path $PROFILE)) {
    New-Item -Path $PROFILE -ItemType File -Force | Out-Null
    $currentProfileContent = ""
} else {
    $currentProfileContent = Get-Content $PROFILE -Raw
}

# Append only if not already present
if ($currentProfileContent -notmatch [regex]::Escape($moduleLine)) {
    Add-Content -Path $PROFILE -Value "`n$moduleLine"
}

if ($currentProfileContent -notmatch [regex]::Escape($defaultParamLine)) {
    Add-Content -Path $PROFILE -Value "`n$defaultParamLine"
}

Write-Host "`$PROFILE updated." -ForegroundColor Green
