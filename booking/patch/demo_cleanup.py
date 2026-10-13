from pathlib import Path

p = Path("/app/src/lib/data/seed.ts")
s = p.read_text(encoding="utf-8")

pairs = [
    ('const DAY_NAMES = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]',
     'const DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]'),
    ('day === today ? "hoy" : day === addDays(today, 1) ? "mañana" :',
     'day === today ? "today" : day === addDays(today, 1) ? "tomorrow" :'),
    ('Agendó un turno para ', 'Created a booking for '),
    ('Reprogramó el turno de ', 'Rescheduled the booking for '),
    ('Canceló el turno de ', 'Cancelled the booking for '),
    ('Le informó los sellos a ', 'Shared loyalty status with '),
    ('Respondió una consulta de ', 'Answered a question from '),
    ('Hoy me quedan ', 'Today I still have '),
    ('¿Te reservo alguno?', 'Would you like me to book one?'),
    ('Hoy ya estamos completos', "We're fully booked today"),
    ('tengo lugar desde las 11:00. ¿Te sirve?', 'I have availability from 11:00. Does that work?'),
    ('¡Tenés la tarjeta completa, Gonza!', 'Your loyalty card is complete!'),
    ('Tu próximo corte sale al 50%. ¿Te busco turno?', 'Your next service is 50% off. Shall I find a time for you?'),
    ('y el siguiente corte te sale al 50%', 'and your next service is 50% off'),
    ('Oncativo 2022', 'our location'),
]
for old, new in pairs:
    s = s.replace(old, new)

# Template literal article: build the marker without embedding a JavaScript template
# expression inside this Python source.
tick = chr(96)
s = s.replace(tick + "el $" + "{DAY_NAMES", tick + "on $" + "{DAY_NAMES")

p.write_text(s, encoding="utf-8")
print("DEMO_LOCALIZATION_APPLIED")
