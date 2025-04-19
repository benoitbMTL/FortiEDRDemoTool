# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator." -ForegroundColor Red
    Write-Host "Right-click on PowerShell and select 'Run as administrator'." -ForegroundColor Yellow
    Pause
    exit 1
}

# Set certificate path
$certPath = Join-Path $PSScriptRoot "Fortinet_CA_SSL.cer"

# Check if cert file exists
if (-not (Test-Path $certPath)) {
    Write-Host "[ERROR] Certificate file not found: $certPath" -ForegroundColor Red
    exit 1
}

Write-Host "Installing certificate into Windows root store..." -ForegroundColor Cyan

# Import into Windows Root store
try {
    certutil -addstore -f "Root" $certPath | Out-Null
    Write-Host "[OK] Certificate added to Windows root store." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to add certificate to Windows root store." -ForegroundColor Red
}

# Try importing into Firefox (if certutil from NSS is available)
$firefoxPaths = @(
    "$env:ProgramFiles\Mozilla Firefox",
    "$env:ProgramFiles(x86)\Mozilla Firefox"
)

$certutilPath = $null
foreach ($path in $firefoxPaths) {
    $candidate = Join-Path $path "certutil.exe"
    if (Test-Path $candidate) {
        $certutilPath = $candidate
        break
    }
}

if (-not $certutilPath) {
    Write-Host "[WARN] Firefox certutil.exe not found. Skipping Firefox store import." -ForegroundColor Yellow
} else {
    Write-Host "Attempting to import into Firefox certificate store..." -ForegroundColor Cyan

    $profilesPath = Join-Path $env:APPDATA "Mozilla\Firefox\Profiles"
    if (-not (Test-Path $profilesPath)) {
        Write-Host "[WARN] Firefox profiles not found at $profilesPath" -ForegroundColor Yellow
    } else {
        $profiles = Get-ChildItem $profilesPath -Directory
        foreach ($profile in $profiles) {
            $dbPath = $profile.FullName
            Write-Host " → Adding cert to Firefox profile: $profile" -ForegroundColor Gray
            & $certutilPath -A -n "Fortinet_CA" -t "TCu,Cu,Tu" -i $certPath -d "sql:$dbPath" 2>$null
        }
        Write-Host "[OK] Certificate imported to all Firefox profiles (if any)." -ForegroundColor Green
    }
}

Write-Host "`nDone."
Pause
