$SCRIPT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Set-Location $SCRIPT_DIR

docker-compose up -d --build

docker image prune -f
