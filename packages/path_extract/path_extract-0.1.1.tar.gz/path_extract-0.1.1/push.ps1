. .\env.ps1 #set environment variables.. 
Remove-Item -Path ".\dist" -Recurse
uv build
uv version --bump patch
uv publish 