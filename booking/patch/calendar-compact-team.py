from pathlib import Path
import re

root = Path("/app")
p = root / "src/components/agenda/day-grid.tsx"
s = p.read_text(encoding="utf-8")

s = s.replace(
    'import { useEffect, useState, useTransition } from "react"',
    'import { useEffect, useRef, useState, useTransition } from "react"',
    1,
)
s = s.replace(
    'import { Bot, Footprints, MessageCircle, Phone, Pin, Scissors, Sparkles, StickyNote } from "lucide-react"',
    'import { Bot, ChevronLeft, ChevronRight, Footprints, MessageCircle, Phone, Pin, Scissors, Sparkles, StickyNote } from "lucide-react"',
    1,
)

# Remove the old one-barber picker and keep every active worker in the timeline.
s, n = re.subn(
    r'\n  const \[selectedStaffId,setSelectedStaffId\].*?\n  const \[displayMode,setDisplayMode\]=useState<"team"\|"single">\("single"\)\n  const visibleStaff=[^\n]*\n',
    '\n  const visibleStaff=staff\n',
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError("Mobile barber selector state changed")
s = s.replace(
    '  const [chargingId, setChargingId] = useState<string | null>(null)',
    '  const [chargingId, setChargingId] = useState<string | null>(null)\n  const staffScrollRef=useRef<HTMLDivElement>(null)',
    1,
)

# Replace the team/single toggle and the narrow one-column scroller.
start = s.find('        {mobileMode && staff.length>0 && <div className="border-b border-line p-2.5">')
scroll = s.find('        <div data-calendar-scroll', start)
if start < 0 or scroll < 0:
    raise RuntimeError("Calendar staff toggle markup changed")
grid = s.find('          <div style={mobileMode&&displayMode==="team"?', scroll)
grid_end = s.find('\n', s.find('>', s.find('className={mobileMode&&displayMode==="single"', grid))) if grid >= 0 else -1
if grid < 0 or grid_end < 0:
    raise RuntimeError("Calendar scroller markup changed")
s = s[:start] + '''        {mobileMode && staff.length>3 && <div className="flex items-center justify-end gap-1 border-b border-line px-2 py-1 sm:hidden">
          <button type="button" data-testid="calendar-staff-prev" aria-label="←" onClick={()=>staffScrollRef.current?.scrollBy({left:-Math.max(112,staffScrollRef.current.clientWidth-48),behavior:"smooth"})}
            className="grid size-8 place-items-center rounded-lg border border-line-strong bg-surface-1 text-ivory-2"><ChevronLeft className="size-4"/></button>
          <button type="button" data-testid="calendar-staff-next" aria-label="→" onClick={()=>staffScrollRef.current?.scrollBy({left:Math.max(112,staffScrollRef.current.clientWidth-48),behavior:"smooth"})}
            className="grid size-8 place-items-center rounded-lg border border-line-strong bg-surface-1 text-ivory-2"><ChevronRight className="size-4"/></button>
        </div>}
        <div ref={staffScrollRef} data-calendar-scroll aria-label="Barber timeline" data-visible-staff={staff.length} className="min-w-0 overflow-x-auto overflow-y-hidden overscroll-x-contain scroll-thin">
          <div data-calendar-grid className={mobileMode?"min-w-full":"min-w-[620px]"} style={{minWidth:mobileMode&&staff.length>3?44+staff.length*112:undefined}}>
''' + s[grid_end+1:]

# Three columns fill the phone; larger teams scroll within the calendar only.
column_re = r'gridTemplateColumns: \x6056px repeat\(\x24\{visibleStaff\.length\}, minmax\(0,1fr\)\)\x60'
s, n = re.subn(column_re, 'gridTemplateColumns: "44px repeat("+staff.length+", minmax("+(mobileMode&&staff.length>3?"112px":"0px")+",1fr))"', s)
if n != 2:
    raise RuntimeError("Expected two calendar grid column definitions, found "+str(n))
s = s.replace(
    '<div className="grid border-b border-line" style={{ gridTemplateColumns:',
    '<div data-staff-header className="grid border-b border-line" style={{ gridTemplateColumns:',
    1,
)
s = s.replace(
    '''              <div />
              {visibleStaff.map((s) => {''',
    '''              <div className="sticky left-0 z-30 bg-obsidian" />
              {visibleStaff.map((s) => {''',
    1,
)
s = s.replace(
    '<div className="relative">',
    '<div data-time-rail className="sticky left-0 z-20 bg-obsidian">',
    1,
)
s = s.replace('gap-2.5 border-l border-line px-4 py-3', 'gap-1.5 border-l border-line px-1.5 py-2')

# Softer status colors: active bookings orange, completed yellow, cancelled red.
status_colors = {
    'border-l-emerald-600 bg-emerald-500/10 ring-1 ring-emerald-500/25 ring-inset':
        'border-l-amber-500 bg-amber-400/15 ring-1 ring-amber-400/25 ring-inset',
    'border-l-teal-600 bg-teal-500/15 ring-1 ring-teal-500/30 ring-inset':
        'border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset',
    'border-l-amber-500 bg-amber-500/12 ring-1 ring-amber-500/25 ring-inset hover:bg-amber-500/15':
        'border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset',
    'border-l-violet-500 bg-violet-500/12 ring-1 ring-violet-500/25 ring-inset':
        'border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset',
    'border-l-rose-500 bg-rose-500/10 opacity-70 ring-1 ring-rose-500/20 ring-inset':
        'border-l-rose-500 bg-rose-400/15 opacity-85 ring-1 ring-rose-400/30 ring-inset',
}
for old, new in status_colors.items():
    if old not in s:
        raise RuntimeError("Calendar status style changed: "+old)
    s = s.replace(old, new, 1)
s = s.replace(
    'bg-black/30 bg-[repeating-linear-gradient(135deg,transparent_0_6px,rgb(255_255_255/0.02)_6px_12px)]',
    'bg-amber-400/10 bg-[repeating-linear-gradient(135deg,transparent_0_6px,rgb(180_120_20/0.035)_6px_12px)]',
    1,
)

p.write_text(s, encoding="utf-8")

# Keep the mobile date header to one compact line.
p = root / "src/app/(panel)/agenda/page.tsx"
s = p.read_text(encoding="utf-8")
s = s.replace(
    'className="inline-grid shrink-0 grid-cols-2 rounded-lg',
    'className="hidden shrink-0 grid-cols-2 rounded-lg sm:inline-grid',
    1,
)
s = s.replace(
    'className="mt-2 grid grid-cols-7 gap-0.5"',
    'className="mt-2 hidden grid-cols-7 gap-0.5 sm:grid"',
    1,
)
p.write_text(s, encoding="utf-8")

# Put language and theme controls in the calendar drawer, while keeping them in
# the normal header (including Settings) throughout the rest of the app.
p = root / "src/components/shell/booking-workspace-shell.tsx"
s = p.read_text(encoding="utf-8")
s = s.replace('       <div id="booking-header-actions"/>\n', '', 1)
old = '''   {open&&<>
     <button type="button" aria-label="Close calendar menu" onClick={()=>setOpen(false)} className="fixed inset-0 z-40 bg-black/60"/>
     <aside className="fixed inset-y-0 left-0 z-50 flex w-[min(84vw,340px)] flex-col overflow-y-auto overscroll-contain border-r border-line bg-obsidian p-4 shadow-2xl" aria-label="Calendar menu">
'''
new = '''   {open&&<button type="button" aria-label="Close calendar menu" onClick={()=>setOpen(false)} className="fixed inset-0 z-40 bg-black/60"/>}
     <aside className={"fixed inset-y-0 left-0 z-50 flex w-[min(84vw,340px)] flex-col overflow-y-auto overscroll-contain border-r border-line bg-obsidian p-4 shadow-2xl transition-transform duration-200 "+(open?"visible translate-x-0":"invisible -translate-x-full pointer-events-none")} aria-label="Calendar menu" aria-hidden={!open} inert={!open}>
'''
if old not in s:
    raise RuntimeError("Calendar drawer structure changed")
s = s.replace(old, new, 1)
s = s.replace(
    '       <CalendarMonthPicker onNavigate={()=>setOpen(false)}/>',
    '       <div className="mb-4 rounded-xl border border-line bg-surface-1 p-3"><div id="booking-calendar-menu-controls"/></div>\n       <CalendarMonthPicker onNavigate={()=>setOpen(false)}/>',
    1,
)
s = s.replace('''   </aside>
   </>}
 </div>''','''   </aside>
 </div>''',1)
if '   </>}' in s:
    raise RuntimeError("Calendar drawer conditional wrapper still present")
p.write_text(s, encoding="utf-8")

p = root / "src/i18n/controls.tsx"
s = p.read_text(encoding="utf-8")
old = '''  useEffect(() => {
    const header = document.getElementById("booking-header-actions") ||
      document.getElementById("booking-public-header-actions")
    setTarget(header)
  }, [pathname])'''
new = '''  useEffect(() => {
    const destination = pathname === "/agenda"
      ? document.getElementById("booking-calendar-menu-controls")
      : document.getElementById("booking-header-actions") || document.getElementById("booking-public-header-actions")
    setTarget(destination)
  }, [pathname])'''
if old not in s:
    raise RuntimeError("Language/theme control mount point changed")
s = s.replace(old, new, 1)
s = s.replace(
    'return target ? createPortal(controls,target) : controls',
    'return target ? createPortal(controls,target) : pathname === "/agenda" ? null : controls',
    1,
)
p.write_text(s, encoding="utf-8")


# Avoid accidental iOS input zoom; leave pinch zoom available to users.
p = root / "src/app/globals.css"
s = p.read_text(encoding="utf-8")
s += """

@media(max-width:767px) {
 [data-booking-workspace="calendar"] [data-calendar-scroll] {touch-action:pan-x pan-y;scrollbar-width:thin;}
 [data-booking-workspace="calendar"] [data-time-rail] {width:44px;}
 [data-booking-workspace="calendar"] [data-staff-header] > div:not(:first-child) {min-height:58px;padding:6px 4px;gap:4px;}
 [data-booking-workspace="calendar"] [data-staff-header] > div:not(:first-child) > span:last-child {min-width:0;overflow:hidden;}
 [data-booking-workspace="calendar"] [data-staff-header] > div:not(:first-child) > span:last-child > span {font-size:11px;line-height:1.2;}
 [data-booking-workspace="calendar"] [data-staff-header] > div:not(:first-child) .num {font-size:10px;}
 [data-booking-workspace="calendar"] input,[data-booking-workspace="calendar"] select,[data-booking-workspace="calendar"] textarea {font-size:16px;}
 [data-booking-workspace="calendar"] {touch-action:manipulation;}
}
"""
p.write_text(s, encoding="utf-8")
print("BOOKING_CALENDAR_COMPACT_THREE_STAFF_INSTALLED")
