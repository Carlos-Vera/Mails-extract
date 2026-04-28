# extract_spark_emails

Ever wanted to pull your actual contacts out of Spark Mail without touching any API or syncing to the cloud? This does exactly that — reads Spark's local SQLite databases directly on your Mac and exports clean, deduplicated contacts in whatever format you need.

Built by [BravesLab](https://braveslab.com).

---

## What it does

- Pulls name, email, and company from Spark's local databases
- Automatically skips spam traps, no-reply addresses, and system accounts
- Exports to CSV, JSON, or plain TXT
- Optionally grabs generic addresses like `info@` or `hello@` if you want those too
- Also picks up Apple Mail and Airmail databases if they're around

---

## Requirements

- macOS
- Python 3.7+
- Spark Mail installed in its default location

No dependencies to install — just run it.

---

## Usage

```bash
# Quickest way — drops a CSV in ~/Downloads
python3 extract_spark_emails.py

# Pick your own output path
python3 extract_spark_emails.py --output ~/Desktop/contacts.csv

# JSON instead of CSV
python3 extract_spark_emails.py --format json

# Just a list of emails, nothing else
python3 extract_spark_emails.py --format txt

# Include generic addresses (info@, hello@, contact@, etc.)
python3 extract_spark_emails.py --include-generic
```

---

## Output

| name | email | company |
|------|-------|---------|
| Carlos Vera | carlos@braveslab.com | Braveslab |
| Jane Doe | jane@acme.com | Acme |

---

## How it works

Spark keeps all your email data locally in SQLite files under:

```
~/Library/Group Containers/3L68KQB4HG.group.com.readdle.smartemail/databases/
```

The script opens each `.sqlite` file in read-only mode, scans every table for email patterns and `"Name" <email>` pairs, deduplicates everything, filters out the noise, and writes your export.

---

## Supported clients

| Client | Status |
|--------|--------|
| Spark Mail | Full support |
| Apple Mail | Detected (partial) |
| Airmail | Detected (partial) |

---

## License

MIT
