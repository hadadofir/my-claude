# Mail Maint - Gmail Maintenance Tool

A Python background service that automatically maintains your Gmail inbox by cleaning old emails, organizing with labels, finding unsubscribe opportunities, and backing up to SQLite.

## Features

- **Backup**: Incrementally backup emails to SQLite database with full-text search
- **Cleanup**: Delete old emails, empty spam/trash, remove emails from blacklisted senders
- **Organize**: Apply labels based on configurable rules (sender patterns, subject keywords)
- **Unsubscribe**: Find and track unsubscribe opportunities from newsletters

## Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as application type
   - Download the credentials as `credentials.json`

### 2. Install Dependencies

```bash
cd mail_maint
pip install -r requirements.txt
```

### 3. Configure

Edit `config.yaml` to customize:
- Cleanup rules (how old before deletion, blacklisted senders)
- Organization rules (label emails by sender/subject patterns)
- Schedule (when each task runs)

### 4. Authenticate

```bash
python -m src.main --setup
```

This opens a browser for Gmail OAuth authorization. Grant access and the token will be saved.

## Usage

### Run Individual Tasks

```bash
# Preview what would be deleted (dry run)
python -m src.main --task cleanup --dry-run

# Actually run cleanup
python -m src.main --task cleanup

# Backup emails to database
python -m src.main --task backup

# Apply organization rules
python -m src.main --task organize

# Scan for unsubscribe opportunities
python -m src.main --task unsubscribe
```

### Check Status

```bash
python -m src.main --status
```

### Generate Unsubscribe Report

```bash
python -m src.main --unsubscribe-report
```

### Run Scheduler (Background Service)

```bash
python -m src.main
```

This runs tasks according to the schedule in `config.yaml`.

## Configuration

### Organization Rules

```yaml
organize:
  rules:
    - match:
        from: "*@github.com"
      label: "Dev/GitHub"
    - match:
        subject: "invoice"
      label: "Finance/Invoices"
```

Supports:
- Wildcard patterns: `*@example.com`
- Regex: `regex:pattern`
- Substring matching (default)

### Cleanup Settings

```yaml
cleanup:
  delete_older_than_days: 90
  empty_spam: true
  empty_trash: true
  sender_blacklist:
    - "noreply@spam.com"
```

### Schedule

```yaml
schedule:
  cleanup: "daily at 02:00"
  organize: "every 6 hours"
  backup: "daily at 03:00"
  unsubscribe_scan: "weekly on monday"
```

## Project Structure

```
mail_maint/
├── config.yaml              # Configuration
├── credentials.json         # Gmail OAuth credentials (you provide)
├── token.json              # OAuth token (auto-generated)
├── src/
│   ├── main.py             # Entry point, scheduler, CLI
│   ├── gmail_client.py     # Gmail API wrapper
│   ├── database.py         # SQLite operations
│   └── tasks/
│       ├── backup.py       # Email backup task
│       ├── cleanup.py      # Cleanup task
│       ├── organize.py     # Labeling task
│       └── unsubscribe.py  # Unsubscribe finder
├── data/
│   └── mail_backup.db      # SQLite database
└── logs/
    └── mail_maint.log      # Log files
```

## Security Notes

- `credentials.json` and `token.json` contain sensitive OAuth data - keep them private
- The SQLite database contains email content - handle appropriately
- Use `--dry-run` to preview destructive operations before running them

## License

MIT
