$ApiBaseUrl = "http://localhost:8000"
$ApiKey = "change_me"
$ConfigPath = "config/demo_targets.json"

if (-not (Test-Path $ConfigPath)) {
    Write-Host "Config file not found: $ConfigPath" -ForegroundColor Red
    exit 1
}

$targets = Get-Content $ConfigPath -Raw | ConvertFrom-Json

foreach ($target in $targets) {
    Write-Host "Creating target: $($target.name)" -ForegroundColor Cyan

    $body = @{
        user_id = $target.user_id
        name = $target.name
        url = $target.url
        expected_status = $target.expected_status
        timeout_seconds = $target.timeout_seconds
        max_response_time_ms = $target.max_response_time_ms
        check_interval_seconds = $target.check_interval_seconds
        failure_threshold = $target.failure_threshold
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod `
            -Method Post `
            -Uri "$ApiBaseUrl/api/targets" `
            -Headers @{"X-API-Key" = $ApiKey} `
            -ContentType "application/json" `
            -Body $body

        Write-Host "Created: $($response.data.name) | ID: $($response.data.id)" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create target: $($target.name)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host "Import finished." -ForegroundColor Green