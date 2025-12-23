$ServerURL = "http://192.168.100.173:8000/logs"
$EventID   = 4625
$SleepSec  = 2

Write-Host "[*] Monitoring FAILED LOGIN events (4625)..."

$LastRecordId = 0

while ($true) {

    $events = Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        Id      = $EventID
    } | Where-Object { $_.RecordId -gt $LastRecordId }

    foreach ($event in $events) {

        $LastRecordId = $event.RecordId

        $data = @{
            event_id = $event.Id
            time     = $event.TimeCreated
            machine  = $event.MachineName
            recordId = $event.RecordId
            message  = $event.FormatDescription()
        }

        $json = $data | ConvertTo-Json -Depth 3

        Invoke-RestMethod `
            -Uri $ServerURL `
            -Method POST `
            -Body $json `
            -ContentType "application/json"

        Write-Host "🚨 FAILED LOGIN sent (RecordId=$($event.RecordId))"
    }

    Start-Sleep -Seconds $SleepSec
}
