#!/bin/bash

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run git pull and capture output
OUTPUT=$(git pull)

# If output contains "Already up to date.", stop here
if echo "$OUTPUT" | grep -q "Already up to date."; then
    echo "No updates."
    exit 0
fi

# Otherwise notify Discord
WEBHOOK_URL="$DISCORD_WEBHOOK_URL"

MESSAGE="🚀 **Update pulled on LOCAL machine!**\n\`\`\`\n$OUTPUT\n\`\`\`"

curl -H "Content-Type: application/json" \
     -d "{\"content\": \"$MESSAGE\"}" \
     $WEBHOOK_URL
