from pathlib import Path
import re

ROOT = Path("/app")

def replace_file(rel, pairs):
    p = ROOT / rel
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")

replace_file("src/lib/auth/session.ts", [
    ('"virex_panel"', '"booking_panel"'),
    ('"virex-panel-v1"', '"booking-panel-v1"'),
])
replace_file("src/lib/auth/session.test.ts", [
    ('"Virex2026"', '"Booking2026"'),
    ('"virex2026"', '"booking2026"'),
])
replace_file("src/lib/data/store/memory.ts", [("__virexDemo", "__bookingDemo")])
replace_file("src/lib/data/store/postgres.ts", [("__virexSql", "__bookingSql")])
replace_file("src/lib/data/seed.ts", [
    ("virex:", "booking:"),
    ('"Asistente Virex"', '"Booking Assistant"'),
])
replace_file("src/lib/zernio/scope.test.ts", [
    ('"wa-virex"', '"wa-booking"'),
    ('"perfil-virex"', '"profile-booking"'),
    ('"sólo deja las del profile de Virex"', '"keeps only accounts from the Booking profile"'),
])

for rel in ["scripts/console-check.mjs","scripts/verify.mjs","scripts/shot.mjs","scripts/webhook-smoke.mjs"]:
    replace_file(rel, [
        ("virex:intro", "booking:intro"),
        ("acc_virex_wa", "acc_booking_wa"),
        ("Virex", "Booking"),
        ("VIREX", "BOOKING"),
    ])

for rel in ["README.md","AGENTS.md","docs/ROADMAP.md","docs/PLAN.md"]:
    p = ROOT / rel
    if not p.exists():
        continue
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"\bVIREX\b", "BOOKING", s)
    s = re.sub(r"\bVirex\b", "Booking", s)
    s = s.replace("virex-barbershop", "booking-system")
    s = s.replace("virex_barbershop", "booking")
    s = s.replace("@virex_barbershop", "@booking")
    p.write_text(s, encoding="utf-8")

replace_file("src/app/api/mercadopago/webhook/route.ts", [
    ('service?.name ?? "turno"', 'service?.name ?? "booking"'),
])
replace_file("src/app/api/zernio/webhook/route.ts", [
    ('"[agente] did not respond"', '"[ai-agent] did not respond"'),
])
replace_file("src/lib/data/settings-actions.ts", [
    (" tiene ", " has "),
    (" turno", " booking"),
])
replace_file("src/lib/mercadopago/config.ts", [
    ("Falta MERCADOPAGO_WEBHOOK_SECRET (se copia al dar de alta la notificación webhook en Mercado Pago).",
     "MERCADOPAGO_WEBHOOK_SECRET is missing (copy it when creating the Mercado Pago webhook notification)."),
])

# Safely replace the mixed-language deposit note without embedding a template literal in this script.
p = ROOT / "src/lib/data/actions.ts"
if p.exists():
    s = p.read_text(encoding="utf-8")
    s = s.replace("(seña " + "$" + "{formatARS(depositPaid)} already paid)",
                  "(deposit " + "$" + "{formatARS(depositPaid)} already paid)")
    p.write_text(s, encoding="utf-8")

print("SOURCE_FINALIZE_APPLIED")
