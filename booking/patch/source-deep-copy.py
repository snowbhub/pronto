from pathlib import Path
import re
root=Path("/app")
MAPPINGS={
 "src/app/(panel)/agente/page.tsx": {
  "Facturaron": "Revenue generated"
 },
 "src/app/(panel)/clientes/page.tsx": {
  "Cartera": "Client portfolio"
 },
 "src/app/(panel)/page.tsx": {
  "La jornada": "Today's schedule"
 },
 "src/app/conectado/page.tsx": {
  "No se pudo conectar": "Could not connect"
 },
 "src/components/agenda/day-grid.tsx": {
  "Le toca el 50%": "50% loyalty discount"
 },
 "src/components/agenda/new-appointment.tsx": {
  "Dura": "Duration",
  "Hora de inicio": "Start time"
 },
 "src/components/agent/agent-settings.tsx": {
  "Canales": "Channels",
  "Personalidad": "Personality",
  "Quitar regla": "Remove rule",
  "Tono": "Tone"
 },
 "src/components/agent/playground.tsx": {
  "Enviar": "Send",
  "Probalo": "Try it"
 },
 "src/components/caja/caja-view.tsx": {
  "Cobros": "Payments",
  "Le toca el 50%": "50% loyalty discount",
  "Nota (opcional): ej. faltan $1.000 del cambio": "Optional note: e.g. the cash drawer is short by 1,000"
 },
 "src/components/caja/expense-dialog.tsx": {
  "Monto": "Amount"
 },
 "src/components/clients/clients-view.tsx": {
  "Gastado": "Spent",
  "visitas": "visits"
 },
 "src/components/clients/loyalty-card.tsx": {
  "Sellado": "Stamped"
 },
 "src/components/finance/week-view.tsx": {
  "A pagar": "To pay",
  "Bebidas y productos": "Drinks and products",
  "Cierre por persona": "Closing per person",
  "Pagado": "Paid",
  "Vales y pagos": "Advances and payments",
  "son de la casa": "belong to the business"
 },
 "src/components/hoy/quick-appointment.tsx": {
  "Lo atiende": "Assigned to"
 },
 "src/components/inbox/inbox.tsx": {
  "Enviar": "Send"
 },
 "src/components/settings/deposit-settings-form.tsx": {
  "Ej. 5000": "e.g. 5000",
  "Minutos para pagar": "Minutes to pay"
 },
 "src/components/settings/fixed-slots-editor.tsx": {
  "Las horas van de 5 en 5 minutos: 17:15 a 18:00, 17:00 a 17:45, lo que necesite.": "You can choose times in 5-minute increments, such as 17:15–18:00 or 17:00–17:45.",
  "· pausado": "· paused"
 },
 "src/components/settings/services-editor.tsx": {
  "(no se ofrece)": "(not offered)",
  "Tipo": "Type"
 },
 "src/components/settings/team-editor.tsx": {
  "(dado de baja)": "(inactive)",
  "Entra": "Starts"
 }
}
updated=[]
for rel, terms in MAPPINGS.items():
 p=root/rel
 if not p.exists():continue
 src=p.read_text(encoding="utf-8")
 before=src
 for original, english in terms.items():
  # Only replace visible JSX text and whole quoted UI values, never TS variables/identifiers.
  src=src.replace(">"+original+"<", ">"+english+"<")
  for quote in ['"',"'"]:
   src=src.replace("="+quote+original+quote, "="+quote+english+quote)
   src=src.replace("("+quote+original+quote+")", "("+quote+english+quote+")")
   src=src.replace(">"+original+"{", ">"+english+"{")
 if src!=before:
  p.write_text(src,encoding="utf-8")
  updated.append(rel)
print("BOOKING_DEEP_COPY_UPDATED",len(updated),*updated,sep=" | ")
