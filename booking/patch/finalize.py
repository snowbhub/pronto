from pathlib import Path
import re
ROOT = Path("/app")

def patch(path, pairs):
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    hits = 0
    for old, new in pairs:
        if old in s:
            s = s.replace(old, new)
            hits += 1
    p.write_text(s, encoding="utf-8")
    print("FINALIZE", path, hits, "/", len(pairs))

patch("src/app/(panel)/page.tsx", [
    ("Quedan ", "There are "),
    (" turnos por atender. El agente agendó ", " bookings left to serve. The AI Agent created "),
    (" por su cuenta hoy.", " automatically today."),
    ("¡Hola ", "Hi "),
    ("! Hace un tiempo que no te vemos por Booking 💈 ¿Te busco un turno esta semana?", "! It has been a while since your last visit. Would you like a booking this week?"),
])

patch("src/app/(panel)/finanzas/page.tsx", [
    (" turnos", " bookings"),
    (" servicios", " services"),
    (" · dueño", " · owner"),
])

patch("src/app/(panel)/ajustes/page.tsx", [
    ("Pendiente: definir con Booking si cobran seña al reservar.", "Pending: configure whether a deposit is required for booking."),
    ("Not connected. Generá el link y mandáselo al dueño: lo abre en una compu y escanea el QR con el celular del local (sigue usando WhatsApp Business como siempre).", "Not connected. Generate the connection link, open it on a computer and scan the QR code with the business phone."),
    ("Not connected. Tiene que ser una cuenta profesional vinculada a una página de Facebook.", "Not connected. A professional account linked to a Facebook page is required."),
])

patch("src/app/(panel)/agenda/page.tsx", [(" turnos", " bookings")])

patch("src/app/conectado/page.tsx", [
    ("El {canal} no quedó conectado", "The {canal} connection was not completed"),
    (" Avisale a quien te mandó el link y lo intentan de nuevo.", " Please try the connection again."),
])

patch("src/components/caja/caja-view.tsx", [
    ("Entró {isToday ? ", "Received {isToday ? "),
    (" propina", " tip"),
])

patch("src/components/settings/fixed-slots-editor.tsx", [
    ("Saved. Note: there are already ", "Saved. Note: "),
    (" turno", " booking"),
    (" cargado", " already existing"),
])

patch("src/components/settings/team-editor.tsx", [
    ("Guardado. Ojo: ", "Saved. Note: "),
    (" turno", " booking"),
    ("Barbero · ", "Staff member · "),
    ("% de comisión + propinas", "% commission + tips"),
])

patch("src/components/hoy/day-timeline.tsx", [
    ("un solo día", "one day only"),
    ("todas las semanas", "every week"),
])

patch("src/components/hoy/quick-appointment.tsx", [("Hoy, de ", "Today, ")])
patch("src/components/agenda/new-appointment.tsx", [("Horario con ", "Time with ")])

patch("src/components/agenda/day-grid.tsx", [
    (" turnos ·", " bookings ·"),
    (", de ", ", "),
    (". Se edita en Ajustes.", ". Edit in Settings."),
    ("Fixed booking · un solo día", "Fixed booking · one day only"),
    ("Fixed booking · todas las semanas", "Fixed booking · every week"),
])

patch("src/components/agent/playground.tsx", [
    (" Cargala en ", " Add it to "),
    (" y reiniciá el servidor.", " and restart the server."),
])

patch("src/components/finance/charts.tsx", [
    ("Día ", "Day "),
    (" por día", " per day"),
])
patch("src/components/finance/week-view.tsx", [(" gastos", " expenses")])

patch("src/components/booking/booking-flow.tsx", [
    (" Tenés", " You have"),
    (" minutos: si no llega el pago, el horario se libera solo.", " minutes. If payment does not arrive, the slot is released automatically."),
])

patch("src/components/inbox/inbox.tsx", [
    ("Podés sacar turno directo desde acá: /reservar", "You can book directly here: /reservar"),
])

patch("src/components/shell/topbar.tsx", [("Booking — Hoy", "Booking — Today")])
patch("src/components/shell/sidebar.tsx", [
    ("Booking — Hoy", "Booking — Today"),
    ("Agente en línea", "AI Agent online"),
    ("Agente pausado", "AI Agent paused"),
])

patch("src/components/clients/loyalty-card.tsx", [
    ('background="#0b0a09"', 'background="var(--surface-1)"'),
    ('color="#fff3c9"', 'color="var(--ivory)"'),
])
patch("src/components/brand/intro.tsx", [("Barbershop · Lanús Este", "Appointments")])

