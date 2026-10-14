from pathlib import Path
root=Path("/app/src")
# Analytics period identifiers stay unchanged; render canonical English labels.
p=root/"app/(panel)/analytics/page.tsx"
s=p.read_text(encoding="utf-8")
anchor='type Period="day"|"week"|"month"|"year"|"custom"'
if anchor not in s:raise RuntimeError("Analytics period declaration moved")
s=s.replace(anchor,anchor+'\nconst periodLabels:Record<Period,string>={day:"Day",week:"Week",month:"Month",year:"Year",custom:"Custom"}',1)
anchor='>{k}</Link>)}</nav>'
if anchor not in s:raise RuntimeError("Analytics navigation markup moved")
s=s.replace(anchor,'>{periodLabels[k]}</Link>)}</nav>',1)
p.write_text(s,encoding="utf-8")

# AI disclosure had hard-coded Spanish fragments around a dynamic model name.
# Rewrite only human-readable sentences; retain model and configuration state.
p=root/"app/(panel)/agente/page.tsx"
s=p.read_text(encoding="utf-8")
if "Modelo: " not in s and "Model: " not in s:
    raise RuntimeError("AI model status label changed")
s=s.replace("Modelo: ","Model: ").replace('"sin configurar"','"not configured"')
begin=s.find(". Cada respuesta se arma con los precios, horarios y")
if begin<0:raise RuntimeError("AI disclosure phrase changed")
end=s.find("memoria.",begin)
if end<0:raise RuntimeError("AI disclosure second line changed")
s=s[:begin]+". Replies use the configured prices, opening hours and rules. The calendar is checked live, not from memory."+s[end+len("memoria."):]
p.write_text(s,encoding="utf-8")
print("BOOKING_ANALYTICS_AND_AI_LAST_MILE_COPY_READY")
