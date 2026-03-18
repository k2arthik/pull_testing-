# Quick Cleanup Script for Unwanted Files
$projectRoot = "d:\devotinal2\project"
Set-Location $projectRoot

# Remove pycache
Get-ChildItem -Path $projectRoot -Recurse -Include "__pycache__", "*.pyc", "*.pyo", "*.pyd" -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host "Cleaned Python cache."

# Remove SQLite journals
Get-ChildItem -Path $projectRoot -Recurse -Filter "*.sqlite3-journal" -Force -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host "Cleaned SQLite journals."

# Remove logs
Get-ChildItem -Path $projectRoot -Recurse -Include "*.log", "*.log.*" -Force -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host "Cleaned logs."
