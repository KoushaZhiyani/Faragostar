# agent.ps1
param(
    [int]$Port = 5000
)

Add-Type -AssemblyName System.Web

# ========== توابع جمع‌آوری داده ==========

function Get-CPUPercent {
    # با PerformanceCounter CPU کلی (درصد بار فعلی)
    $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    return [math]::Round($cpu, 2)
}

function Get-MemoryInfo {
    $os = Get-CimInstance Win32_OperatingSystem
    $total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $free  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $used  = [math]::Round($total - $free, 2)
    $percent = if ($total -gt 0) { [math]::Round(($used / $total) * 100, 2) } else { 0 }

    return @{
        total_gb = $total
        used_gb  = $used
        percent  = $percent
    }
}

function Get-DiskInfo {
    param(
        [string]$DriveLetter = "D:"
    )
    $drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$DriveLetter'"
    if (-not $drive) {
        return @{ error = "Drive $DriveLetter not found" }
    }
    $total = [math]::Round($drive.Size / 1GB, 2)
    $free  = [math]::Round($drive.FreeSpace / 1GB, 2)
    $used  = [math]::Round($total - $free, 2)
    $percent = if ($total -gt 0) { [math]::Round(($used / $total) * 100, 2) } else { 0 }

    return @{
        drive    = $DriveLetter
        total_gb = $total
        used_gb  = $used
        free_gb  = $free
        percent  = $percent
    }
}

# ========== HTTP Listener ==========

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://0.0.0.0:$Port/")
$listener.Start()

Write-Host "Agent PowerShell running on http://0.0.0.0:$Port"
Write-Host "Available endpoints:"
Write-Host "  GET /cpu"
Write-Host "  GET /memory"
Write-Host "  GET /disk?drive=D:"

while ($listener.IsListening) {
    $context = $listener.GetContext()   # منتظر درخواست
    $request = $context.Request
    $response = $context.Response

    # فقط GET مجاز است
    if ($request.HttpMethod -ne "GET") {
        $response.StatusCode = 405
        $msg = @{ error = "Method not allowed" } | ConvertTo-Json
        $buf = [System.Text.Encoding]::UTF8.GetBytes($msg)
        $response.OutputStream.Write($buf, 0, $buf.Length)
        $response.Close()
        continue
    }

    $path = $request.Url.AbsolutePath
    # پارامتر drive
    $drive = $request.QueryString["drive"]
    if (-not $drive) { $drive = "D:" }

    try {
        switch ($path) {
            "/cpu" {
                $data = @{ cpu_percent = Get-CPUPercent }
            }
            "/memory" {
                $data = Get-MemoryInfo
            }
            "/disk" {
                $data = Get-DiskInfo -DriveLetter $drive
            }
            default {
                $response.StatusCode = 404
                $data = @{ error = "Path not found" }
            }
        }
    }
    catch {
        $response.StatusCode = 500
        $data = @{ error = $_.Exception.Message }
    }

    # ارسال JSON
    $json = $data | ConvertTo-Json -Compress
    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
    $response.ContentType = "application/json"
    $response.ContentLength64 = $buffer.Length
    $response.OutputStream.Write($buffer, 0, $buffer.Length)
    $response.Close()
}

$listener.Stop()
