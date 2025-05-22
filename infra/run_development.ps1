param(
    [switch]$Setup = $false,
    [string]$EnvFile = ".env"
)

Write-Host "Deploying Foodgram for local development"
$Infra = $PSScriptRoot
$Backend = Resolve-Path "$Infra/../backend"
$Initdata = Resolve-Path "$Backend/data/initial_data.json"
$ManagePy = Resolve-Path "$Backend/foodgram/manage.py"
$MediaVolume = Resolve-Path "$Infra/../data/volume"
$MediaBackend = "$Backend/foodgram/media"
$Requirements = Resolve-Path "$Backend/requirements.txt"
$Env = Resolve-Path "$PSScriptRoot/$EnvFile"

if ($Setup) {
Write-Host "** Creating virtual environment **"
Push-Location $Backend
py -m venv venv
Pop-Location
}
$Venv = Resolve-Path "$Backend/venv/Scripts/Activate.ps1"

Write-Host "** Activating virtual environment **"
. $Venv | Out-Null

Write-Host "** Setting up environment variables **"
Get-Content $Env | ForEach-Object {
    $name, $value = $_.split('=')

    if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) { return }

    Set-Content env:\$name $value
}

Set-Content env:DJANGO_IS_DEBUG True
Set-Content env:DJANGO_IS_SQLITE3 True

if ($Setup) {
Write-Host "** Installing virtual environment packages **"
pip install -r $Requirements | Out-Null

Write-Host "** Setting up migrations **"
py $ManagePy migrate | Out-Null

Write-Host "** Copying volume data **"
Copy-Item $MediaVolume $MediaBackend -Recurse -ErrorAction Ignore

Write-Host "** Importing fixture data **"
py $ManagePy loaddata $Initdata

Write-Host "** Collecting static **"
py $ManagePy collectstatic --noinput | Out-Null
}

Write-Host "** Running **"
py $ManagePy runserver
