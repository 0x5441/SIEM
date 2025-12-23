# ===== SETTINGS =====
$Server    = "http://192.168.100.173:8000/logs"
$LogName   = "Security"     # Security | System | Application
$MaxEvents = 50
$Interval  = 30             # بالثواني

Write-Host "Starting Windows log sender (every $Interval seconds)..."

while ($true) {

    try {
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
         -Body $json `
         -ErrorAction Stop

        Write-Host "$(Get-Date -Format 'HH:mm:ss') - Logs sent successfully"

    } catch {
        Write-Host "$(Get-Date -Format 'HH:mm:ss') - Error sending logs"
    }

    # انتظار 30 ثانية
    Start-Sleep -Seconds $Interval
}