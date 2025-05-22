param(
    [switch]$Setup = $false
)

Write-Host "Deploying Foodgram for production server"
$MediaVolume = Resolve-Path "$PSScriptRoot/../data/volume"

Push-Location $PSScriptRoot

if ($Setup) {

Write-Host "** Running: docker compose up --build **"
docker compose up --force-recreate --build -d

Write-Host "** Waiting for postgres to start up **"
Start-Sleep -Seconds 10

Write-Host "** Setting up migrations **"
docker compose exec backend python foodgram/manage.py migrate | Out-Null

Write-Host "** Copying volume data **"
docker cp $MediaVolume/. foodgram-backend:/app/foodgram/media

Write-Host "** Importing fixture data **"
docker compose exec backend python foodgram/manage.py loaddata data/initial_data.json | Out-Null

Write-Host "** Collecting static **"
docker compose exec backend python foodgram/manage.py collectstatic --noinput | Out-Null
} else {
Write-Host "** Running: docker compose up **"
docker compose up -d
}

Pop-Location

Write-Host "** Success **"