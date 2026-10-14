from pathlib import Path
import re
p=Path("/app/src/app/(panel)/ajustes/page.tsx")
s=p.read_text(encoding="utf-8")
target='''      <div className="mt-5 max-w-3xl">'''
if target not in s:raise RuntimeError("Settings tab content anchor missing")
routes=["/cash-management","/analytics","/payroll","/staff-accounts","/ranks","/inventory"]
removed=[]
lines=s.splitlines(keepends=True)
for route in routes:
 matches=[i for i,line in enumerate(lines) if ('<Link href="'+route+'"') in line and 'className="mb-4' in line]
 if len(matches)!=1:raise RuntimeError(f"Settings feature shortcut {route}: expected 1, found {len(matches)}")
 lines[matches[0]]=""
 removed.append(route)
s="".join(lines)
# Do not put unrelated inventory, cash, salary or analytics ahead of the employee
# editor. Every tab must open directly with its own functional form or list.
# Display the consolidated admin links only in the local/business management tab.
block='''        {tab === "local" && <section className="mb-5 rounded-xl border border-line bg-surface-1 p-3 sm:p-4">
          <h2 className="mb-3 text-sm font-semibold text-ivory">Management</h2>
          <nav aria-label="Management tools" className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {([
              ["/staff-accounts","Staff access"],
              ["/ranks","Professional levels"],
              ["/payroll","Salaries"],
              ["/inventory","Products and stock"],
              ["/cash-management","Cash and expenses"],
              ["/analytics","Analytics"],
            ] as const).map(([href,label])=>
              <Link key={href} href={href} className="flex min-h-12 items-center justify-between gap-2 rounded-lg border border-line-strong bg-surface-2 px-3 py-2 text-xs font-medium text-ivory">
                <span>{label}</span><span aria-hidden>→</span>
              </Link>
            )}
          </nav>
        </section>}
'''
s=s.replace(target,target+"\n"+block,1)
p.write_text(s,encoding="utf-8")
print("BOOKING_SETTINGS_FOCUSED_TABS",",".join(removed))
