from pathlib import Path
root=Path("/app/src")
def require(text, old, replacement, label):
    if old not in text:
        raise RuntimeError("Manual UI polish anchor missing: "+label)
    return text.replace(old,replacement,1)
# Remove redundant Spanish/Ukrainian combinations in the professional level picker.
p=Path("/app/src/app/(panel)/ranks/page.tsx")
s=p.read_text(encoding="utf-8")
for old,new in [("Trainee / Стажер","Trainee"),("Junior / Молодший барбер","Junior barber"),("Barber / Барбер","Barber"),("Senior / Старший барбер","Senior barber")]:
    s=require(s,old,new,"rank "+old)
p.write_text(s,encoding="utf-8")
# Keep employee editing together while hiding 100+ time selector options until requested.
p=root/"components/settings/team-editor.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace("Staff commissions","Employees")
start='''            <ScheduleEditor key={JSON.stringify(m.schedule ?? null)} member={m} />'''
end='''            <TimeOffList entries={timeOff.filter((t) => t.staffId === m.id)} onAdd={() => setOffFor(m.id)} />'''
if start not in s or end not in s:raise RuntimeError("Team card content changed")
s=s.replace(start,'''            <details className="rounded-xl border border-line-strong bg-surface-2 p-3">
              <summary className="cursor-pointer text-sm font-semibold text-ivory">Working hours and absences</summary>
              <div className="mt-4 space-y-4">
'''+start,1)
s=s.replace(end,end+'''
              </div>
            </details>''',1)
p.write_text(s,encoding="utf-8")
# Only names get data-i18n-skip; UI headings continue to translate.
p=root/"components/clients/clients-view.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('''<span className="block truncate text-[14px] font-medium text-ivory">{r.client.name}</span>''',
'''<span data-i18n-skip="true" className="block truncate text-[14px] font-medium text-ivory">{r.client.name}</span>''')
s=s.replace('''<SheetTitle className="font-display text-[24px] leading-tight">{row.client.name}</SheetTitle>''',
'''<SheetTitle data-i18n-skip="true" className="font-display text-[24px] leading-tight">{row.client.name}</SheetTitle>''')
p.write_text(s,encoding="utf-8")
# A complete mobile visit count must be in one text node so Ukrainian plurals
# do not split into a number and an uninflected label.
import re
p=root/"components/clients/clients-view.tsx"
s=p.read_text(encoding="utf-8")
s,visits=re.subn(r'\{r\.visits\}\s*<span className="text-ivory-3 lg:hidden">[^<]*</span>',
    '<span className="lg:hidden">{`\u0024{r.visits} visits`}</span><span className="hidden lg:inline">{r.visits}</span>',s,count=1)
if visits!=1:raise RuntimeError("Client visit counter markup changed")
p.write_text(s,encoding="utf-8")
# Compose a single translated salary summary; React otherwise splits the number
# from "commission"/"services" and runtime plural rules cannot act on the phrase.
p=root/"app/(panel)/payroll/page.tsx"
s=p.read_text(encoding="utf-8")
old="{line.commissionPct}% commission · {line.count} services"
if old not in s:raise RuntimeError("Payroll count wording changed")
s=s.replace(old,'{`\u0024{line.commissionPct}% commission · \u0024{line.count} services`}',1)
p.write_text(s,encoding="utf-8")
# Status is presentation only; appointment status IDs remain untouched.
p=root/"components/agenda/status.tsx"
s=p.read_text(encoding="utf-8")
for old,new in [('pendiente: "Sin confirmar"','pendiente: "Not confirmed"'),
                ('confirmado: "Confirmado"','confirmado: "Confirmed"'),
                ('en_curso: "En curso"','en_curso: "In progress"'),
                ('completado: "Atendido"','completado: "Served"'),
                ('cancelado: "Cancelado"','cancelado: "Cancelled"'),
                ('no_show: "No vino"','no_show: "No-show"')]:
    if old in s:s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
# The calendar displays appointments, not employee revenue (finance belongs to Admin).
p=root/"components/agenda/day-grid.tsx"
s=p.read_text(encoding="utf-8")
lines=s.splitlines(keepends=True)
changed=0
for i,line in enumerate(lines):
    if "{mine.length}" in line and "formatARS(mine.reduce" in line:
        pad=line[:len(line)-len(line.lstrip())]
        lines[i]=pad+"{`${mine.length} bookings`}\n"
        changed+=1
if changed!=1:raise RuntimeError(f"Expected one staff revenue label in day grid; got {changed}")
s="".join(lines)
p.write_text(s,encoding="utf-8")
p=root/"app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('Staff commissions','Employees')
p.write_text(s,encoding="utf-8")
print("BOOKING_MANUAL_UI_POLISH_APPLIED: rank labels, compact staff editor, client names, appointment statuses, calendar privacy")
