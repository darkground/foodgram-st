param(
    [switch]$Setup = $false
)

Write-Host "Deploying Foodgram for production server"
$Infra = $PSScriptRoot
$Initdata = "/app/data/ingredients.json"

if ($Setup) {
Write-Host "** Running: docker compose up (setup)**"
docker compose up --force-recreate --build -d
} else {
Write-Host "** Running: docker compose up (no setup)**"
docker compose up -d
}

if ($Setup) {
Write-Host "** Setting up migrations **"
docker compose exec backend python foodgram/manage.py migrate | Out-Null

Write-Host "** Creating superuser root@foodgram.com:root **"
"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('root', 'root@foodgram.com', 'root')" | docker compose exec backend python foodgram/manage.py shell | Out-Null

Write-Host "** Importing ingredients data **"
"from core.models import Ingredient; from json import loads; `
fl = open(r'$Initdata', mode='r', encoding='utf-8'); jsn = loads(fl.read()); fl.close(); `
Ingredient.objects.bulk_create([Ingredient(name=item['name'], measurement_unit=item['measurement_unit']) for item in jsn]);" | docker compose exec backend python foodgram/manage.py shell | Out-Null

Write-Host "** Collecting static **"
docker compose exec backend python foodgram/manage.py collectstatic --noinput | Out-Null
}

Write-Host "** Success **"