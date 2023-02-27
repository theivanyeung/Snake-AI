
@REM For firebase training use only

@echo off

set count=0
set max_count=91

:loop
if %count% GEQ %max_count% goto end

python agent.py

set /a count+=1
goto loop

:end