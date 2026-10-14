from pathlib import Path
root=Path("/app/src")
# Full sentence replacements only. Do not touch enums, database keys, SQL,
# function names, identifiers or payment-provider brand names.
FIXES={
 "app/(panel)/page.tsx":{
  "agendados":"scheduled",
  "sillas":"chairs",
  "libre":"available",
 },
 "components/settings/team-editor.tsx":{
  "Edit to staff member to set their commission percentage. Weekly payroll is shown under Finance.":
   "Select an employee to update their commission, working hours and access. Payroll is managed under Finance.",
 },
 "components/finance/week-view.tsx":{
  "To pay = comisión + tips − vales − pagos ya hechos. Los owners no cobran comisión: lo que facturan queda en la casa.":
   "Amount due = commission + tips − advances − payments already made. Owners do not receive commissions; revenue from their services belongs to the business.",
  "Registrar pago":"Record payment",
 },
 "components/caja/caja-view.tsx":{
  "Mercado Payment":"Mercado Pago",
  ">Cargar<":">Add expense<",
 },
 "components/clients/clients-view.tsx":{
  'label: "Frecuentes"':'label: "Regular"',
  'label: "Nuevos"':'label: "New"',
 },
 "components/inbox/inbox.tsx":{
  'Sin leer':'Unread',
  'La IA':'AI',
 },
 "app/(panel)/ranks/page.tsx":{
  "each levon can provide":"each level can provide",
  "add to rule":"add a rule",
 },
 "app/(panel)/analytics/page.tsx":{
  "It is not to verified cash-drawer balance":"It is not a verified cash-drawer balance",
 },
 "components/agent/agent-settings.tsx":{
  "Cancon bookings":"Cancel bookings",
  "Write as to client":"Write as a client",
 },
 "components/agent/playground.tsx":{
  "Write as to client":"Write as a client",
 },
 "app/(panel)/agente/page.tsx":{
  "needs to person":"needs a person",
  "HANDED OFF TO TO PERSON":"HANDED OFF TO STAFF",
  "los ya atendidos":"for completed visits",
  "Activo":"Active",
  "Pausar":"Pause",
  "Falta GEMINI_API_KEY is missing":"GEMINI_API_KEY is missing",
  "Falta GEMINI_API_KEY":"GEMINI_API_KEY is missing",
 },
 "app/login/login-form.tsx":{
  "Admin panon password":"Administrator password",
 },
 "components/booking/booking-flow.tsx":{
  "Choose to specialist":"Choose a specialist",
  "Choose to service":"Choose a service",
 },
 "app/reservar/page.tsx":{
  "Choose to specialist":"Choose a specialist",
  "Choose to service":"Choose a service",
 },
}
changed=[]
for path,changes in FIXES.items():
 p=root/path
 if not p.exists():continue
 s=p.read_text(encoding="utf-8")
 n=0
 for old,new in changes.items():
  if old in s:
   s=s.replace(old,new)
   n+=1
 if n:
  p.write_text(s,encoding="utf-8")
  changed.append(f"{path}:{n}")
print("BOOKING_PRECISE_COPY_REPAIRS",len(changed)," | ".join(changed))
