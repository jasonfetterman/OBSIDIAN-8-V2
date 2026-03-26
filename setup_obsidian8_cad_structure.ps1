# OBSIDIAN-8 CAD Folder Setup Script

$root = "C:\Users\twitc\OBSIDIAN-8_V3_MASTER_STRUCTURE\CAD"

New-Item -ItemType Directory -Force -Path "$root\Assemblies"
New-Item -ItemType Directory -Force -Path "$root\Parts"
New-Item -ItemType Directory -Force -Path "$root\Hardware"
New-Item -ItemType Directory -Force -Path "$root\Electronics"
New-Item -ItemType Directory -Force -Path "$root\Exports"

Write-Host "OBSIDIAN-8 CAD structure created successfully."