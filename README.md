# Schedule Automation

This tool automates adding your work schedule from Gmail to Google Calendar.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Get Google Credentials**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Enable **Gmail API** and **Google Calendar API**.
    - Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
    - Choose **Desktop app**.
    - Download the JSON file and save it as `credentials.json` in this folder.
    - **Important**: Add your email as a "Test User" in the OAuth consent screen configuration if the app is not published.

3.  **Run the Script**:
    ```bash
    python3 main.py
    ```
    - On the first run, a browser window will open asking you to log in to your Google account.
    - Grant the requested permissions.
    - A `token.json` file will be created to store your login session.

## How it Works

- **Gmail**: Searches for emails from `mymenu-support@ext.mcdonalds.com` with subjects "Beosztásod megváltozott" or "Új beosztásod".
- **Parser**: Extracts dates and times from the Hungarian email body.
- **Calendar**:
    - Automatically creates a secondary calendar named **"Work Schedule"** (so it doesn't clutter your main calendar).
    - Checks if an event exists on that day with the summary "Work at McDonald's".
    - If it exists, it **updates** the event with the new time (handling schedule changes).
    - If it doesn't exist, it **creates** a new event.

## Features

- **Smart Sync**: Updates existing events if schedule changes.
- **Dedicated Calendar**: Uses "Work Schedule" calendar.
- **Shift Adjustment**: Automatically subtracts **20 minutes** from the start time (e.g., 12:00 -> 11:40) so you arrive early.

## Deployment

See [DEPLOY.md](DEPLOY.md) for instructions on deploying to a VPS with automated cron scheduling.

## Backfilling Past Schedules
