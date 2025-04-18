# Check if the latest version of PowerShell 7 is already installed

# Get installed version (if PowerShell 7 is present)
$installedVersion = $null
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    $installedVersion = & pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion.ToString()'
}

# Get latest version from GitHub
$latestRelease = Invoke-RestMethod https://api.github.com/repos/PowerShell/PowerShell/releases/latest
$latestVersion = $latestRelease.tag_name.TrimStart("v")

if ($installedVersion -eq $latestVersion) {
    Write-Host "Latest PowerShell version ($latestVersion) is already installed. Exiting." -ForegroundColor Green
    return
}

# Download and install latest version
$asset = $latestRelease.assets | Where-Object { $_.name -like '*win-x64.msi' } | Select-Object -First 1
$installerPath = "$env:TEMP\powershell-$latestVersion.msi"

Write-Host "Downloading PowerShell $latestVersion..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $installerPath

Write-Host "Installing PowerShell $latestVersion..." -ForegroundColor Cyan
Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /qn" -Wait

Write-Host "Installation complete. You can now launch 'PowerShell 7'." -ForegroundColor Green
