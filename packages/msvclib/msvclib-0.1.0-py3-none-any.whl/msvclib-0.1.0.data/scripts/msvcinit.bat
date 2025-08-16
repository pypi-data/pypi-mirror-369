@echo off
echo Initializing MSVC environment...
call %~dp0\..\Lib\site-packages\msvclib\devcmd.bat
set DISTUTILS_USE_SDK=1
echo MSVC environment initialized successfully!
echo You can now use Visual Studio build tools in this command prompt.
