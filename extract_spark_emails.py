#!/usr/bin/env python3
"""
extract_spark_emails.py
Extrae contactos (nombre, email, empresa) desde la base de datos local de Spark Mail (Mac).
Filtra spam, emails genéricos y dominios de sistema.

Uso:
  python3 extract_spark_emails.py
  python3 extract_spark_emails.py --output ~/Desktop/contactos.csv
  python3 extract_spark_emails.py --format json
  python3 extract_spark_emails.py --include-generic
"""

import sqlite3, re, csv, os, json, argparse
from pathlib import Path
from collections import defaultdict

# ── Regex ──────────────────────────────────────────────────────────────────────
EMAIL_REGEX      = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
NAME_EMAIL_REGEX = re.compile(r'"?([^"<@\n]{2,60}?)"?\s*<([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})>')

SPAM_PATTERNS = re.compile(
    r'(noreply|no-reply|donotreply|do-not-reply|mailer|newsletter|notifications?|'
    r'bounce|unsubscribe|autorespond|postmaster|daemon|sendgrid|klaviyo|mailgun|'
    r'amazonses|akamaitech|spamhaus|exacttarget|salesforce|hubspot|marketo|'
    r'constantcontact|listserv|bulk|campaign|digest|alert@|notify@|update@|news@)',
    re.IGNORECASE
)

GENERIC_LOCALS = re.compile(
    r'^(info|hello|hola|contact|contacto|ventas|sales|soporte|support|admin|'
    r'billing|accounts?|invoice|factura|team|equipo|office|no[-_]?reply)$',
    re.IGNORECASE
)

SKIP_DOMAINS = {
    "apple.com", "icloud.com", "sentry.io", "crashlytics.com", "readdle.com",
    "amazonaws.com", "googleusercontent.com", "akamaitech.net", "sendgrid.net",
    "mailgun.org", "mailchimp.com", "sparkpostmail.com", "bounces.google.com"
}

# ── Paths por cliente ──────────────────────────────────────────────────────────
CLIENT_PATHS = {
    "Spark": "~/Library/Group Containers/3L68KQB4HG.group.com.readdle.smartemail/databases/",
    "Apple Mail": "~/Library/Mail/",
    "Airmail": "~/Library/Group Containers/it.bloop.airmail2/",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def domain_from_email(email):
    parts = email.split("@")
    return parts[1] if len(parts) == 2 else ""

def company_from_domain(domain):
    parts = domain.split(".")
    return parts[-2].capitalize() if len(parts) >= 2 else domain

def is_spam(email, include_generic=False):
    if SPAM_PATTERNS.search(email):
        return True
    dom = domain_from_email(email)
    if any(dom == d or dom.endswith("." + d) for d in SKIP_DOMAINS):
        return True
    if not include_generic:
        local = email.split("@")[0]
        if GENERIC_LOCALS.match(local):
            return True
    return False

# ── Extracción ─────────────────────────────────────────────────────────────────
def scan_db(db_path, contacts, include_generic=False):
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        for table in tables:
            try:
                cur.execute(f'SELECT * FROM "{table}" LIMIT 15000')
                for row in cur.fetchall():
                    row_text = " ".join(str(c) for c in row if c)
                    # Pares nombre+email
                    for m in NAME_EMAIL_REGEX.finditer(row_text):
                        name_raw, email = m.group(1).strip(), m.group(2).strip().lower()
                        if is_spam(email, include_generic):
                            continue
                        name = re.sub(r'\s+', ' ', re.sub(r'[\=\?utf\-8BQbq_]+', ' ', name_raw)).strip()
                        if len(name) < 2 or re.search(r'\d{4,}', name):
                            name = ""
                        dom  = domain_from_email(email)
                        if contacts[email]["name"] == "" and name:
                            contacts[email]["name"] = name
                        contacts[email]["email"]   = email
                        if contacts[email]["company"] == "":
                            contacts[email]["company"] = company_from_domain(dom)
                    # Emails sueltos
                    for email in EMAIL_REGEX.findall(row_text):
                        email = email.lower()
                        if is_spam(email, include_generic) or email in contacts:
                            continue
                        dom = domain_from_email(email)
                        contacts[email] = {"name": "", "email": email, "company": company_from_domain(dom)}
            except Exception:
                continue
        conn.close()
    except Exception as e:
        print(f"  [!] {os.path.basename(db_path)}: {e}")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Extrae contactos desde Spark Mail (Mac)")
    parser.add_argument("--output", default=str(Path.home() / "Downloads" / "spark_emails.csv"),
                        help="Ruta del archivo de salida (default: ~/Downloads/spark_emails.csv)")
    parser.add_argument("--format", choices=["csv", "json", "txt"], default="csv",
                        help="Formato de salida (default: csv)")
    parser.add_argument("--include-generic", action="store_true",
                        help="Incluir emails genéricos (info@, hello@, etc.)")
    args = parser.parse_args()

    contacts = defaultdict(lambda: {"name": "", "email": "", "company": ""})

    for client, base_path in CLIENT_PATHS.items():
        expanded = os.path.expanduser(base_path)
        if not os.path.exists(expanded):
            continue
        dbs = list(Path(expanded).rglob("*.sqlite"))
        if not dbs:
            continue
        print(f"\n[{client}] {len(dbs)} base(s) encontrada(s)")
        for db in dbs:
            print(f"  → {db.name}")
            scan_db(str(db), contacts, args.include_generic)

    rows = sorted([v for v in contacts.values() if v["email"]], key=lambda x: x["email"])

    if not rows:
        print("\n❌ No se encontraron contactos.")
        return

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "csv":
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "email", "company"])
            writer.writeheader()
            writer.writerows(rows)
    elif args.format == "json":
        output = output.with_suffix(".json")
        with open(output, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    elif args.format == "txt":
        output = output.with_suffix(".txt")
        with open(output, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(f"{r['email']}\n")

    print(f"\n✅ {len(rows)} contactos exportados → {output}")

if __name__ == "__main__":
    main()
