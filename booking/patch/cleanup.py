from pathlib import Path
import re

ROOT = Path("/app")

def patch(rel, pairs):
    p = ROOT / rel
    if not p.exists():
        print("CLEANUP_MISSING", rel)
        return
    s = p.read_text(encoding="utf-8")
    hits = 0
    for old, new in pairs:
        if old in s:
            s = s.replace(old, new)
            hits += 1
    p.write_text(s, encoding="utf-8")
    print("CLEANUP", rel, hits, "/", len(pairs))

# Type-safety fixes caused by earlier display-copy normalization.
patch("src/app/(panel)/finanzas/page.tsx", [
    ('  services: "Utilities & internet",', '  servicios: "Utilities & internet",'),
])

patch("src/components/clients/loyalty-card.tsx", [
    ('background="var(--surface-1)"', 'background="#050505"'),
    ('color="var(--ivory)"', 'color="#ffffff"'),
])

# Visible panel copy. Internal IDs, enum values and routes intentionally remain unchanged.
patch("src/app/(panel)/page.tsx", [
    ("Quedan ", "There are "),
    (" turnos to serve.", " bookings to serve."),
    ('? "turno" : "turnos"', '? "booking" : "bookings"'),
    (' : "cerrado"', ' : "closed"'),
])

patch("src/app/(panel)/agenda/page.tsx", [
    ("Hoy", "Today"),
    ("} turnos", "} bookings"),
])

patch("src/app/(panel)/caja/page.tsx", [
    ("Hoy", "Today"),
])

patch("src/app/(panel)/clientes/page.tsx", [
    ("} clientes ·", "} clients ·"),
])

patch("src/app/(panel)/finanzas/page.tsx", [
    ("} turnos", "} bookings"),
    ("} servicios", "} services"),
    ('" · dueño"', '" · owner"'),
])

patch("src/components/caja/caja-view.tsx", [
    ('? "hoy" : "that day"', '? "today" : "that day"'),
    ("} servicios ·", "} services ·"),
    (' : "dueño"}', ' : "owner"}'),
    (" + propinas)", " + tips)"),
    (" propina</span>", " tip</span>"),
])

patch("src/components/clients/loyalty-card.tsx", [
    ("Corte ", "Visit "),
])

patch("src/components/hoy/quick-appointment.tsx", [
    ("Anotado: ", "Booked: "),
    (" con ", " with "),
    (" a las ", " at "),
    (", cuando termine el turno que tiene", ", after the current booking ends"),
])

patch("src/components/booking/booking-flow.tsx", [
    ("No quedan horarios that day. Probá con otro día o con otro barbero.",
     "No times are available that day. Try another day or another staff member."),
    ('Tenés{" "}', 'You have{" "}'),
])

patch("src/components/shell/mobile-nav.tsx", [
    ("Más", "More"),
])

patch("src/components/finance/week-view.tsx", [
    ("A pagar = comisión + propinas − vales − pagos ya hechos. Los dueños no cobran comisión: lo que facturan queda en la casa",
     "Payout = commission + tips − advances − payments already made. Owners do not receive commission: their revenue stays with the business"),
    (" gastos", " expenses"),
])

patch("src/components/agenda/day-grid.tsx", [
    ("} turnos ·", "} bookings ·"),
    ("Turno pasado a ", "Booking moved to "),
    (". Avisale al cliente si esperaba a otro barbero.", ". Let the client know if they expected another staff member."),
    ("Cancelar turno", "Cancel booking"),
])

patch("src/components/agenda/new-appointment.tsx", [
    (" has no free slots of ", " has no free slots of "),
    ("Elegí otra hora abajo, o probá con otro barbero o día.",
     "Choose another time below, or try another staff member or day."),
])

patch("src/components/settings/fixed-slots-editor.tsx", [
    (" turno", " booking"),
    (" cargado", " already existing"),
])

patch("src/components/settings/team-editor.tsx", [
    (" turno", " booking"),
    ("Barbero · ", "Staff member · "),
    ("% de comisión + propinas", "% commission + tips"),
])

patch("src/lib/data/settings-actions.ts", [
    (" tiene ", " has "),
    (" turno", " booking"),
    (" upcoming.", " upcoming."),
])

patch("src/components/finance/charts.tsx", [
    ("Día ", "Day "),
])

# Customer/admin-visible integration messages.
patch("src/lib/mercadopago/client.ts", [
    ("Mercado Pago no está configurado.", "Mercado Pago is not configured."),
    ("Mercado Pago tardó demasiado en responder.", "Mercado Pago took too long to respond."),
    ("No se pudo conectar con Mercado Pago.", "Could not connect to Mercado Pago."),
])

