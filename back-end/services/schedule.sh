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
CRON_JOB1="1 0 * * * /bin/bash -c 'source /path/to/venv/bin/activate && python3 $SCRIPT1_PATH' "
CRON_JOB2="0 7 * * * /bin/bash -c 'source /path/to/venv/bin/activate && python3 $SCRIPT2_PATH' "

# Create a temporary file for the crontab
CRON_TEMP=$(mktemp)

# Write out current crontab
crontab -l > $CRON_TEMP 2>/dev/null

# Ensure the cron jobs do not already exist before adding
grep -F "$SCRIPT1_PATH" $CRON_TEMP || echo "$CRON_JOB1" >> $CRON_TEMP
grep -F "$SCRIPT2_PATH" $CRON_TEMP || echo "$CRON_JOB2" >> $CRON_TEMP

# Install the new crontab
crontab $CRON_TEMP

# Remove the temporary file
rm $CRON_TEMP

echo "Cron jobs added successfully."

crontab -l
