from pathlib import Path
root=Path("/app")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text()
s=s.replace('label: "Equipo"','label: "Team & commission"')
s=s.replace('value="Argentina (UTC−3)"','value="America/Argentina/Buenos_Aires (currently fixed in source; editing requires migration)"')
s=s.replace('name: "Base de datos (Supabase)"','name: "PostgreSQL database"')
p.write_text(s)
p=root/"src/components/settings/team-editor.tsx"
s=p.read_text()
s=s.replace('className="space-y-5">\n      {staff.map', 'className="space-y-5">\n      <div className="rounded-xl border border-line-strong bg-surface-2 p-4"><h2 className="text-lg font-semibold text-ivory">Staff commissions</h2><p className="mt-2 text-sm text-ivory-2">Edit a staff member to set their commission percentage. Weekly payroll is shown under Finance.</p></div>\n      {staff.map')
p.write_text(s)
p=root/"src/components/finance/week-view.tsx"
s=p.read_text().replace('min-w-[640px]','min-w-[640px]')
p.write_text(s)
print("BOOKING_PAYROLL_DISCOVERY_APPLIED")
