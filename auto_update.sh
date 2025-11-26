#!/bin/bash

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Get current commit hash before pull
OLD_HEAD=$(git rev-parse HEAD)

# Run git pull and capture output
OUTPUT=$(git pull)

# Get new commit hash after pull
NEW_HEAD=$(git rev-parse HEAD)

# If hashes match, no updates
if [ "$OLD_HEAD" == "$NEW_HEAD" ]; then
    echo "No updates."
    exit 0
fi

# Get the changes (commit messages)
CHANGES=$(git log --pretty=format:"• \`%h\` %s (%an)" $OLD_HEAD..$NEW_HEAD)

# Get machine hostname
HOSTNAME=$(hostname)

# Prepare the message content
MESSAGE="🚀 **Update pulled on \`$HOSTNAME\`!**

**Changes:**
$CHANGES

**Git Output:**
\`\`\`
$OUTPUT
\`\`\`"

# Use Python to safely send the webhook (handles JSON escaping)
python3 -c "
import os
import json
import urllib.request

webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
message = \"\"\"$MESSAGE\"\"\"

if webhook_url:
    payload = {
        'content': message
    }
    
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    
    try:
        urllib.request.urlopen(req)
        print('Notification sent to Discord.')
    except Exception as e:
        print(f'Failed to send notification: {e}')
else:
    print('DISCORD_WEBHOOK_URL not set, skipping notification.')
"
