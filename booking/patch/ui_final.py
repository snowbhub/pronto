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


# Exhaustive runtime prose cleanup found by the strict audit.
patch("src/components/caja/caja-view.tsx", [
    (">Cobrar →</span>", ">Charge →</span>"),
    ("<dt>Esperado al cerrar</dt>", "<dt>Expected at close</dt>"),
])
patch("src/components/caja/charge-dialog.tsx", [
    (">Cobrar</DialogTitle>", ">Charge</DialogTitle>"),
])
patch("src/components/caja/expense-dialog.tsx", [
    ('category === "vale" ? "Vale cargado" : "Expense added"', 'category === "vale" ? "Advance added" : "Expense added"'),
])
patch("src/components/settings/team-editor.tsx", [
    (">Ninguno cargado.</p>", ">None added.</p>"),
])
patch("src/components/finance/week-view.tsx", [
    (">Cortes, productos, bebidas y propinas.</p>", ">Services, products, drinks and tips.</p>"),
])
patch("src/components/inbox/inbox.tsx", [
    (BT + 'Ventana de WhatsApp abierta: quedan ${Math.floor(window24)} h para responder libremente.' + BT,
     BT + 'WhatsApp window open: ${Math.floor(window24)} h left to reply freely.' + BT),
])

patch("src/lib/data/actions.ts", [
    (BT + '${staff.name} no tiene libre ese horario. Elegí otro.' + BT,
     BT + '${staff.name} is not available at that time. Choose another.' + BT),
    (BT + 'Alguien acaba de tomar ese horario con ${staff.name}. Elegí otro.' + BT,
     BT + 'Someone just took that time with ${staff.name}. Choose another.' + BT),
    (BT + '${member.name} acaba de ocupar ese horario. Elegí otro barbero.' + BT,
     BT + '${member.name} just took that time. Choose another staff member.' + BT),
    (BT + '${service.name} (seña ${formatARS(depositPaid)} already paid)' + BT,
     BT + '${service.name} (deposit ${formatARS(depositPaid)} already paid)' + BT),
    (BT + '${staff.name} está ocupado por un buen rato. Probá con otro barbero o agendalo a una hora.' + BT,
     BT + '${staff.name} is busy for a while. Try another staff member or book a specific time.' + BT),
    (BT + '${staff.name} justo tiene un turno en ese momento. Probá con otro barbero.' + BT,
     BT + '${staff.name} already has a booking at that time. Try another staff member.' + BT),
])
patch("src/lib/data/seed.ts", [
    (BT + 'Tenés ${gStatus.stamps} de ${gStatus.required} stamps. You need ${gStatus.required - gStatus.stamps} and your next service is 50% off ✨' + BT,
     BT + 'You have ${gStatus.stamps} of ${gStatus.required} stamps. You need ${gStatus.required - gStatus.stamps} more and your next service is 50% off ✨' + BT),
    (BT + 'Agendó ${svc(a.serviceId).name} a ${c.name.split(" ")[0]} · ${relDay(dayKey(a.startsAt))} ${hm(a.startsAt)}' + BT,
     BT + 'Created ${svc(a.serviceId).name} for ${c.name.split(" ")[0]} · ${relDay(dayKey(a.startsAt))} ${hm(a.startsAt)}' + BT),
])
patch("src/lib/mercadopago/config.ts", [
    (BT + 'MERCADOPAGO_WEBHOOK_SECRET parece incompleto (mínimo ${MIN_WEBHOOK_SECRET_LENGTH} caracteres).' + BT,
     BT + 'MERCADOPAGO_WEBHOOK_SECRET looks incomplete (minimum ${MIN_WEBHOOK_SECRET_LENGTH} characters).' + BT),
])
patch("src/lib/zernio/client.ts", [
    ('"Could not reach Zernio. Revisá la conexión del servidor."', '"Could not reach Zernio. Check the server connection."'),
    ('"Zernio returned an error. Volvé a intentar en unos minutos."', '"Zernio returned an error. Try again in a few minutes."'),
])
patch("src/lib/zernio/actions.ts", [
    ('"Falta ZERNIO_PROFILE_ID: creá en Zernio un profile para Booking (cada profile admite un solo WhatsApp)."',
     '"ZERNIO_PROFILE_ID is missing: create a Zernio profile for Booking (each profile supports one WhatsApp account)."'),
])
patch("src/lib/zernio/config.ts", [
    (BT + 'ZERNIO_API_KEY es demasiado corta (mínimo ${MIN_API_KEY_LENGTH} caracteres).' + BT,
     BT + 'ZERNIO_API_KEY is too short (minimum ${MIN_API_KEY_LENGTH} characters).' + BT),
    (BT + 'ZERNIO_WEBHOOK_SECRET es demasiado corto (mínimo ${MIN_WEBHOOK_SECRET_LENGTH} caracteres).' + BT,
     BT + 'ZERNIO_WEBHOOK_SECRET is too short (minimum ${MIN_WEBHOOK_SECRET_LENGTH} characters).' + BT),
])
patch("src/lib/agent/config.ts", [
    (BT + 'AGENT_PROVIDER="${raw}" no existe: usá "gemini" o "anthropic".' + BT,
     BT + 'AGENT_PROVIDER="${raw}" is not supported: use "gemini" or "anthropic".' + BT),
    (BT + 'Falta ${keyVar} en el entorno del servidor. Sin ella el agente no puede responder.' + BT,
     BT + '${keyVar} is missing from the server environment. The AI Agent cannot reply without it.' + BT),
])
patch("src/lib/agent/respond.ts", [
    (BT + '[Respondió una persona del equipo] ${m.body}' + BT,
     BT + '[A team member replied] ${m.body}' + BT),
    ('"tarjeta completa, el próximo corte va al 50%"', '"loyalty card complete, the next service is 50% off"'),
    (BT + '${loyalty!.stamps} de ${loyalty!.required} sellos' + BT,
     BT + '${loyalty!.stamps} of ${loyalty!.required} stamps' + BT),
])
patch("src/lib/agent/tools.ts", [
    ('Hora mínima HH:MM si el cliente pide una franja ("a la tarde" = 14:00, "después de las 6" = 18:00, "tipo 17" = 17:00). Cadena vacía si no importa.',
     'Minimum HH:MM time when the client requests a time range ("afternoon" = 14:00, "after 6" = 18:00, "around 17" = 17:00). Empty string if irrelevant.'),
    ('Teléfono del cliente, o cadena vacía si no se sabe.', 'Client phone number, or an empty string if unknown.'),
    ('Lista los próximos turnos del cliente de esta conversación, con su id.', 'Lists upcoming bookings for the client in this conversation, including their IDs.'),
    ('Mueve un turno del cliente a otra fecha y hora (mismo servicio y barbero).', 'Moves a client booking to another date and time (same service and staff member).'),
    ('Cancela un turno del cliente.', 'Cancels a client booking.'),
    ('Devuelve cuántos sellos tiene el cliente en la tarjeta de fidelidad y si payout el descuento.', 'Returns the client loyalty stamp count and whether the reward discount is ready.'),
    (BT + '${m.name} ya no tiene libre ${input.hora} el ${formatDayLong(input.fecha)}. Volvé a consultar disponibilidad.' + BT,
     BT + '${m.name} is no longer available at ${input.hora} on ${formatDayLong(input.fecha)}. Check availability again.' + BT),
    (BT + 'Ese horario se acaba de ocupar. Volvé a consultar disponibilidad.' + BT,
     BT + 'That time was just taken. Check availability again.' + BT),
    (BT + '${m.name} no tiene libre ese horario. Consultá disponibilidad.' + BT,
     BT + '${m.name} is not available at that time. Check availability.' + BT),
    (BT + '${m.name} ya no tiene libre ese horario. Consultá disponibilidad.' + BT,
     BT + '${m.name} is no longer available at that time. Check availability.' + BT),
    (BT + 'Cancelado por el agente: ${String(input.motivo).slice(0, 200)}' + BT,
     BT + 'Cancelled by AI Agent: ${String(input.motivo).slice(0, 200)}' + BT),
])
patch("src/lib/agent/providers/types.ts", [
    ('[Contexto del sistema — no es parte del mensaje del cliente]', '[System context — not part of the client message]'),
])
patch("src/lib/agent/providers/anthropic.ts", [
    (BT + 'La IA respondió con un error (${error.status}).' + BT, BT + 'The AI provider returned an error (${error.status}).' + BT),
])
patch("src/lib/agent/providers/gemini.ts", [
    (BT + 'La IA respondió con un error (${error.status}).' + BT, BT + 'The AI provider returned an error (${error.status}).' + BT),
])
patch("src/lib/domain/slots.ts", [
    ('"Business está cerrado that day."', '"The business is closed that day."'),
    ('"La duración tiene que ser mayor a cero."', '"Duration must be greater than zero."'),
    (BT + 'Ese turno queda fuera del horario del local (${BRAND.openingHours.open} a ${BRAND.openingHours.close}).' + BT,
     BT + 'That booking falls outside business hours (${BRAND.openingHours.open} to ${BRAND.openingHours.close}).' + BT),
    ('"Ese horario ya pasó."', '"That time has already passed."'),
    ('" Si ya terminó, cobralo o marcalo como terminado para liberar el horario."', '" If it has already ended, charge it or mark it completed to free the time slot."'),
    (BT + '${staff.name} already has un turno de ${fmtRange([minutesOfDay(clash.startsAt), minutesOfDay(clash.endsAt)])}.${hint}' + BT,
     BT + '${staff.name} already has a booking from ${fmtRange([minutesOfDay(clash.startsAt), minutesOfDay(clash.endsAt)])}.${hint}' + BT),
    (BT + 'Coincide con un franco o un turno fijo de ${staff.name}.' + BT,
     BT + 'It overlaps with time off or a fixed booking for ${staff.name}.' + BT),
    ('"El turno ya está con ese barbero."', '"The booking is already assigned to that staff member."'),
    ('"Sólo se puede pasar un turno que todavía no empezó."', '"Only a booking that has not started can be moved."'),
    (BT + '${staff.name} no está activo.' + BT, BT + '${staff.name} is not active.' + BT),
])
patch("src/lib/domain/schedule.ts", [
    ('"La hora de salida tiene que ser después de la de entrada."', '"End time must be after start time."'),
    (BT + 'Dos franjas del mismo día se pisan (${prev.start} a ${prev.end} y ${cur.start} a ${cur.end}).' + BT,
     BT + 'Two time ranges on the same day overlap (${prev.start} to ${prev.end} and ${cur.start} to ${cur.end}).' + BT),
])
patch("src/lib/import/historial.ts", [
    (BT + 'Historial · ${l.label.toLowerCase()}' + BT, BT + 'History · ${l.label.toLowerCase()}' + BT),
    (BT + '${day}: el encabezado decía "${b.headerName.toLowerCase()} ${b.headerDay}/${b.headerMonth}" pero that day es ${real.toLowerCase()} ${dia}/${mes} (usé la fecha por orden).' + BT,
     BT + '${day}: the header said "${b.headerName.toLowerCase()} ${b.headerDay}/${b.headerMonth}" but that date is ${real.toLowerCase()} ${dia}/${mes} (date order was used).' + BT),
    (BT + '${day}: ${barbero ? barbero.toLowerCase() : concept} tiene ${n} en cantidad pero ninguna plata anotada (esos cortes no se importaron).' + BT,
     BT + '${day}: ${barbero ? barbero.toLowerCase() : concept} has quantity ${n} but no amount recorded (those services were not imported).' + BT),
    (BT + '${day}: fila "${l.label.toLowerCase()}" que no es un barbero conocido: se cargó ${l.cash + l.tr} sin barbero asignado.' + BT,
     BT + '${day}: row "${l.label.toLowerCase()}" is not a known staff member: ${l.cash + l.tr} was loaded without an assigned staff member.' + BT),
    (BT + '${titleCase(a)}: sin cantidad de cortes, no se cargó.' + BT,
     BT + '${titleCase(a)}: no service quantity; not loaded.' + BT),
    (BT + '${titleCase(a)}: sin fecha de sus cortes, no se cargó.' + BT,
     BT + '${titleCase(a)}: no service date; not loaded.' + BT),
    (BT + '${tarjetas[tarjetas.length - 1].name}: el teléfono "${String(a)}" no tiene 10 dígitos (no se cargó).' + BT,
     BT + '${tarjetas[tarjetas.length - 1].name}: phone "${String(a)}" does not have 10 digits (not loaded).' + BT),
])


