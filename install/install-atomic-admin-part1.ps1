Write-Host "Checking PowerShellGet version..." -ForegroundColor Cyan

$psGet = Get-Module -ListAvailable PowerShellGet | Sort-Object Version -Descending | Select-Object -First 1

if ($psGet.Version -lt [version]"2.0.0") {
    Write-Host "Installing latest PowerShellGet..." -ForegroundColor Yellow
    Install-Module PowerShellGet -Force -AllowClobber
    Write-Host "PowerShellGet updated." -ForegroundColor Green
} else {
    Write-Host "PowerShellGet is up to date." -ForegroundColor Green
}

Write-Host "`nNow run 'install-atomic-user.ps1' from a normal PowerShell window (non-admin)." -ForegroundColor Cyan
