# Configure $PROFILE for future sessions

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