patch("src/lib/data/seed.ts", [
    ("Asistente Virex", "Booking Assistant"),
    ("Asistente Booking", "Booking Assistant"),
    ("Buenas! hasta qué hora están hoy?", "Hi! What time are you open until today?"),
    ("tienen turno hoy?", "Do you have an appointment today?"),
    ("Reclamo por un corte", "Complaint about a service"),
    ("Hola, el corte de ayer me quedó desparejo del lado izquierdo, se nota bastante", "Hi, yesterday's service turned out uneven on the left side and it is quite noticeable"),
    ("Uh Ezequiel, lamento mucho eso. Ya le aviso a Santiago para que lo vea personalmente y te escriba en un rato para solucionarlo. 🙏", "I'm sorry about that. I'll pass this to the team so someone can review it and contact you shortly. 🙏"),
    ("ok espero", "Okay, I'll wait"),
    ("Pregunta por platinado: no está en la lista de servicios", "Asked about a service that is not in the service list"),
    ("Hola! hacen platinado? tengo el pelo bastante oscuro", "Hi! Do you offer platinum coloring? My hair is quite dark"),
    ("¡Hola Tomi! Por ahora en el local hacemos corte y corte + barba. Igual le paso tu consulta a Santiago para que te responda él 🙌", "Hi! At the moment we offer the configured core services. I'll pass your question to the team so they can reply. 🙌"),
    ("dale, le mando una foto?", "Okay, should I send a photo?"),
    ("che hoy no llego a las 17, se puede más tarde?", "Hi, I can't make 17:00 today. Is later possible?"),
    ("Sin drama, Franco. Te lo pasé a las 19:00 con Sebastián, mismo servicio (Corte). ¿Te sirve?", "No problem. I moved it to 19:00 with the same service. Does that work?"),
    ("joya gracias", "Perfect, thanks"),
    ("aceptan mercado pago?", "Do you accept Mercado Pago?"),
    ("¡Sí! Aceptamos efectivo, transferencia, Mercado Pago y débito o crédito. 🙌", "Yes! We accept cash, transfer, Mercado Pago, debit and credit cards. 🙌"),
    ("Hola! quería sacar turno para mi hijo de 8 años, el sábado a la mañana", "Hi! I'd like to book my 8-year-old son for Saturday morning"),
    ("si porfa", "Yes please"),
    ("cuántos cortes me faltan para el 50%?", "How many visits are left until the 50% reward?"),
    ("🔥🔥🔥 quedó terrible el corte", "🔥🔥🔥 the haircut turned out great"),
    ("¡Gracias crack! 🙌 Cuando quieras repetir, escribinos y te buscamos turno.", "Thanks! Whenever you want to come again, message us and we'll find a time."),
    ("Santi, el sábado podés a las 12? es para mi casamiento, quiero algo prolijo", "Can I book Saturday at 12:00? It's for my wedding and I'd like something neat"),
    ("Joaco, te guardé el sábado 12:00 👌 Vení con el pelo lavado y hacemos corte + barba a navaja.", "Saturday 12:00 is reserved. Come with clean hair and we'll provide the configured service."),
    ("crack, gracias!", "Great, thanks!"),
    ("Nunca inventes descuentos ni promociones que no existen.", "Never invent discounts or promotions that do not exist."),
    ("Por ahora el local hace sólo corte y corte + barba. Si piden otra cosa (color, diseño, barba sola), decilo y derivá a Santiago.", "For now, only the configured core services are offered. If someone asks for something else, say so and hand it off to a person."),
    ("Si alguien se queja de un corte, pedí disculpas y derivá a una persona de inmediato.", "If someone complains about a service, apologize and hand the conversation to a person immediately."),
    ("Por Instagram, pedí nombre y teléfono antes de confirmar un turno.", "On Instagram, ask for name and phone before confirming a booking."),
    ("Fuera de horario igual podés agendar, pero aclarás que el local atiende de martes a sábado de 11 a 20.", "Bookings can still be created outside opening hours, but clearly state the configured business hours."),
])

visible_files = [
    "src/app/(panel)/page.tsx","src/app/(panel)/agenda/page.tsx","src/app/(panel)/agente/page.tsx",
    "src/app/(panel)/ajustes/page.tsx","src/app/(panel)/caja/page.tsx","src/app/(panel)/clientes/page.tsx",
    "src/app/(panel)/finanzas/page.tsx","src/app/conectado/page.tsx","src/app/login/page.tsx",
    "src/app/login/login-form.tsx","src/app/pago/page.tsx","src/app/reservar/page.tsx",
    "src/components/agenda/day-grid.tsx","src/components/agenda/new-appointment.tsx",
    "src/components/caja/caja-view.tsx","src/components/caja/charge-dialog.tsx",
    "src/components/caja/expense-dialog.tsx","src/components/caja/quick-charge-dialog.tsx",
    "src/components/clients/clients-view.tsx","src/components/clients/loyalty-card.tsx",
    "src/components/settings/fixed-slots-editor.tsx","src/components/settings/services-editor.tsx",
    "src/components/settings/team-editor.tsx","src/components/hoy/agent-live-card.tsx",
    "src/components/hoy/day-timeline.tsx","src/components/hoy/quick-appointment.tsx",
    "src/components/inbox/inbox.tsx","src/components/agent/agent-settings.tsx",
    "src/components/agent/agent-toggle.tsx","src/components/agent/playground.tsx",
    "src/components/booking/booking-flow.tsx","src/components/shell/mobile-nav.tsx",
    "src/components/shell/sidebar.tsx","src/components/shell/topbar.tsx",
    "src/components/finance/charts.tsx","src/components/finance/week-view.tsx"
]
marker = re.compile(r"[¿¡áéíóúñü]|\b(?:turno|turnos|barbero|barberos|cliente|clientes|caja|finanzas|ajustes|bandeja|agente|fidelidad|gasto|gastos|seña|guardar|elegí|revisá|dueño|hoy|mañana|servicio|servicios|propina|horario|semana|mes|cobro|cerrado|ingresos|desde|hasta|cuánto|corte)\b", re.I)
res = []
for rel in visible_files:
    p = ROOT / rel
    if not p.exists(): continue
    for i,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
        st = line.strip()
        if st.startswith(("//","*","/*","import ")): continue
        if marker.search(line): res.append(f"{rel}:{i}: {st[:220]}")
print("FINAL_VISIBLE_RESIDUALS", len(res))
for x in res[:160]: print("FINAL_VISIBLE", x)
