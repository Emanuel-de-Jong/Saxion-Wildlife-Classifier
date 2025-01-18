@echo off

poetry run uvicorn main:app --port 8000 --log-level error

REM print error.log if it exists
set error_file=error.log
if exist %error_file% (
    type %error_file%
)
