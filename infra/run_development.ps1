param(
    [switch]$Setup = $false,
    [switch]$ClearData = $false,
    [string]$EnvFile = ".env_dev"
)

Write-Host "Deploying Foodgram for local development"
$Infra = $PSScriptRoot
$Backend = Resolve-Path "$Infra/../backend"
$Initdata = Resolve-Path "$Infra/../data/ingredients.json"
$ManagePy = Resolve-Path "$Backend/foodgram/manage.py"
$Venv = Resolve-Path "$Backend/venv/Scripts/Activate.ps1"
$Requirements = Resolve-Path "$Backend/requirements.txt"

Write-Host "** Activating virtual environment **"
. $Venv | Out-Null

if ($Setup) {
Write-Host "** Installing virtual environment packages **"
pip install -r $Requirements | Out-Null
}

if ($ClearData) {
Write-Host "** Clearing previous database data **"

"from core.models import Ingredient; Ingredient.objects.all().delete()" | py $ManagePy shell | Out-Null

"from django.contrib.auth import get_user_model; User = get_user_model(); `
usernames_list = ['root', 'vasya.ivanov', 'second-user', 'third-user-username', 'NoEmail', 'NoFirstName', 'NoLastName', 'NoPassword', 'TooLongEmail', `
'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-', `
'TooLongFirstName', 'TooLongLastName', 'InvalidU`$ername', 'EmailInUse']; `
delete_num, _ = User.objects.filter(username__in=usernames_list).delete(); `
exit(1) if not delete_num else exit(0);" | py $ManagePy shell | Out-Null

}

Write-Host "** Setting up environment variables **"
Get-Content $EnvFile | ForEach-Object {
    $name, $value = $_.split('=')

    if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) { return }

    Set-Content env:\$name $value
}

Set-Content env:DJANGO_IS_DEBUG True
Set-Content env:DJANGO_IS_SQLITE3 True

if ($Setup) {
Write-Host "** Setting up migrations **"
py $ManagePy migrate | Out-Null

Write-Host "** Creating superuser root@foodgram.com:root **"
"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('root', 'root@foodgram.com', 'root')" | py $ManagePy shell | Out-Null

Write-Host "** Importing ingredients data **"
"from core.models import Ingredient; from json import loads; `
fl = open(r'$Initdata', mode='r', encoding='utf-8'); jsn = loads(fl.read()); fl.close(); `
Ingredient.objects.bulk_create([Ingredient(name=item['name'], measurement_unit=item['measurement_unit']) for item in jsn]);" | py $ManagePy shell | Out-Null

Write-Host "** Collecting static **"
py $ManagePy collectstatic --noinput | Out-Null
}

Write-Host "** Running **"
py $ManagePy runserver
