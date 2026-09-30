param([string]$CoreConsole)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
$folder=Join-Path $root 'verification/revision-05'
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$source=Join-Path $root 'analysis/NGORO.source.dwg'
if(-not(Test-Path -LiteralPath $source)){$source=Join-Path $root 'web/dist/downloads/NGORO.source.dwg'}
$copy=Join-Path $folder 'NGORO.viewer-source.dwg'
$target=Join-Path $folder 'NGORO.viewer-source.dxf'
if(Test-Path -LiteralPath $target){throw 'DXF already exists; inspect rather than overwrite'}
$before=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
Copy-Item -LiteralPath $source -Destination $copy
if(-not $CoreConsole){$cadPath=(Get-Process acad -ErrorAction Stop | Select-Object -First 1).Path;$CoreConsole=Join-Path (Split-Path $cadPath) 'accoreconsole.exe'}
if(-not(Test-Path -LiteralPath $CoreConsole)){throw 'Supply installed AutoCAD Core Console path'}
$scriptPath=Join-Path $folder 'export.scr'
$targetCad=$target.Replace('\','/')
@('(setvar "FILEDIA" 0)','_DXFOUT',('"'+$targetCad+'"'),'16','_QUIT','_Y','') | Set-Content -LiteralPath $scriptPath -Encoding ascii
& $CoreConsole /i $copy /s $scriptPath /l en-US | Out-File -LiteralPath (Join-Path $folder 'core-export.log') -Encoding utf8
if(-not(Test-Path -LiteralPath $target)){throw 'DXF not written; inspect core-export.log'}
Write-Output ('Source copy exported to DXF: '+(Get-Item -LiteralPath $target).Length+' bytes')
$after=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
if($before -ne $after){throw 'Source hash mismatch'}
@{source_sha256=$before;unchanged=$true;dxf=$target} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'source-preservation.json') -Encoding utf8
