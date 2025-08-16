# MarketSwimmer Cleanup Script
# Removes analysis output folders and text files from prior runs

Write-Host "MarketSwimmer Cleanup Script" -ForegroundColor Green
Write-Host "Removing analysis output folders and text files..." -ForegroundColor Yellow

# Define folders to delete
$foldersToDelete = @(
    "analysis_output",
    "charts", 
    "data",
    "downloaded_files"
)

# Delete folders if they exist
foreach ($folder in $foldersToDelete) {
    if (Test-Path $folder) {
        Write-Host "Deleting folder: $folder" -ForegroundColor Cyan
        Remove-Item -Path $folder -Recurse -Force
        Write-Host "✓ Deleted: $folder" -ForegroundColor Green
    } else {
        Write-Host "✓ Folder not found (already clean): $folder" -ForegroundColor Gray
    }
}

# Delete all .txt files in the base directory
$txtFiles = Get-ChildItem -Path "." -Filter "*.txt" -File
if ($txtFiles.Count -gt 0) {
    Write-Host "Deleting .txt files in base directory:" -ForegroundColor Cyan
    foreach ($file in $txtFiles) {
        Write-Host "  - $($file.Name)" -ForegroundColor Yellow
        Remove-Item -Path $file.FullName -Force
    }
    Write-Host "✓ Deleted $($txtFiles.Count) .txt files" -ForegroundColor Green
} else {
    Write-Host "✓ No .txt files found in base directory" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Cleanup completed successfully!" -ForegroundColor Green
Write-Host "All analysis output folders and text files have been removed." -ForegroundColor White
