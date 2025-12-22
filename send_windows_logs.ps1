# ===== SETTINGS =====
$Server = "http://192.168.100.173:8000/logs"
$LogName = "Security"     # Security | System | Application
$MaxEvents = 50

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
$json = $events | ConvertTo-Json -Depth 4

# إرسال للسيرفر
Invoke-WebRequest `
 -Uri $Server `
 -Method POST `
 -Headers @{ "Content-Type"="application/json" } `
 -Body $json

Write-Host "Logs sent successfully"

