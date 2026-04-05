# Gmail Empty Trash

A modern Python script to permanently empty your Gmail trash using the Gmail API.

Since Gmail's automatic trash deletion only happens every 30 days and isn't configurable, this script allows you to empty your trash on a custom schedule (e.g., using `launchd` on macOS or `cron` on Linux).

## Features

- **Efficient**: Uses `batchDelete` to remove messages in large chunks.
- **Modern**: Built with `google-auth` and current Google API client libraries.
- **Scalable**: Handles pagination for large trash folders.
- **Safe**: Includes a `--dry-run` flag to preview deletions.

## Setup

### 1. Enable the Gmail API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Search for "Gmail API" and enable it.
4. Go to **APIs & Services > Credentials**.
5. Click **Create Credentials > OAuth client ID**.
6. Select **Desktop app** as the application type.
7. Download the JSON file and rename it to `client_secret.json`. Place it in the same directory as the script.

### 2. Install Dependencies

It is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

pip install -r requirements.txt
```

## Usage

Run the script manually to authenticate:

```bash
python empty-trash.py
```

On the first run, it will open a browser for you to authorize the application. A `token.json` file will be created to store your credentials securely.

### Dry Run

To see how many messages are in the trash without deleting them:

```bash
python empty-trash.py --dry-run
```

## Automation

### macOS (launchd)

Create a plist file in `~/Library/LaunchAgents/com.user.gmail-empty-trash.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.gmail-empty-trash</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/your/empty-trash.py</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer> <!-- Every hour -->
    <key>WorkingDirectory</key>
    <string>/path/to/your/project</string>
</dict>
</plist>
```

Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.user.gmail-empty-trash.plist
```

### Linux (cron)

Add a crontab entry to run every hour:

```bash
0 * * * * cd /path/to/project && /path/to/venv/bin/python empty-trash.py
```
