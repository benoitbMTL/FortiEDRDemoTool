# Ensure TLS 1.2 is used for secure HTTPS connections (required by GitHub)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Download and execute the Atomic Red Team installer script from GitHub
Invoke-Expression (Invoke-WebRequest 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing).Content

# Install the Invoke-AtomicRedTeam execution framework and the Atomics folder (tests + payloads), forcing reinstallation if needed
Install-AtomicRedTeam -getAtomics -Force
