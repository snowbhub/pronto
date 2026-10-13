from pathlib import Path
import re

ROOT = Path("/app")

# Package metadata.
for rel in ["package.json", "package-lock.json"]:
    p = ROOT / rel
    if p.exists():
        s = p.read_text(encoding="utf-8")
        s = s.replace('"name": "virex-barbershop"', '"name": "booking-system"')
        s = s.replace('"name":"virex-barbershop"', '"name":"booking-system"')
        p.write_text(s, encoding="utf-8")

# Active brand module.
old_mark = ROOT / "src/components/brand/virex-mark.tsx"
new_mark = ROOT / "src/components/brand/booking-mark.tsx"
if old_mark.exists():
    if new_mark.exists():
        new_mark.unlink()
    old_mark.rename(new_mark)

source_files = list((ROOT / "src").rglob("*.ts")) + list((ROOT / "src").rglob("*.tsx"))
for p in source_files:
    s = p.read_text(encoding="utf-8")
    s = s.replace("@/components/brand/virex-mark", "@/components/brand/booking-mark")
    s = s.replace("./virex-mark", "./booking-mark")
    s = s.replace("VirexMark", "BookingMark")
    p.write_text(s, encoding="utf-8")

# Remove the creator badge from every remaining screen before deleting the legacy component.
for rel in [
    "src/app/conectado/page.tsx",
    "src/app/pago/page.tsx",
    "src/components/shell/mobile-nav.tsx",
]:
    p = ROOT / rel
    if not p.exists():
        continue
    body = p.read_text(encoding="utf-8")
    body = re.sub(r'import \{ OperonBadge \} from "@/components/brand/operon-badge"\n', "", body)
    body = re.sub(r'\s*<OperonBadge(?:\s+className="[^"]*")?\s*/>', "", body)
    p.write_text(body, encoding="utf-8")

# Remove legacy brand modules only when nothing imports them.
legacy = [
    ("src/components/brand/virex-wordmark.tsx", ["virex-wordmark", "VirexWordmark"]),
    ("src/components/brand/intro.tsx", ["brand/intro", "IntroOverlay"]),
    ("src/components/brand/operon-badge.tsx", ["operon-badge", "OperonBadge"]),
]
for rel, needles in legacy:
    p = ROOT / rel
    if not p.exists():
        continue
    refs = []
    for q in source_files:
        if q == p or not q.exists():
            continue
        body = q.read_text(encoding="utf-8", errors="ignore")
        if any(n in body for n in needles):
            refs.append(str(q.relative_to(ROOT)))
    if refs:
        raise RuntimeError("LEGACY_BRAND_STILL_REFERENCED " + rel + " " + ",".join(refs))
    p.unlink()

for rel in ["public/intro-boot.js", "scripts/intro-frames.mjs"]:
    p = ROOT / rel
    if p.exists():
        p.unlink()

# Remaining visible integration/config messages.
replacements = [
    ("Falta MERCADOPAGO_WEBHOOK_SECRET (se copia al dar de alta la notificación webhook en Mercado Pago).",
     "MERCADOPAGO_WEBHOOK_SECRET is missing (copy it when creating the Mercado Pago webhook notification)."),
    ("Mercado Pago respondió", "Mercado Pago returned"),
    ("Tipo de evento no reflejado en la Bandeja.", "Event type is not represented in Inbox."),
    ("El evento no identifica la conversación.", "The event does not identify the conversation."),
]
for p in source_files:
    s = p.read_text(encoding="utf-8")
    for a, b in replacements:
        s = s.replace(a, b)
    p.write_text(s, encoding="utf-8")

# Old intro CSS namespace is inactive, but remove old product wording from source.
css = ROOT / "src/app/globals.css"
if css.exists():
    s = css.read_text(encoding="utf-8")
    s = s.replace("virex-intro", "booking-intro")
    css.write_text(s, encoding="utf-8")

# Audit old brand references.
brand_hits = []
for p in ROOT.rglob("*"):
    if not p.is_file() or "node_modules" in p.parts or ".next" in p.parts or ".git" in p.parts:
        continue
    if p.suffix not in {".ts", ".tsx", ".js", ".mjs", ".css", ".json", ".md"}:
        continue
    try:
        s = p.read_text(encoding="utf-8")
    except Exception:
        continue
    if re.search(r"\bVirex\b|VIREX|virex-mark|virex-wordmark|operon-badge", s, re.I):
        brand_hits.append(str(p.relative_to(ROOT)))

print("BRAND_SOURCE_CLEANUP residuals=", len(brand_hits))
for x in brand_hits[:100]:
    print("BRAND_SOURCE_RESIDUAL", x)
