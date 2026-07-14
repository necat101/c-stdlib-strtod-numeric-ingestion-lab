@echo off
setlocal

REM Find zig
if defined ZIG_BIN if exist "%ZIG_BIN%" (
  set "ZIG=%ZIG_BIN%"
  goto zig_found
)
where zig >nul 2>nul
if %ERRORLEVEL%==0 (
  for /f "delims=" %%i in ('where zig') do set "ZIG=%%i" & goto zig_found
)
if exist "%USERPROFILE%\.local\bin\zig.exe" set "ZIG=%USERPROFILE%\.local\bin\zig.exe" & goto zig_found
if exist "%USERPROFILE%\bin\zig.exe" set "ZIG=%USERPROFILE%\bin\zig.exe" & goto zig_found
echo zig not found (tried %%ZIG_BIN%%, where zig, %%USERPROFILE%%\.local\bin\zig.exe, %%USERPROFILE%%\bin\zig.exe) 1>&2
exit /b 1
:zig_found

REM Find python
if defined PYTHON_BIN if exist "%PYTHON_BIN%" (
  set "PY=%PYTHON_BIN%"
  goto py_found
)
where python3 >nul 2>nul
if %ERRORLEVEL%==0 (
  for /f "delims=" %%i in ('where python3') do set "PY=%%i" & goto py_found
)
where python >nul 2>nul
if %ERRORLEVEL%==0 (
  for /f "delims=" %%i in ('where python') do set "PY=%%i" & goto py_found
)
echo python not found 1>&2
exit /b 1
:py_found

echo zig:
"%ZIG%" version
echo python:
"%PY%" --version

"%ZIG%" cc -std=c11 -O2 -Wall -Wextra -Wpedantic strtod_lab.c -lm -o strtod_lab_check.exe
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
del strtod_lab_check.exe 2>nul
echo compile check: ok

"%PY%" -m py_compile run_lab.py test_lab.py
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
echo py_compile: ok

"%PY%" run_lab.py
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
echo.
"%PY%" -m unittest -v
