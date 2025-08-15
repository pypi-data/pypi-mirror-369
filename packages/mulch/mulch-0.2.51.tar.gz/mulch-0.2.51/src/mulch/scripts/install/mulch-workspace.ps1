param (
    [string]$path
)

if (-Not (Test-Path -Path $path)) {
    Write-Error "Path not found: $path"
    return
}

Write-Output "Processing path: $path"

Set-Location -Path $path

## Where does mulch.exe live on a Windows system
$env:PATH += ";$env:USERPROFILE\.local\bin"

## Run mulch workspace, with flags relevant to a user facing context menu right-click tool
mulch workspace --here --pattern new # --pattern date

Read-Host -Prompt "Press Enter to exit"