# ========================================
# CLEANUP SCRIPT - Remove Unwanted Files
# ========================================
# Run this script to clean up the project
# WARNING: This will delete files permanently!
# ========================================

Write-Host "🧹 Starting Project Cleanup..." -ForegroundColor Cyan
Write-Host ""

$projectRoot = "d:\devotinal2\project"
Set-Location $projectRoot

# Track statistics
$filesDeleted = 0
$foldersDeleted = 0

# ========================================
# 1. Remove Python Cache Files
# ========================================
Write-Host "📦 Removing Python cache files..." -ForegroundColor Yellow

$pycachePatterns = @("__pycache__", "*.pyc", "*.pyo", "*.pyd")

foreach ($pattern in $pycachePatterns) {
    $items = Get-ChildItem -Path $projectRoot -Recurse -Include $pattern -Force -ErrorAction SilentlyContinue
    
    foreach ($item in $items) {
        try {
            if ($item.PSIsContainer) {
                Remove-Item -Path $item.FullName -Recurse -Force
                $foldersDeleted++
                Write-Host "  ✓ Deleted folder: $($item.FullName)" -ForegroundColor Green
            } else {
                Remove-Item -Path $item.FullName -Force
                $filesDeleted++
                Write-Host "  ✓ Deleted file: $($item.FullName)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ✗ Failed to delete: $($item.FullName)" -ForegroundColor Red
        }
    }
}

# ========================================
# 2. Remove SQLite Journal Files
# ========================================
Write-Host ""
Write-Host "📄 Removing SQLite journal files..." -ForegroundColor Yellow

$journalFiles = Get-ChildItem -Path $projectRoot -Recurse -Filter "*.sqlite3-journal" -Force -ErrorAction SilentlyContinue

foreach ($file in $journalFiles) {
    try {
        Remove-Item -Path $file.FullName -Force
        $filesDeleted++
        Write-Host "  ✓ Deleted: $($file.FullName)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to delete: $($file.FullName)" -ForegroundColor Red
    }
}

# ========================================
# 3. Remove Log Files
# ========================================
Write-Host ""
Write-Host "📝 Removing log files..." -ForegroundColor Yellow

$logPatterns = @("*.log",  "*.log.*")

foreach ($pattern in $logPatterns) {
    $logFiles = Get-ChildItem -Path $projectRoot -Recurse -Include $pattern -Force -ErrorAction SilentlyContinue
    
    foreach ($file in $logFiles) {
        try {
            Remove-Item -Path $file.FullName -Force
            $filesDeleted++
            Write-Host "  ✓ Deleted: $($file.FullName)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Failed to delete: $($file.FullName)" -ForegroundColor Red
        }
    }
}

# ========================================
# 4. Remove Duplicate/Old App Folders
# ========================================
Write-Host ""
Write-Host "📁 Checking for duplicate project folders..." -ForegroundColor Yellow

# Check if there are old/duplicate folders
$duplicateFolders = @()

if (Test-Path "$projectRoot\karya_siddhi") {
    Write-Host "  ⚠ Found: karya_siddhi folder" -ForegroundColor Yellow
    $duplicateFolders += "karya_siddhi"
}

if (Test-Path "$projectRoot\my_project") {
    Write-Host "  ⚠ Found: my_project folder" -ForegroundColor Yellow
    $duplicateFolders += "my_project"
}

if ($duplicateFolders.Count -gt 0) {
    Write-Host ""
    Write-Host "  ⚠ WARNING: Found potential duplicate/old project folders:" -ForegroundColor Red
    foreach ($folder in $duplicateFolders) {
        Write-Host "    - $folder" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "  These folders may contain old code or duplicates." -ForegroundColor Yellow
    Write-Host "  Review them manually before deleting!" -ForegroundColor Yellow
    Write-Host "  To delete manually, run:" -ForegroundColor Cyan
    foreach ($folder in $duplicateFolders) {
        Write-Host "    Remove-Item -Path '$projectRoot\$folder' -Recurse -Force" -ForegroundColor Cyan
    }
}

# ========================================
# 5. OLD Content Folder (After Migration Complete)
# ========================================
Write-Host ""
Write-Host "📂 Checking old content folder..." -ForegroundColor Yellow

$oldContentPath = "$projectRoot\templates\content"

if (Test-Path $oldContentPath) {
    Write-Host "  ⚠ Found: templates/content folder (OLD structure)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  ⚠ WARNING: This folder contains old mixed DTL+HTML files" -ForegroundColor Red
    Write-Host "  The new CMS structure is in: templates/cms/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  After verifying everything works, delete it with:" -ForegroundColor Yellow
    Write-Host "    Remove-Item -Path '$oldContentPath' -Recurse -Force" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  ⚠ DO NOT DELETE YET - Test the new structure first!" -ForegroundColor Red
}

# ========================================
# 6. Remove Empty Directories
# ========================================
Write-Host ""
Write-Host "📂 Removing empty directories..." -ForegroundColor Yellow

$emptyDirs = Get-ChildItem -Path $projectRoot -Recurse -Directory -Force -ErrorAction SilentlyContinue | 
             Where-Object { (Get-ChildItem -Path $_.FullName -Force -ErrorAction SilentlyContinue).Count -eq 0 }

foreach ($dir in $emptyDirs) {
    try {
        Remove-Item -Path $dir.FullName -Force
        $foldersDeleted++
        Write-Host "  ✓ Deleted empty folder: $($dir.FullName)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to delete: $($dir.FullName)" -ForegroundColor Red
    }
}

# ========================================
# 7. Remove .git folder (if exists and unwanted)
# ========================================
Write-Host ""
Write-Host "🔧 Checking for .git folder..." -ForegroundColor Yellow

$gitPath = "$projectRoot\.git"

if (Test-Path $gitPath) {
    Write-Host "  ℹ Found .git folder (Git repository)" -ForegroundColor Cyan
    Write-Host "  If you want to remove version control, run:" -ForegroundColor Yellow
    Write-Host "    Remove-Item -Path '$gitPath' -Recurse -Force" -ForegroundColor Cyan
    Write-Host "  (Skipping automatic deletion)" -ForegroundColor Yellow
}

# ========================================
# SUMMARY
# ========================================
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Statistics:" -ForegroundColor White
Write-Host "  📄 Files deleted: $filesDeleted" -ForegroundColor Green
Write-Host "  📁 Folders deleted: $foldersDeleted" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test your website: python manage.py runserver" -ForegroundColor Cyan
Write-Host "  2. Verify all pages work correctly" -ForegroundColor Cyan
Write-Host "  3. Review duplicate folders before deleting" -ForegroundColor Cyan
Write-Host "  4. Keep backups of important files!" -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan

# Optional: Pause to review output
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
