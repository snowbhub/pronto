from pathlib import Path
p=Path("/app/src/components/agenda/day-grid.tsx")
s=p.read_text(encoding="utf-8")
pairs=[
  (
   '"absolute inset-x-1.5 overflow-hidden rounded-lg px-2.5 text-left transition-[background-color,transform] hover:z-10 hover:-translate-y-px"',
   '"absolute inset-x-0.5 overflow-hidden rounded-md border-l-[3px] px-2 text-left shadow-sm transition-[background-color,transform] hover:z-10 hover:-translate-y-px"'
  ),
  ('"bg-surface-2 opacity-60 ring-1 ring-line ring-inset hover:opacity-100"',
   '"border-l-emerald-600 bg-emerald-500/10 ring-1 ring-emerald-500/25 ring-inset"'),
  ('"bg-ok/12 ring-1 ring-ok/60 ring-inset"',
   '"border-l-teal-600 bg-teal-500/15 ring-1 ring-teal-500/30 ring-inset"'),
  ('"bg-surface-3 ring-1 ring-line-strong ring-inset hover:bg-[#2c2924]"',
   '"border-l-amber-500 bg-amber-500/12 ring-1 ring-amber-500/25 ring-inset hover:bg-amber-500/15"'),
  ('"bg-surface-2 outline-1 -outline-offset-1 outline-dashed outline-ivory-3/60"',
   '"border-l-violet-500 bg-violet-500/12 ring-1 ring-violet-500/25 ring-inset"'),
  ('"bg-danger/8 line-through opacity-55 ring-1 ring-danger/50 ring-inset"',
   '"border-l-rose-500 bg-rose-500/10 opacity-70 ring-1 ring-rose-500/20 ring-inset"')
]
for a,b in pairs:
 if a not in s:raise RuntimeError("Calendar card source changed: "+a[:90])
 s=s.replace(a,b)
a='''<span className="flex min-w-0 items-baseline gap-1.5">
                            <span className="num shrink-0 text-[11px] text-ivory-3">{hm(a.startsAt)}</span>
                            <span className="truncate text-[13px] font-medium text-ivory">{client?.name}</span>
                          </span>'''
b='''<span className="block min-w-0">
                            <span className="num block truncate text-[10px] font-semibold text-ivory-2">{hm(a.startsAt)}–{hm(a.endsAt)}</span>
                            <span className="block truncate text-[12px] font-semibold leading-4 text-ivory">{client?.name||"Client"}</span>
                          </span>'''
if a not in s:raise RuntimeError("Calendar card text structure changed")
s=s.replace(a,b)
# Keep the timeline internally horizontally scrollable without making the whole phone page draggable.
s=s.replace('data-calendar-scroll className=', 'data-calendar-scroll aria-label="Barber timeline" className=')
p.write_text(s,encoding="utf-8")
print("BOOKING_TIMELINE_CARD_READABILITY_OK")
