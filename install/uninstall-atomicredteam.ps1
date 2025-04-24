Write-Host "Uninstalling Atomic Red Team..." -ForegroundColor Cyan

# Remove AtomicRedTeam folder if present
$atomicFolder = "C:\AtomicRedTeam"
if (Test-Path $atomicFolder) {
    try {
        Remove-Item -Recurse -Force $atomicFolder -ErrorAction Stop
        Write-Host "Removed folder: $atomicFolder"
    } catch {
        Write-Warning "Could not remove $atomicFolder. It may be in use or locked."
    }
} else {
    Write-Host "Atomic Red Team folder not found."
}

# Try to uninstall powershell-yaml module
try {
    powershell -NoProfile -Command "Uninstall-Module powershell-yaml -Force -ErrorAction Stop"
    Write-Host "powershell-yaml module uninstalled."
} catch {
    Write-Host "powershell-yaml module not found or already removed."
}

Write-Host "Uninstallation complete." -ForegroundColor Green
