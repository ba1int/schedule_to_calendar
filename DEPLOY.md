# VPS Deployment Guide

This guide will help you deploy the schedule automation on your VPS to run automatically via cron.

## Prerequisites

- VPS with SSH access
- Python 3.9+ installed on VPS
- Your `credentials.json` file (from Google Cloud Console)

---

## Step 1: Initial Authentication (On Your Local Machine)

Since OAuth requires a browser, we need to authenticate locally first.

1. **Run the script locally once:**
   ```bash
   python3 main.py
   ```

2. **Complete the OAuth flow** in your browser

3. **Verify `token.json` was created** in your project folder

> **Note:** `token.json` contains your authenticated session and will work on the VPS.

---

## Step 2: Upload to VPS

1. **ZIP the project** (excluding `.git` if present):
   ```bash
   cd /Users/balint/.gemini/antigravity/scratch/schedule_automation
   tar -czf schedule_automation.tar.gz --exclude='.git' .
   ```

2. **Upload to VPS:**
   ```bash
   scp schedule_automation.tar.gz user@your-vps-ip:~/
   ```

3. **SSH into VPS:**
   ```bash
   ssh user@your-vps-ip
   ```

4. **Extract:**
   ```bash
   mkdir -p ~/schedule_automation
   cd ~/schedule_automation
   tar -xzf ../schedule_automation.tar.gz
   ```

---

## Step 3: Install Dependencies on VPS

```bash
cd ~/schedule_automation
python3 -m pip install --user -r requirements.txt
```

---

## Step 4: Test the Script

Run it once manually to verify everything works:

```bash
cd ~/schedule_automation
python3 main.py
```

You should see:
```
Authenticating with Google Services...
Using calendar: Work Schedule (ID: ...)
Searching for recent schedule emails...
...
Done! Added: X, Updated: Y
```

---

## Step 5: Set Up Cron Job

1. **Open crontab editor:**
   ```bash
   crontab -e
   ```

2. **Add this line** (runs 3 times daily: 8 AM, 2 PM, 8 PM):
   ```cron
   0 8,14,20 * * * cd /home/YOUR_USERNAME/schedule_automation && /usr/bin/python3 main.py >> /home/YOUR_USERNAME/schedule_automation/cron.log 2>&1
   ```

   **Replace `YOUR_USERNAME`** with your actual username.

3. **Save and exit** (`:wq` in vim, or `Ctrl+X` then `Y` in nano)

4. **Verify cron job is set:**
   ```bash
   crontab -l
   ```

---

## Step 6: Monitor Logs

Check the log file to see if it's working:

```bash
tail -f ~/schedule_automation/cron.log
```

---

## Cron Schedule Options

If you want different timing, modify the cron expression:

- **Every 6 hours:** `0 */6 * * *`
- **Twice daily (9 AM, 9 PM):** `0 9,21 * * *`
- **Every day at noon:** `0 12 * * *`
- **Every 2 hours:** `0 */2 * * *`

---

## Troubleshooting

### "Authentication failed"
- Make sure `credentials.json` and `token.json` are in the project folder
- Re-run `python3 main.py` locally to refresh `token.json`, then re-upload

### "No module named 'google'"
- Install dependencies: `python3 -m pip install --user -r requirements.txt`

### Cron job not running
- Check logs: `tail -f ~/schedule_automation/cron.log`
- Verify cron service is running: `sudo systemctl status cron`
- Test the command manually first

### Token expires
Google tokens should auto-refresh, but if you see auth errors:
1. Delete `token.json` on your VPS
2. Re-authenticate locally
3. Re-upload `token.json` to VPS

---

## Updating the Script

When you make changes locally:

1. **Re-package:**
   ```bash
   cd /Users/balint/.gemini/antigravity/scratch/schedule_automation
   tar -czf schedule_automation.tar.gz --exclude='.git' .
   ```

2. **Upload and extract:**
   ```bash
   scp schedule_automation.tar.gz user@your-vps-ip:~/
   ssh user@your-vps-ip
   cd ~/schedule_automation
   tar -xzf ../schedule_automation.tar.gz
   ```

The cron job will automatically use the updated code.
