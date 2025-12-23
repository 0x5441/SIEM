# ===== Settings =====
$LogName   = "Security"   # Security | System | Application
$MaxEvents = 100          # عدد اللوقز
$OutFile   = "C:\SIEM\events.json"

# تأكد أن المجلد موجود
New-Item -ItemType Directory -Force -Path "C:\SIEM" | Out-Null

# سحب اللوقز
$events = Get-WinEvent -LogName $LogName -MaxEvents $MaxEvents |
Select-Object @{
    Name="timestamp"; Expression={$_.TimeCreated}
}, @{
    Name="event_id"; Expression={$_.Id}
}, @{
    Name="level"; Expression={$_.LevelDisplayName}
}, @{
    Name="provider"; Expression={$_.ProviderName}
}, @{
    Name="message"; Expression={$_.Message}
}

# تحويل إلى JSON
$events | ConvertTo-Json -Depth 4 | Out-File $OutFile -Encoding utf8

Write-Host "✔ Events exported to $OutFile"
