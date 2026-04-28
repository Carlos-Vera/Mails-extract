# extract_spark_emails

Reads Spark Mail's local SQLite databases directly — no API, no cloud, no sync. Extracts name, email, and company from every contact that ever landed in your inbox and exports a clean, deduplicated list.

Built by [BravesLab](https://braveslab.com).

---

## What it does

- Extracts name, email, and company from Spark's local databases
- Skips spam traps, no-reply addresses, and system accounts automatically
- Exports to CSV, JSON, or plain TXT
- Use `--include-generic` if you also want addresses like `info@` or `hello@`
- Detects Apple Mail and Airmail databases if present

---

## Requirements

- macOS
- Python 3.7+
- Spark Mail installed in its default location

No dependencies. Just run it.

---

## Usage

```bash
# Default — drops spark_emails.csv in ~/Downloads
python3 extract_spark_emails.py

# Custom output path
python3 extract_spark_emails.py --output ~/Desktop/contacts.csv

# JSON
python3 extract_spark_emails.py --format json

# Emails only, plain text
python3 extract_spark_emails.py --format txt

# Include generic addresses (info@, hello@, contact@...)
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

Spark stores email data in SQLite files at:

```
~/Library/Group Containers/3L68KQB4HG.group.com.readdle.smartemail/databases/
```

The script opens each `.sqlite` file in read-only mode, scans all tables for email patterns and `"Name" <email>` pairs, deduplicates, filters noise, and writes the export.

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

---

*Desarrollado por Carlos Vera para la comunidad y toda la gloria a nuestro señor JesusCristo.*
