[CmdletBinding()]
param(
    [switch]$NoBackend,
    [switch]$NoFrontend
)

$ErrorActionPreference = 'Stop'

function Set-ProcessEnvironmentFromFile {
    param(
        [string]$FilePath
    )

    if (-not (Test-Path -LiteralPath $FilePath)) {
        Write-Verbose "No environment file found at $FilePath"
        return
    }

    Write-Host "Loading environment variables from $FilePath" -ForegroundColor Cyan
    foreach ($line in Get-Content -LiteralPath $FilePath) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
        if ($trimmed.StartsWith('#')) { continue }
        $parts = $trimmed.Split('=', 2)
        if ($parts.Length -ne 2) { continue }

        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")
        if (-not $name) { continue }

        $existingItem = Get-Item -Path "env:$name" -ErrorAction SilentlyContinue
        if (-not $existingItem -or [string]::IsNullOrEmpty($existingItem.Value)) {
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

function Assert-Command {
    param(
        [Parameter(Mandatory = $true)][string]$Name
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found on PATH."
    }
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot

Set-ProcessEnvironmentFromFile -FilePath (Join-Path $scriptRoot '.env')

if (-not $NoBackend) {
    Assert-Command -Name 'python'
}

if (-not $NoFrontend) {
    Assert-Command -Name 'npm'
}

$apiHost = if ($env:OV_TRADER_API_HOST) { $env:OV_TRADER_API_HOST } else { '127.0.0.1' }
$apiPort = if ($env:OV_TRADER_API_PORT) { $env:OV_TRADER_API_PORT } else { '8000' }
$webHost = if ($env:OV_TRADER_WEB_HOST) { $env:OV_TRADER_WEB_HOST } else { '127.0.0.1' }
$webPort = if ($env:OV_TRADER_WEB_PORT) { $env:OV_TRADER_WEB_PORT } else { '3000' }

if (-not $env:NEXT_PUBLIC_API_BASE_URL) {
    $env:NEXT_PUBLIC_API_BASE_URL = "http://$apiHost`:$apiPort"
}

$processes = @()

if (-not $NoBackend) {
    Write-Host "Starting FastAPI backend on http://$apiHost`:$apiPort" -ForegroundColor Green
    $backendArgs = @('-m', 'uvicorn', 'ov_trader.server.api:app', '--reload', '--host', $apiHost, '--port', $apiPort)
    $backend = Start-Process -FilePath 'python' -ArgumentList $backendArgs -WorkingDirectory $scriptRoot -PassThru -NoNewWindow
    $processes += $backend
}

if (-not $NoFrontend) {
    Write-Host "Starting Next.js frontend on http://$webHost`:$webPort" -ForegroundColor Green
    $webDirectory = Join-Path $scriptRoot 'web'
    $frontendArgs = @('run', 'dev', '--', '--hostname', $webHost, '--port', $webPort)
    $frontend = Start-Process -FilePath 'npm' -ArgumentList $frontendArgs -WorkingDirectory $webDirectory -PassThru -NoNewWindow
    $processes += $frontend
}

if ($processes.Count -eq 0) {
    Write-Warning 'No processes were started. Use the switches to enable the backend and/or frontend.'
    exit 0
}

Write-Host 'Press Ctrl+C to stop both services.' -ForegroundColor Yellow

try {
    while ($true) {
        Start-Sleep -Seconds 1
        foreach ($proc in $processes) {
            if ($proc.HasExited) {
                throw "Process $($proc.ProcessName) (PID $($proc.Id)) exited with code $($proc.ExitCode)."
            }
        }
    }
}
catch {
    Write-Warning $_
}
finally {
    foreach ($proc in $processes) {
        if ($null -ne $proc -and -not $proc.HasExited) {
            Write-Host "Stopping $($proc.ProcessName) (PID $($proc.Id))" -ForegroundColor DarkYellow
            try {
                $proc | Stop-Process -Force -ErrorAction SilentlyContinue
            }
            catch {
                Write-Verbose "Failed to stop process $($proc.ProcessName): $_"
            }
        }
    }
}
