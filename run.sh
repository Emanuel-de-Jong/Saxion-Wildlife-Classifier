#!/bin/bash
set +v

poetry run uvicorn main:app --port 8000 --log-level error

# print error.log if it exists
export error_file=error.log
if [ -e "$error_file" ]; then
    cat "$error_file"
fi