# Resolve mixed-language strings created when earlier dictionary passes translate only a prefix.
patch("src/components/inbox/inbox.tsx", [
    (BT + 'WhatsApp window open: quedan ${Math.floor(window24)} h left to reply freely.' + BT,
     BT + 'WhatsApp window open: ${Math.floor(window24)} h left to reply freely.' + BT),
])
patch("src/lib/mercadopago/config.ts", [
    (BT + 'MERCADOPAGO_WEBHOOK_SECRET looks incomplete (mínimo ${MIN_WEBHOOK_SECRET_LENGTH} caracteres).' + BT,
     BT + 'MERCADOPAGO_WEBHOOK_SECRET looks incomplete (minimum ${MIN_WEBHOOK_SECRET_LENGTH} characters).' + BT),
])
patch("src/lib/zernio/actions.ts", [
    ('"ZERNIO_PROFILE_ID is missing: creá en Zernio un profile para Booking (cada profile admite un solo WhatsApp)."',
     '"ZERNIO_PROFILE_ID is missing: create a Zernio profile for Booking (each profile supports one WhatsApp account)."'),
])
patch("src/lib/zernio/config.ts", [
    (BT + 'ZERNIO_API_KEY is too short (mínimo ${MIN_API_KEY_LENGTH} caracteres).' + BT,
     BT + 'ZERNIO_API_KEY is too short (minimum ${MIN_API_KEY_LENGTH} characters).' + BT),
    (BT + 'ZERNIO_WEBHOOK_SECRET is too short (mínimo ${MIN_WEBHOOK_SECRET_LENGTH} caracteres).' + BT,
     BT + 'ZERNIO_WEBHOOK_SECRET is too short (minimum ${MIN_WEBHOOK_SECRET_LENGTH} characters).' + BT),
])
patch("src/lib/agent/tools.ts", [
    (BT + 'That time was just taken. Volvé a consultar disponibilidad.' + BT,
     BT + 'That time was just taken. Check availability again.' + BT),
])
patch("src/lib/import/historial.ts", [
    (BT + '${day}: ${barbero ? barbero.toLowerCase() : concept} tiene ${n} en cantidad but no amount recorded (those services were not imported).' + BT,
     BT + '${day}: ${barbero ? barbero.toLowerCase() : concept} has quantity ${n} but no amount recorded (those services were not imported).' + BT),
    (BT + '${day}: fila "${l.label.toLowerCase()}" is not a known staff member: se cargó ${l.cash + l.tr} without an assigned staff member.' + BT,
     BT + '${day}: row "${l.label.toLowerCase()}" is not a known staff member: ${l.cash + l.tr} was loaded without an assigned staff member.' + BT),
    (BT + '${tarjetas[tarjetas.length - 1].name}: el teléfono "${String(a)}" does not have 10 digits (not loaded).' + BT,
     BT + '${tarjetas[tarjetas.length - 1].name}: phone "${String(a)}" does not have 10 digits (not loaded).' + BT),
])