patch("src/lib/zernio/client.ts", [
    ("Zernio no está configurado todavía.", "Zernio is not configured yet."),
    ("Zernio rechazó la clave.", "Zernio rejected the API key."),
    ("Tu plan de Zernio no habilita esta función.", "Your Zernio plan does not include this feature."),
    ("Zernio no encontró ese recurso.", "Zernio could not find that resource."),
    ("Zernio pidió esperar por límite de pedidos.", "Zernio asked to wait because of a rate limit."),
    ("Zernio tardó demasiado en responder.", "Zernio took too long to respond."),
    ("No se pudo llegar a Zernio.", "Could not reach Zernio."),
    ("Zernio respondió con un formato inesperado.", "Zernio returned an unexpected response format."),
    ("Zernio respondió con un error.", "Zernio returned an error."),
])

patch("src/lib/zernio/actions.ts", [
    ("Canal inválido.", "Invalid channel."),
    ("No se pudo saber la dirección del panel.", "Could not determine the panel address."),
])

patch("src/lib/zernio/events.ts", [
    ("Tipo de evento no reflejado en la Bandeja.", "Event type is not represented in Inbox."),
    ("El evento no identifica la conversación.", "The event does not identify the conversation."),
])

patch("src/lib/zernio/deliver.ts", [
    ("Pasaron más de 24 h desde el último mensaje del cliente: WhatsApp sólo deja escribirle con una plantilla aprobada. Esperá a que vuelva a escribir.",
     "More than 24 hours have passed since the client's last message: WhatsApp only allows an approved template. Wait for the client to message again."),
    ("Esta conversación es de una cuenta que no pertenece a este panel: no se envía nada.",
     "This conversation belongs to an account outside this panel, so nothing was sent."),
])

# Validate that no display-copy pass corrupted common technical identifiers.
bad_ident = re.compile(r"\b(?:staff member|booking|client|service)_[A-Za-z0-9_]+\s*:")
for p in list((ROOT / "src").rglob("*.ts")) + list((ROOT / "src").rglob("*.tsx")):
    body = p.read_text(encoding="utf-8")
    m = bad_ident.search(body)
    if m:
        raise RuntimeError("CLEANUP_CORRUPTED_IDENTIFIER " + str(p.relative_to(ROOT)) + ": " + m.group(0))

visible_files = [
    "src/app/(panel)/page.tsx",
    "src/app/(panel)/agenda/page.tsx",
    "src/app/(panel)/agente/page.tsx",
    "src/app/(panel)/ajustes/page.tsx",
    "src/app/(panel)/caja/page.tsx",
    "src/app/(panel)/clientes/page.tsx",
    "src/app/(panel)/finanzas/page.tsx",
    "src/app/conectado/page.tsx",
    "src/app/login/page.tsx",
    "src/app/login/login-form.tsx",
    "src/app/pago/page.tsx",
    "src/app/reservar/page.tsx",
    "src/components/agenda/day-grid.tsx",
    "src/components/agenda/new-appointment.tsx",
    "src/components/caja/caja-view.tsx",
    "src/components/caja/charge-dialog.tsx",
    "src/components/caja/expense-dialog.tsx",
    "src/components/caja/quick-charge-dialog.tsx",
    "src/components/clients/clients-view.tsx",
    "src/components/clients/loyalty-card.tsx",
    "src/components/settings/fixed-slots-editor.tsx",
    "src/components/settings/services-editor.tsx",
    "src/components/settings/team-editor.tsx",
    "src/components/hoy/agent-live-card.tsx",
    "src/components/hoy/day-timeline.tsx",
    "src/components/hoy/quick-appointment.tsx",
    "src/components/inbox/inbox.tsx",
    "src/components/agent/agent-settings.tsx",
    "src/components/agent/agent-toggle.tsx",
    "src/components/agent/playground.tsx",
    "src/components/booking/booking-flow.tsx",
    "src/components/shell/mobile-nav.tsx",
    "src/components/shell/sidebar.tsx",
    "src/components/shell/topbar.tsx",
    "src/components/finance/charts.tsx",
    "src/components/finance/week-view.tsx",
]

marker = re.compile(r"[¿¡áéíóúñü]|\b(?:turno|turnos|barbero|barberos|cliente|clientes|fidelidad|gasto|gastos|seña|elegí|revisá|dueño|hoy|mañana|propina|cerrado|cuánto|corte|más)\b", re.I)
res = []
for rel in visible_files:
    p = ROOT / rel
    if not p.exists():
        continue
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        st = line.strip()
        if st.startswith(("//", "*", "/*", "import ")):
            continue
        if marker.search(line):
            res.append(rel + ":" + str(i) + ": " + st[:220])
print("CLEANUP_VISIBLE_RESIDUALS", len(res))
for x in res[:180]:
    print("CLEANUP_VISIBLE", x)
