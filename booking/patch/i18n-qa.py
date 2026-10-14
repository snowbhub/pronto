from pathlib import Path
import json,re,sys
root=Path("/app")
bundle=Path("/tmp/booking-patch")
rows=[]
for p in sorted(bundle.glob("rows*.json")):
 rows += json.loads(p.read_text(encoding="utf-8"))
english={}
conflicts=[]
for es,en,de,uk in rows:
 if en in english and english[en]!=(de,uk):
  conflicts.append((en,english[en],(de,uk)))
 else:english[en]=(de,uk)
# English inputs in newly built features are localized by the shared bridge.
critical={
 "src/app/(panel)/inventory/page.tsx":["Products & stock","New product","Stock balance","Add product","Sale price","Quantity"],
 "src/app/(panel)/payroll/page.tsx":["Staff payroll","Commission","Tips","Advances","Paid","Apply date range"],
 "src/app/(panel)/staff-accounts/page.tsx":["Staff accounts","Username","New password (at least 12 characters)"],
 "src/app/staff-login/page.tsx":["Staff sign in","Administrator sign in"],
 "src/app/staff/page.tsx":["My schedule","Upcoming appointments","New appointment"],
 "src/app/(panel)/ranks/page.tsx":["Barber levels","Service permissions by rank","Professional level"],
}
missing=[]
for rel,phrases in critical.items():
 source=(root/rel).read_text(encoding="utf-8")
 for phrase in phrases:
  if phrase not in source:missing.append(f"{rel}: source string missing: {phrase}")
  if phrase not in english:missing.append(f"{rel}: translation missing: {phrase}")
  else:
   de,uk=english[phrase]
   if not re.search(r"[А-Яа-яІіЇїЄєҐґ]",uk):missing.append(f"{rel}: Ukrainian missing: {phrase}")
print("BOOKING_I18N_QA", "entries",len(rows),"critical_checks",sum(map(len,critical.values())),"conflicts",len(conflicts),"missing",len(missing))
for item in conflicts[:30]:print("I18N_CONFLICT",repr(item))
for item in missing:print("I18N_MISSING",item)
if missing:sys.exit(1)
