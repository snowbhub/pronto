from pathlib import Path
import re

ROOT = Path("/app")
BT = chr(96)

def patch(rel, pairs):
    p = ROOT / rel
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    before = s
    for old, new in pairs:
        s = s.replace(old, new)
    if s != before:
        p.write_text(s, encoding="utf-8")
        print("UI_FINAL_PATCH", rel)

patch("src/app/(panel)/page.tsx", [
    (BT + 'Quedan ${left} turnos to serve. The AI Agent created ${d.agent.booked} ${d.agent.booked === 1 ? "turno" : "turnos"} automatically today.' + BT,
     BT + 'There are ${left} ${left === 1 ? "booking" : "bookings"} to serve. The AI Agent created ${d.agent.booked} ${d.agent.booked === 1 ? "booking" : "bookings"} automatically today.' + BT),
])
patch("src/app/(panel)/agenda/page.tsx", [
    ('>{w.count} turnos</span>', '>{w.count} {w.count === 1 ? "booking" : "bookings"}</span>'),
])
patch("src/app/(panel)/finanzas/page.tsx", [
    ('detail: ' + BT + '${v.count} turnos' + BT,
     'detail: ' + BT + '${v.count} ${v.count === 1 ? "booking" : "bookings"}' + BT),
    ('detail: ' + BT + '${l.services} servicios${l.staff.commissionPct ? ' + BT + ' · payout ${formatARS(l.payout)}' + BT + ' : " · dueño"}' + BT,
     'detail: ' + BT + '${l.services} ${l.services === 1 ? "service" : "services"}${l.staff.commissionPct ? ' + BT + ' · payout ${formatARS(l.payout)}' + BT + ' : " · owner"}' + BT),
])
patch("src/components/caja/caja-view.tsx", [
    ('<p className="eyebrow">Entró {isToday ? "hoy" : "that day"}</p>',
     '<p className="eyebrow">Received {isToday ? "today" : "that day"}</p>'),
    ('+{formatARS(p.tip)} propina</span>', '+{formatARS(p.tip)} tip</span>'),
    (BT + 'payout (${l.staff.commissionPct}% + propinas)' + BT + ' : "dueño"',
     BT + 'payout (${l.staff.commissionPct}% + tips)' + BT + ' : "owner"'),
])
patch("src/components/settings/fixed-slots-editor.tsx", [
    (BT + 'Saved. Note: there are already ${res.overlapping} turno${res.overlapping === 1 ? "" : "s"} cargado${res.overlapping === 1 ? "" : "s"} in that time range. Move them from the schedule.' + BT,
     BT + 'Saved. Note: there ${res.overlapping === 1 ? "is" : "are"} already ${res.overlapping} ${res.overlapping === 1 ? "booking" : "bookings"} in that time range. Move ${res.overlapping === 1 ? "it" : "them"} from the schedule.' + BT),
])
patch("src/components/settings/team-editor.tsx", [
    (BT + 'Saved. Note: ${member.name} already has ${res.overlapping} turno${res.overlapping === 1 ? "" : "s"} in that period. Move them from the schedule.' + BT,
     BT + 'Saved. Note: ${member.name} already has ${res.overlapping} ${res.overlapping === 1 ? "booking" : "bookings"} in that period. Move ${res.overlapping === 1 ? "it" : "them"} from the schedule.' + BT),
])
patch("src/components/agenda/day-grid.tsx", [
    ('>{mine.length} turnos · {formatARS(mine.reduce((sum, a) => sum + a.price, 0))}</',
     '>{mine.length} {mine.length === 1 ? "booking" : "bookings"} · {formatARS(mine.reduce((sum, a) => sum + a.price, 0))}</'),
])
patch("src/components/finance/charts.tsx", [
    (BT + 'Día ${p?.[0]?.payload?.day}' + BT, BT + 'Day ${p?.[0]?.payload?.day}' + BT),
])
patch("src/components/finance/week-view.tsx", [
    ('−{formatARS(x.expenses)} gastos</span>', '−{formatARS(x.expenses)} expenses</span>'),
])
patch("src/components/booking/booking-flow.tsx", [
    ('</span>. Tenés{" "}', '</span>. You have{" "}'),
])
patch("src/app/api/mercadopago/webhook/route.ts", [
    (BT + 'Deposit · ${service?.name ?? "turno"}' + BT, BT + 'Deposit · ${service?.name ?? "booking"}' + BT),
])
patch("src/lib/mercadopago/client.ts", [
    ('"Mercado Pago no está configurado."', '"Mercado Pago is not configured."'),
    ('"Mercado Pago tardó demasiado en responder."', '"Mercado Pago took too long to respond."'),
    ('"No se pudo conectar con Mercado Pago."', '"Could not connect to Mercado Pago."'),
])
patch("src/lib/mercadopago/config.ts", [
    ('"Falta MERCADOPAGO_WEBHOOK_SECRET (se copia al dar de alta la notificación webhook en Mercado Pago)."',
     '"MERCADOPAGO_WEBHOOK_SECRET is missing (copy it when creating the Mercado Pago webhook notification)."'),
])
patch("src/lib/zernio/events.ts", [
    ('"Tipo de evento no reflejado en la Bandeja."', '"Event type is not represented in Inbox."'),
    ('"El evento no identifica la conversación."', '"The event does not identify the conversation."'),
])

spanish = re.compile(
    r"[¿¡áéíóúñü]|\b(?:Quedan|turnos?|barberos?|clientes?|servicios?|propinas?|"
    r"dueño|gastos?|Día|Hoy|Mañana|Tenés|Entró|cargados?|Guardar|Elegí|Revisá|"
    r"Cobrar|Cerrar|Ingresos|Fidelidad|Ajustes|Bandeja|Agente|Caja|Finanzas)\b",
    re.I,
)

candidates = []
runtime_files = (
    list((ROOT / "src/app").rglob("*.tsx"))
    + list((ROOT / "src/components").rglob("*.tsx"))
    + list((ROOT / "src/lib").rglob("*.ts"))
)
for p in runtime_files:
    if ".test." in p.name:
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    text = re.sub(r"^\s*//[^\n]*", "", text, flags=re.M)
    for i, line in enumerate(text.splitlines(), 1):
        if not spanish.search(line):
            continue
        stripped = line.strip()
        technical = (
            stripped.startswith("import ")
            or stripped.startswith("export ")
            or stripped.startswith("type ")
            or stripped.startswith("interface ")
            or "href=" in stripped
            or "router." in stripped
            or "PageProps<" in stripped
            or "params." in stripped
            or "searchParams" in stripped
            or "setStep(" in stripped
            or "useState<" in stripped
            or ".source ===" in stripped
            or ".author !==" in stripped
            or "discountReason ===" in stripped
            or "kind ===" in stripped
            or "method ===" in stripped
            or re.search(r'\b(?:role|category|id):\s*["\']', stripped)
        )
        if technical:
            continue
        visible = (
            "<" in stripped
            or "toast." in stripped
            or "label:" in stripped
            or "title=" in stripped
            or "placeholder=" in stripped
            or "aria-label=" in stripped
            or "message:" in stripped
            or "error:" in stripped
            or "description:" in stripped
            or "concept:" in stripped
            or BT in stripped
        )
        if visible:
            candidates.append(f"{p.relative_to(ROOT)}:{i}: {stripped[:240]}")

print("FINAL_RUNTIME_UI_SPANISH_CANDIDATES", len(candidates))
for item in candidates[:200]:
    print("FINAL_RUNTIME_UI_SPANISH", item)
if candidates:
    raise RuntimeError("Visible Spanish candidates remain in runtime UI: " + str(len(candidates)))
