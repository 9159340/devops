@echo off
setlocal

cd /d "%~dp0" || exit /b 1

set "GIT="
for /f "delims=" %%G in ('where git 2^>nul') do set "GIT=%%G" & goto :have_git
set "GIT=C:\Program Files\Git\cmd\git.exe"
:have_git
if not exist "%GIT%" (
  echo git not found
  exit /b 1
)

if not exist "tmp" mkdir "tmp"
set "LOG=tmp\git-upd.log"

echo [%date% %time%] start >> "%LOG%"

"%GIT%" add . >> "%LOG%" 2>&1 || goto :fail

"%GIT%" diff --cached --quiet
if errorlevel 1 (
  "%GIT%" commit -m "upd" >> "%LOG%" 2>&1 || goto :fail
) else (
  echo [%date% %time%] nothing to commit >> "%LOG%"
)

"%GIT%" push >> "%LOG%" 2>&1 || goto :fail

echo [%date% %time%] ok >> "%LOG%"
exit /b 0

:fail
echo [%date% %time%] failed >> "%LOG%"
exit /b 1