patch("src/lib/zernio/actions.ts", [
    ('"ZERNIO_PROFILE_ID is missing: creá en Zernio un profile for Booking (each profile supports one WhatsApp account)."',
     '"ZERNIO_PROFILE_ID is missing: create a Zernio profile for Booking (each profile supports one WhatsApp account)."'),
])
patch("src/lib/import/historial.ts", [
    (BT + '${day}: ${barbero ? barbero.toLowerCase() : concept} tiene ${n} quantity but no amount recorded (those services were not imported).' + BT,
     BT + '${day}: ${barbero ? barbero.toLowerCase() : concept} has quantity ${n} but no amount recorded (those services were not imported).' + BT),
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
            or re.search(r'\.(?:agente|servicios|cliente|barbero)\b', stripped)
            or re.search(r'\b(?:tab|source|author|kind)\s*===?\s*["\'](?:servicios|agente|cliente|servicio)["\']', stripped)
            or ("select " in stripped.lower() and " kind = " in stripped.lower())
            or stripped.startswith("const push = (barbero:")
            or "/bandeja?" in stripped
            or re.search(r'\[\s*\d+\s*,\s*["\']cliente["\']\s*,', stripped)
            or ("barbero ? barbero.toLowerCase()" in stripped and "has quantity" in stripped)
            or ('push(null, "servicio"' in stripped and "History ·" in stripped)
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


# Last-mile, exact visible strings only. Never alter technical keys or payment values.
patch("src/app/pago/page.tsx", [
    ("Estamos confirmando tu pago", "We are confirming your payment"),
])
patch("src/components/caja/quick-charge-dialog.tsx", [
    (">Medio de pago<", ">Payment method<"),
])
patch("src/components/caja/charge-dialog.tsx", [
    (">Medio de pago<", ">Payment method<"),
])
patch("src/app/api/mercadopago/webhook/route.ts", [
    ('"sin id de pago"', '"missing payment ID"'),
    ('"[mercadopago] no se pudo consultar el pago"', '"[mercadopago] could not retrieve the payment"'),
])
