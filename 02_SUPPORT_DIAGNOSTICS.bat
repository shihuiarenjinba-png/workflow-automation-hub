@echo off
setlocal
cd /d "%~dp0"
set "APP=%~dp0WorkflowAutomationHub.exe"
set "REPORT=%~dp0support_report.txt"

if not exist "%APP%" (
  echo WorkflowAutomationHub.exe was not found in this folder.
  echo このフォルダーに WorkflowAutomationHub.exe がありません。
  pause
  exit /b 2
)

if exist "%REPORT%" del /q "%REPORT%" >nul 2>&1
"%APP%" --diagnose "%REPORT%"
set "RC=%ERRORLEVEL%"

if exist "%REPORT%" (
  echo.
  echo Support report created:
  echo %REPORT%
  echo サポート用レポートを作成しました。
) else (
  echo.
  echo Support report could not be created.
  echo サポート用レポートを作成できませんでした。
)

echo.
echo Do not send OAuth JSON or Google tokens. Send support_report.txt only.
echo OAuth JSON や Google トークンは送らず、support_report.txt のみ送ってください。
pause
exit /b %RC%
