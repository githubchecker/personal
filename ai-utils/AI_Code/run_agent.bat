@echo off
:: ==========================================================================
:: AI Agent Launcher (Updated Logic)
:: --------------------------------------------------------------------------
:: This script runs the agent.py script from a separate utility folder.
::
:: DEFAULT BEHAVIOR: Scans ALL project files.
::
:: To scan only changed files, use the --changes flag.
:: Example: run_agent.bat --changes
::
:: All arguments are forwarded to the agent.py script.
:: ==========================================================================

:: Define the relative path from the project directory to the agent script
set AGENT_PATH=../Utils/AI_Code/agent.py

:: Announce what we are doing
echo Running AI Agent from: %AGENT_PATH%
echo Operating on project directory: %cd%
echo(

:: Execute the Python script, passing along all command-line arguments (%*)
python "%AGENT_PATH%" %*

echo(
echo Agent has finished.

pause