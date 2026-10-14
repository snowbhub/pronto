from pathlib import Path
root=Path("/app")
src=Path("/tmp/booking-patch/calendar-page.tsx")
(root/"src/app/(panel)/agenda/page.tsx").write_text(src.read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/components/agenda/day-grid.tsx"
s=p.read_text(encoding="utf-8")
needle='  const visibleStaff=mobileMode?staff.filter(s=>s.id===selectedStaffId):staff'
if needle not in s:raise RuntimeError("Expected responsive timeline patch missing")
s=s.replace(needle,'''  const [displayMode,setDisplayMode]=useState<"team"|"single">("team")
  const visibleStaff=mobileMode&&displayMode==="single"?staff.filter(s=>s.id===selectedStaffId):staff''')
start=s.index('        {mobileMode && staff.length>0 && <div className="grid grid-cols-2')
end=s.index('        <div className={mobileMode?',start)
s=s[:start]+'''        {mobileMode && staff.length>0 && <div className="border-b border-line p-2.5">
          <div className="grid grid-cols-2 gap-2 rounded-xl border border-line-strong bg-surface-1 p-1">
            <button type="button" aria-pressed={displayMode==="team"} onClick={()=>setDisplayMode("team")}
              className={cn("rounded-lg px-3 py-2.5 text-xs font-semibold transition-colors",displayMode==="team"?"bg-surface-3 text-ivory":"text-ivory-3")}>Team · all barbers</button>
            <button type="button" aria-pressed={displayMode==="single"} onClick={()=>setDisplayMode("single")}
              className={cn("rounded-lg px-3 py-2.5 text-xs font-semibold transition-colors",displayMode==="single"?"bg-surface-3 text-ivory":"text-ivory-3")}>One barber</button>
          </div>
          {displayMode==="single" && <div className="mt-2 flex gap-1.5 overflow-x-auto">
            {staff.map(member=><button key={member.id} type="button" onClick={()=>setSelectedStaffId(member.id)}
              className={cn("shrink-0 rounded-lg border px-3 py-2 text-xs",selectedStaffId===member.id?"border-ivory-2 bg-surface-3":"border-line bg-surface-1")}>
              {member.name}
            </button>)}
          </div>}
        </div>}
''' + s[end:]
s=s.replace('''<div className={mobileMode?"overflow-x-hidden":"overflow-x-auto scroll-thin"}>
          <div className={mobileMode?"w-full min-w-0":"min-w-[620px]"}>''',
'''<div data-calendar-scroll className={mobileMode&&displayMode==="single"?"overflow-x-hidden":"overflow-x-auto scroll-thin"}>
          <div style={mobileMode&&displayMode==="team"?{minWidth:56+Math.max(1,visibleStaff.length)*150}:undefined}
            className={mobileMode&&displayMode==="single"?"w-full min-w-0":!mobileMode?"min-w-[620px]":"w-full"}>''')
s=s.replace('''<span className="truncate">{service.name}</span>''','''<span className="truncate">{service.name}</span>
                              {paid.has(a.id) && <span className="ml-auto shrink-0 rounded bg-ok/15 px-1 py-0.5 text-[10px] font-semibold text-ok">Paid</span>}''',1)
s=s.replace('''{paid && <span className="text-[11px] font-medium text-ok">Cobrado</span>}''','''<span className={cn("rounded-full px-2 py-0.5 text-[11px] font-semibold",paid?"bg-ok/15 text-ok":"bg-surface-3 text-ivory-2")}>
                  {paid?"Paid":"Unpaid"}
                </span>''')
s=s.replace('''<SheetContent className="w-full border-line sm:max-w-[420px]">''','''<SheetContent className="w-full min-w-0 max-w-full border-line sm:max-w-[420px]">''')
if 'Team · all barbers' not in s or 'Unpaid' not in s:raise RuntimeError("Calendar workspace patch failed")
# Expand the timeline to include real worker shifts and existing bookings.
s=s.replace('''  const openMin = hmToMinutes(BRAND.openingHours.open)
  const closeMin = hmToMinutes(BRAND.openingHours.close)''','''  const weekday=new Date(day+"T12:00:00Z").getUTCDay()
  const shiftBounds=staff.flatMap(member=>(member.schedule||[])
    .filter(shift=>shift.weekday===weekday)
    .flatMap(shift=>[hmToMinutes(shift.start),hmToMinutes(shift.end)]))
  const appointmentBounds=appointments.flatMap(a=>[minutesOfDay(a.startsAt),minutesOfDay(a.endsAt)])
  const lower=Math.min(hmToMinutes(BRAND.openingHours.open),...shiftBounds,...appointmentBounds)
  const upper=Math.max(hmToMinutes(BRAND.openingHours.close),...shiftBounds,...appointmentBounds)
  const openMin=Math.max(0,Math.floor(lower/60)*60)
  const closeMin=Math.min(1440,Math.ceil(upper/60)*60)''')
p.write_text(s,encoding="utf-8")
p=root/"src/lib/data/queries.ts"
s=p.read_text(encoding="utf-8")
s=s.replace('import { addDays, addMonths, dayKey, daysInMonth, monthKey, weekStart } from "@/lib/time"',
'''import { addDays, addMonths, dayKey, daysInMonth, monthKey, weekStart, weekday } from "@/lib/time"''')
s=s.replace('''    open: isOpen(day),
    staff: s.staff,''','''    open: isOpen(day) || s.staff.some(m=>m.active && m.schedule?.some(shift=>shift.weekday===weekday(day))) ||
      s.appointments.some(a=>dayKey(a.startsAt)===day),
    staff: s.staff,''')
s=s.replace('''        open: isOpen(d),
        count: appts.filter(ACTIVE).length,''','''        open: isOpen(d) || s.staff.some(m=>m.active&&m.schedule?.some(shift=>shift.weekday===weekday(d))) || appts.length>0,
        count: appts.filter(ACTIVE).length,''')
p.write_text(s,encoding="utf-8")
p=root/"src/app/globals.css"
s=p.read_text(encoding="utf-8")
s+='''

/* Calendar and admin never share fixed navigation or page-wide overflow. */
[data-booking-workspace="calendar"] { width:100%; max-width:100vw; isolation:isolate; }
[data-booking-workspace="calendar"] main { scrollbar-gutter:stable; }
[data-booking-workspace="calendar"] [data-calendar-scroll] { width:100%;max-width:100%;overscroll-behavior-x:contain; }
[data-booking-workspace="calendar"] [data-calendar-scroll] button { overflow-wrap:anywhere; }
[data-booking-workspace="calendar"] .panel { border-radius:16px; }
@media(max-width:767px) {
 [data-booking-workspace="calendar"] [data-calendar-scroll] {scrollbar-width:thin;}
 [data-booking-workspace="calendar"] [data-calendar-scroll] .grid {min-width:0;}
 [data-booking-workspace="calendar"] [data-calendar-scroll] button {min-width:0;padding-left:5px;padding-right:5px;}
}
'''
p.write_text(s,encoding="utf-8")
print("BOOKING_CALENDAR_MODE_SCREEN_INSTALLED")
