from pathlib import Path
import json, re, sys

ROOT=Path("/app")
BUNDLE=Path("/tmp/booking-patch")
errors=[]
rows=[]

for p in sorted(BUNDLE.glob("rows*.json")):
    data=json.loads(p.read_text(encoding="utf-8"))
    for i,row in enumerate(data):
        if not isinstance(row,list) or len(row)!=4:
            errors.append(f"{p.name}[{i}] must be [source,en,de,uk]")
            continue
        if not all(isinstance(v,str) and v.strip() for v in row):
            errors.append(f"{p.name}[{i}] has an empty translation")
        rows.append(tuple(row))

if ("Booking","Booking","Termin","Запис") not in rows:
    errors.append("localized product names are missing")

messages=(ROOT/"src/i18n/messages.ts").read_text(encoding="utf-8")
controls=(ROOT/"src/i18n/controls.tsx").read_text(encoding="utf-8")
bridge=(ROOT/"src/i18n/bridge.tsx").read_text(encoding="utf-8")
css=(ROOT/"src/app/globals.css").read_text(encoding="utf-8")
layout=(ROOT/"src/app/layout.tsx").read_text(encoding="utf-8")

compact=lambda s: re.sub(r"\s+","",s)
if 'exporttypeLocale="en"|"de"|"uk"' not in compact(messages):
    errors.append("Locale union is not exactly en|de|uk")
if 'SUPPORTED_LOCALES:Locale[]=["en","de","uk"]' not in compact(messages):
    errors.append("SUPPORTED_LOCALES is not exactly en,de,uk")
if '(["en","de","uk"]asLocale[])' not in compact(controls):
    errors.append("language switcher is not exactly EN/DE/UK")
if "booking_locale" not in controls or "booking_locale" not in bridge:
    errors.append("locale persistence is missing")
if "booking_theme" not in controls or 'html[data-theme="light"]' not in css:
    errors.append("dark/light theme support is incomplete")
if "Booking · Panel" not in layout:
    errors.append("Booking metadata is missing")

# Old brand may remain only in the compatibility filename virex-mark.
for p in list((ROOT/"src/app").rglob("*.ts*"))+list((ROOT/"src/components").rglob("*.ts*")):
    s=p.read_text(encoding="utf-8",errors="ignore").replace("virex-mark","brand-mark")
    s=re.sub(r"/\*[\s\S]*?\*/","",s)
    s=re.sub(r"(?m)^\s*//[^\n]*","",s)
    if re.search(r"\bVirex\b|VIREX",s):
        errors.append(f"old visible brand remains in {p.relative_to(ROOT)}")

if errors:
    print("BOOKING_I18N_VERIFY_FAILED")
    for e in errors:
        print("VERIFY_ERROR",e)
    sys.exit(1)

print(f"BOOKING_I18N_VERIFY_OK rows={len(rows)} locales=en,de,uk names=Booking|Termin|Запис themes=dark|light")
