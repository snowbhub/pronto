from pathlib import Path
import re
root=Path("/app/src")
trigger=re.compile(r"\b(?:Agendar|Entrar|Empezar|Cobrar|Nuevo turno|No vino|Sin confirmar|Confirmado|Cancelado|Turno fijo|No trabaja hoy|Nadie|Bebida|Cambiar|Falta|Configurar|Guardando|Cargando|Ver chat|Volver|Cerrar|Confirmar turno|Día pasado|Próximamente|Origen|Precio|Propina|Ninguno|Seña|Elegí|Probá|Tenés|Quedan|acaba de|cargado|interesad|Mensaje|Ventana|Local y fidelidad|Servicios|Cortes|Gastos|Ventas|Ingresos|Contado|Tarjeta|Cliente no|Franco|Agregar|Continuar|Horarios|Depósito)\b",re.I)
entries=[]
for p in sorted(root.rglob("*.tsx")):
 if ".test." in p.name:continue
 code=p.read_text(encoding="utf-8")
 # Actual JSX text nodes and user-facing string props.
 visible=[]
 for m in re.finditer(r">(?!\s*\{)([^<>{}\n]{3,})<",code):
  if trigger.search(m.group(1)):visible.append((code.count("\n",0,m.start())+1,m.group(1).strip()))
 for m in re.finditer(r"\b(?:placeholder|aria-label|title|description|label)=(?:\"([^\"\n]+)\"|'([^'\n]+)')",code):
  value=m.group(1) or m.group(2)
  if trigger.search(value):visible.append((code.count("\n",0,m.start())+1,value))
 for line,value in visible[:24]:
  entries.append((str(p.relative_to(root)),line,value[:170]))
print("BOOKING_UI_SOURCE_SPANISH_CANDIDATES",len(entries))
for row in entries[:130]:print("UI_CANDIDATE",*row)
