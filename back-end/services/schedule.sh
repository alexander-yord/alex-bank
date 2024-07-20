#!/bin/bash

# Define the paths to the Python scripts
SCRIPT1="updateStatuses.py"
SCRIPT2="sendEmails.py"

# Check if both scripts exist in the current directory
if [[ ! -f "$SCRIPT1" ]] || [[ ! -f "$SCRIPT2" ]]; then
  echo "One or both Python scripts are missing in the current directory."
  exit 1
fi

# Get the absolute paths of the scripts
SCRIPT1_PATH=$(pwd)/$SCRIPT1
SCRIPT2_PATH=$(pwd)/$SCRIPT2

# Define the cron job lines
CRON_JOB1="1 0 * * * source $(pwd)/../venv/bin/activate && /usr/bin/python3 $SCRIPT1_PATH"
CRON_JOB2="0 8 * * * source $(pwd)/../venv/bin/activate && /usr/bin/python3 $SCRIPT2_PATH"

# Check if the cron jobs already exist to avoid duplication
(crontab -l 2>/dev/null | grep -F "$SCRIPT1_PATH" >/dev/null) || (crontab -l; echo "$CRON_JOB1") | crontab -
(crontab -l 2>/dev/null | grep -F "$SCRIPT2_PATH" >/dev/null) || (crontab -l; echo "$CRON_JOB2") | crontab -

echo "Cron jobs added successfully."
