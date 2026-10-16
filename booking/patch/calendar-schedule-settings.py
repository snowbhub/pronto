from pathlib import Path
import re

root = Path('/app')

def edit(path, old, new, count=1):
    p = root / path
    s = p.read_text(encoding='utf-8')
    if old not in s:
        raise RuntimeError(f'Expected source fragment missing in {path}: {old[:100]!r}')
    s = s.replace(old, new, count)
    p.write_text(s, encoding='utf-8')

# Persistent date-specific schedules and independent calendar settings.
edit('src/lib/domain/types.ts', '  schedule?: WorkShift[]\n', '''  schedule?: WorkShift[]
  /** Date-specific shifts supersede the weekly template, including explicit days off. */
  dateSchedule?: { day: string; works: boolean; shifts: Omit<WorkShift, "weekday">[] }[]
  calendarOpen?: string
  calendarClose?: string
  calendarStepMin?: number
  allowStaffOverlaps?: boolean
'''.replace('+',''))
edit('src/lib/domain/types.ts', '  slotStepMin: number\n', '''  slotStepMin: number
  calendarOpen: string
  calendarClose: string
  calendarStepMin: number
  allowStaffOverlaps: boolean
'''.replace('+',''))

edit('src/lib/data/store/types.ts', '  setStaffSchedule(staffId: string, shifts: WorkShift[]): Promise<void>\n', '''  setStaffSchedule(staffId: string, shifts: WorkShift[]): Promise<void>
  setStaffDateSchedule(staffId: string, day: string, works: boolean, shifts: { start: string; end: string }[]): Promise<void>
'''.replace('+',''))
edit('src/lib/data/store/types.ts', '    newClient?: NewClient\n', '    newClient?: NewClient\n    allowOverlap?: boolean\n')

p = root / 'src/lib/data/store/postgres.ts'
s = p.read_text(encoding='utf-8')
s = s.replace('const [staff, services, clients, appointments, payments, expenses, conversations, messages, settings, shifts, timeOff, shop, closures, fixed] = await Promise.all([', 'const [staff, services, clients, appointments, payments, expenses, conversations, messages, settings, shifts, dateSchedules, timeOff, shop, closures, fixed] = await Promise.all([', 1)
needle = "      sql`select staff_id, weekday, to_char(start_time, 'HH24:MI') as start, to_char(end_time, 'HH24:MI') as \"end\" from staff_schedules order by weekday, start_time`,\n"
if needle not in s: raise RuntimeError('Postgres weekly shift query missing')
s = s.replace(needle, needle + "      sql`select staff_id, to_char(business_day, 'YYYY-MM-DD') as day, works, shifts from staff_schedule_overrides order by business_day`,\n", 1)
s = s.replace('''        schedule: shifts.filter((x) => x.staff_id === r.id).map((x) => ({ weekday: Number(x.weekday), start: x.start as string, end: x.end as string })),
        timeOff:'''.replace('+',''), '''        schedule: shifts.filter((x) => x.staff_id === r.id).map((x) => ({ weekday: Number(x.weekday), start: x.start as string, end: x.end as string })),
        dateSchedule: dateSchedules.filter((x) => x.staff_id === r.id).map((x) => ({ day: String(x.day), works: Boolean(x.works), shifts: (x.shifts as {start:string;end:string}[]) ?? [] })),
        timeOff:'''.replace('+',''), 1)
s = s.replace('''        timezone: String(shop[0].timezone ?? \"Europe/Berlin\"),
      },'''.replace('+',''), '''        timezone: String(shop[0].timezone ?? \"Europe/Berlin\"),
        calendarOpen: String(shop[0].calendar_open ?? '11:00'),
        calendarClose: String(shop[0].calendar_close ?? '20:00'),
        calendarStepMin: Number(shop[0].calendar_step_min ?? 15),
        allowStaffOverlaps: Boolean(shop[0].allow_staff_overlaps ?? false),
      },'''.replace('+',''), 1)
anchor = '''  async addTimeOff({ staffId, startsAt, endsAt, reason }) {'''
method = '''  async setStaffDateSchedule(staffId, day, works, shifts) {
    const sql = sqlClient()
    await sql`insert into staff_schedule_overrides (staff_id, business_day, works, shifts)
              values (${staffId}, ${day}, ${works}, ${sql.json(shifts)})
              on conflict (staff_id, business_day) do update set works = excluded.works, shifts = excluded.shifts, updated_at = now()`
  },

'''
if anchor not in s: raise RuntimeError('Postgres setDateSchedule insertion point missing')
s = s.replace(anchor, method + anchor, 1)
s = s.replace('    if (patch.slotStepMin !== undefined) row.slot_step_min = patch.slotStepMin\n', '''    if (patch.slotStepMin !== undefined) row.slot_step_min = patch.slotStepMin
    if (patch.calendarOpen !== undefined) row.calendar_open = patch.calendarOpen
    if (patch.calendarClose !== undefined) row.calendar_close = patch.calendarClose
    if (patch.calendarStepMin !== undefined) row.calendar_step_min = patch.calendarStepMin
    if (patch.allowStaffOverlaps !== undefined) row.allow_staff_overlaps = patch.allowStaffOverlaps
'''.replace('+',''), 1)
# Staff/admin can create intentional overlaps only after the per-store setting is enabled.
s = s.replace('''  async createAppointment({ appointment, newClient, linkConversationId }) {
    const sql = sqlClient()
    await sweepExpiredHolds(sql)
    return sql.begin(async (tx) => {
      let clientId = appointment.clientId
'''.replace('+',''), '''  async createAppointment({ appointment, newClient, linkConversationId, allowOverlap = false }) {
    const sql = sqlClient()
    await sweepExpiredHolds(sql)
    return sql.begin(async (tx) => {
      const day = String(appointment.startsAt).slice(0, 10)
      await tx`select pg_advisory_xact_lock(hashtext(${appointment.staffId + ':' + day}))`
      if (!allowOverlap || appointment.source === 'web' || appointment.source === 'agente') {
        const overlaps = await tx`select 1 from appointments where staff_id = ${appointment.staffId} and status not in ('cancelado','no_show') and starts_at < ${appointment.endsAt} and ends_at > ${appointment.startsAt} limit 1`
        if (overlaps.length) throw new SlotTakenError()
      }
      let clientId = appointment.clientId
'''.replace('+',''), 1)
p.write_text(s, encoding='utf-8')

p = root / 'src/lib/data/store/memory.ts'
s = p.read_text(encoding='utf-8')
s = s.replace('async createAppointment({ appointment, newClient, linkConversationId }) {', 'async createAppointment({ appointment, newClient, linkConversationId, allowOverlap = false }) {', 1)
s = s.replace('if (overlaps(s, appointment.staffId, appointment.startsAt, appointment.endsAt)) throw new SlotTakenError()', 'if (!allowOverlap && overlaps(s, appointment.staffId, appointment.startsAt, appointment.endsAt)) throw new SlotTakenError()', 1)
s = s.replace('''  async addTimeOff(entry) {''', '''  async setStaffDateSchedule(staffId, day, works, shifts) {
    const m = state().staff.find((x) => x.id === staffId)
    if (!m) return
    const entries = (m.dateSchedule ?? []).filter((x) => x.day !== day)
    entries.push({ day, works, shifts })
    m.dateSchedule = entries.sort((a, b) => a.day.localeCompare(b.day))
  },

  async addTimeOff(entry) {'''.replace('+',''), 1)
p.write_text(s, encoding='utf-8')

# Expose shop-level calendar configuration to calendar and booking calculations.
edit('src/lib/data/repo.ts', '  if (!s.fixedSlots.length) return s\n', '', 1)
edit('src/lib/data/repo.ts', '  return {\n    ...s,\n    staff: s.staff.map((m) => ({\n      ...m,\n      timeOff:', '  return {\n    ...s,\n    staff: s.staff.map((m) => ({\n      ...m,\n      calendarOpen: s.shopSettings.calendarOpen,\n      calendarClose: s.shopSettings.calendarClose,\n      calendarStepMin: s.shopSettings.calendarStepMin,\n      allowStaffOverlaps: s.shopSettings.allowStaffOverlaps,\n      timeOff:', 1)

# Date override takes precedence over the weekly pattern; closed overrides can
# open an exceptional day even when the normal weekday is closed.
p = root / 'src/lib/domain/slots.ts'
s = p.read_text(encoding='utf-8')
s = s.replace('Pick<Staff, \"schedule\">', 'Pick<Staff, \"schedule\" | \"dateSchedule\" | \"calendarOpen\" | \"calendarClose\">')
s = s.replace('staff: Pick<Staff, \"id\" | \"skipsServiceIds\" | \"schedule\" | \"timeOff\">', 'staff: Pick<Staff, \"id\" | \"skipsServiceIds\" | \"schedule\" | \"dateSchedule\" | \"timeOff\" | \"calendarOpen\" | \"calendarClose\">', 1)
s = s.replace('''  const shopOpen = hmToMinutes(BRAND.openingHours.open)
  const shopClose = hmToMinutes(BRAND.openingHours.close)
  if (!staff.schedule) return [[shopOpen, shopClose]]
  const wd = weekday(day)
  return staff.schedule
    .filter((s) => s.weekday === wd)
    .map((s) => [Math.max(shopOpen, hmToMinutes(s.start)), Math.min(shopClose, hmToMinutes(s.end))] as [number, number])'''.replace('+',''), '''  const shopOpen = hmToMinutes(staff.calendarOpen ?? BRAND.openingHours.open)
  const shopClose = hmToMinutes(staff.calendarClose ?? BRAND.openingHours.close)
  const override = staff.dateSchedule?.find((entry) => entry.day === day)
  if (override) return override.works ? override.shifts.map((s) => [Math.max(shopOpen, hmToMinutes(s.start)), Math.min(shopClose, hmToMinutes(s.end))] as [number, number]).filter(([a,b])=>b>a) : []
  if (!staff.schedule) return [[shopOpen, shopClose]]
  const wd = weekday(day)
  return staff.schedule
    .filter((s) => s.weekday === wd)
    .map((s) => [Math.max(shopOpen, hmToMinutes(s.start)), Math.min(shopClose, hmToMinutes(s.end))] as [number, number])'''.replace('+',''), 1)
s = s.replace('export function worksOn(staff: Pick<Staff, "schedule" | "timeOff">, day: string): boolean {\n  if (!isOpen(day)) return false', '''export function worksOn(staff: Pick<Staff, "schedule" | "dateSchedule" | "timeOff" | "calendarOpen" | "calendarClose">, day: string): boolean {
  const override = staff.dateSchedule?.find((entry) => entry.day === day)
  if (override) return override.works && shiftsFor(staff, day).length > 0 && !staff.timeOff?.some((t)=>new Date(t.startsAt)<at(day,"23:59")&&new Date(t.endsAt)>at(day,"00:00"))
  if (!isOpen(day)) return false'''.replace('+',''), 1)
s = s.replace('''  if (!isOpen(day)) return []
  if (staff.skipsServiceIds.includes(service.id)) return []'''.replace('+',''), '''  if (!isOpen(day) && !staff.dateSchedule?.some((entry) => entry.day === day && entry.works)) return []
  if (staff.skipsServiceIds.includes(service.id)) return []'''.replace('+',''), 1)
s = s.replace('const shopOpen = hmToMinutes(BRAND.openingHours.open)\n  const shopClose = hmToMinutes(BRAND.openingHours.close)', 'const shopOpen = hmToMinutes(staff.calendarOpen ?? BRAND.openingHours.open)\n  const shopClose = hmToMinutes(staff.calendarClose ?? BRAND.openingHours.close)', 1)
s = s.replace('staff: Pick<Staff, "id" | "name" | "skipsServiceIds" | "schedule" | "timeOff">', 'staff: Pick<Staff, "id" | "name" | "skipsServiceIds" | "schedule" | "dateSchedule" | "timeOff" | "calendarOpen" | "calendarClose">', 1)
s = s.replace('''  const shopOpen = hmToMinutes(BRAND.openingHours.open)
  const shopClose = hmToMinutes(BRAND.openingHours.close)
  const start = hmToMinutes(time)'''.replace('+',''), '''  const shopOpen = hmToMinutes(staff.calendarOpen ?? BRAND.openingHours.open)
  const shopClose = hmToMinutes(staff.calendarClose ?? BRAND.openingHours.close)
  const start = hmToMinutes(time)'''.replace('+',''), 1)
s = s.replace('  if (!isOpen(day)) return { ok: false, error: "El local está cerrado ese día." }', '  if (!isOpen(day) && !staff.dateSchedule?.some((entry)=>entry.day===day&&entry.works)) return { ok: false, error: "El local está cerrado ese día." }', 1)
s = s.replace('''  const clash = appointments
    .filter((a) => a.staffId === staff.id && BLOCKING.has(a.status) && dayKey(a.startsAt) === day)
    .find((a) => start < minutesOfDay(a.endsAt) && end > minutesOfDay(a.startsAt))
  if (clash) {'''.replace('+',''), '''  const clash = appointments
    .filter((a) => a.staffId === staff.id && BLOCKING.has(a.status) && dayKey(a.startsAt) === day)
    .find((a) => start < minutesOfDay(a.endsAt) && end > minutesOfDay(a.startsAt))
  if (clash && !q.allowOverlap) {'''.replace('+',''), 1)
s = s.replace('  allowPast?: boolean\n}', '  allowPast?: boolean\n  allowOverlap?: boolean\n}', 1)
p.write_text(s, encoding='utf-8')

# Include date-specific openings in public and staff booking calendars while
# keeping the public slot calculation strict against existing appointments.
p = root / 'src/components/agenda/new-appointment.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('  const days = nextOpenDays(today, 8)', '  const days = [...new Set([...nextOpenDays(today, 8), ...catalog.staff.flatMap((m) => (m.dateSchedule ?? []).filter((x) => x.works && x.day >= today).map((x) => x.day))])].sort().slice(0, 12)', 1)
s = s.replace('prefill.day && isOpen(prefill.day) ? prefill.day : days[0]', 'prefill.day && (isOpen(prefill.day) || catalog.staff.some((m) => m.dateSchedule?.some((x) => x.day === prefill.day && x.works))) ? prefill.day : days[0]', 1)
p.write_text(s, encoding='utf-8')

# Calendar day: only scheduled staff, max three columns on phones, one-at-a-time
# paging arrows. The grid itself never pans horizontally or pinch-zooms.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('import { useEffect, useRef, useState, useTransition } from "react"', 'import { useEffect, useState, useTransition } from "react"', 1)
s = s.replace('import { checkStaffTransfer, offHoursFor } from "@/lib/domain/slots"', 'import { checkStaffTransfer, offHoursFor, worksOn } from "@/lib/domain/slots"', 1)
s = s.replace('''  const [mobileMode,setMobileMode] = useState(false)
  const [staffPage,setStaffPage] = useState(0)
  const visibleStaff=mobileMode ? staff.slice(staffPage,staffPage+3) : staff
  useEffect(()=>setStaffPage((page)=>Math.min(page,Math.max(0,staff.length-3))),[staff.length])''', '''  const [mobileMode,setMobileMode] = useState(false)
  const [staffPage,setStaffPage] = useState(0)
  useEffect(()=>{const media=window.matchMedia("(max-width: 767px)");const update=()=>setMobileMode(media.matches);update();media.addEventListener("change",update);return()=>media.removeEventListener("change",update)},[])
  const workingStaff=staff.filter((member)=>member.active&&(worksOn(member,day)||appointments.some((a)=>a.staffId===member.id&&a.status!=="cancelado"&&a.status!=="no_show")))
  const visibleStaff=mobileMode?workingStaff.slice(staffPage,staffPage+3):workingStaff
  useEffect(()=>setStaffPage((page)=>Math.min(page,Math.max(0,workingStaff.length-3))),[workingStaff.length])''', 1)
s = re.sub(r'        \{mobileMode && workingStaff.length>3 && <div className="flex items-center justify-end gap-1 border-b border-line px-2 py-1 sm:hidden">.*?        </div>\}\n', '', s, count=1, flags=re.S)
s = s.replace('''        <div ref={staffScrollRef} data-calendar-scroll aria-label="Barber timeline" data-visible-staff={staff.length} className="min-w-0 overflow-x-auto overflow-y-hidden overscroll-x-contain scroll-thin">
          <div data-calendar-grid className={mobileMode?"min-w-full":"min-w-[620px]"} style={{minWidth:mobileMode&&workingStaff.length>3?44+staff.length*112:undefined}}>'''.replace('+',''), '''        <div data-calendar-scroll aria-label="Barber timeline" data-visible-staff={visibleStaff.length} data-total-staff={workingStaff.length} className="min-w-0 overflow-x-hidden overflow-y-hidden overscroll-x-none">
          <div data-calendar-grid className={mobileMode?"w-full min-w-0":"min-w-[620px]"}>'''.replace('+',''), 1)
s = s.replace('gridTemplateColumns: "44px repeat("+staff.length+", minmax("+(mobileMode&&workingStaff.length>3?"112px":"0px")+",1fr))"', 'gridTemplateColumns: "44px repeat("+visibleStaff.length+", minmax(0,1fr))"', 2)
# Put the paging controls beside the barber names and subtly pin the header.
s = s.replace('<div data-staff-header className="grid border-b border-line"', '<div data-staff-header className="relative grid border-b border-line bg-surface-1 shadow-sm"', 1)
s, arrows_removed = re.subn(r'<div className="sticky left-0 z-30 flex items-center justify-center gap-0\.5 bg-obsidian">\s*\{mobileMode && (?:workingStaff|staff)\.length>3 && <>.*?</>\}\s*</div>', '<div className="sticky left-0 z-30 bg-obsidian" />', s, count=1, flags=re.S)
if arrows_removed != 1: raise RuntimeError('Calendar hour-rail arrows not found')
header = '''              <div className="sticky left-0 z-30 bg-obsidian" />
              {visibleStaff.map((s) => {'''
header_with_controls = '''              <div className="sticky left-0 z-30 bg-obsidian" />
              {mobileMode && workingStaff.length>3 && staffPage>0 && <button type="button" aria-label="Попередні барбери" onClick={()=>setStaffPage((page)=>Math.max(0,page-1))} className="absolute left-1 top-1/2 z-50 grid size-7 -translate-y-1/2 place-items-center rounded-full border border-line-strong bg-surface-2 shadow"><ChevronLeft className="size-4"/></button>}
              {mobileMode && workingStaff.length>3 && staffPage<workingStaff.length-3 && <button type="button" aria-label="Наступні барбери" onClick={()=>setStaffPage((page)=>Math.min(workingStaff.length-3,page+1))} className="absolute right-1 top-1/2 z-50 grid size-7 -translate-y-1/2 place-items-center rounded-full border border-line-strong bg-surface-2 shadow"><ChevronRight className="size-4"/></button>}
              {visibleStaff.map((s) => {'''
if header not in s: raise RuntimeError('Calendar staff header insertion point missing')
s = s.replace(header, header_with_controls, 1)
s = s.replace('border-l-amber-500 bg-amber-400/15 ring-1 ring-amber-400/25 ring-inset', 'border-l-amber-500 bg-amber-300/20 ring-1 ring-amber-300/30 ring-inset', 1)
s = s.replace('border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset', 'border-l-emerald-500 bg-emerald-400/15 ring-1 ring-emerald-400/30 ring-inset', 1)
s = s.replace('a.status === "confirmado" && "border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset"', 'a.status === "confirmado" && "border-l-sky-400 bg-sky-300/15 ring-1 ring-sky-300/30 ring-inset"', 1)
s = s.replace('a.status === "confirmado" && "border-l-slate-400 bg-slate-400/10 ring-1 ring-slate-300/20 ring-inset"', 'a.status === "confirmado" && "border-l-sky-400 bg-sky-300/15 ring-1 ring-sky-300/30 ring-inset"', 1)
s = s.replace('a.status === "pendiente" && "border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset"', 'a.status === "pendiente" && "border-l-sky-400 bg-sky-300/15 ring-1 ring-sky-300/30 ring-inset"', 1)
s = s.replace('bg-amber-400/10 bg-[repeating-linear-gradient(135deg,transparent_0_6px,rgb(180_120_20/0.035)_6px_12px)]', 'bg-surface-2/70', 1)
s = s.replace('const minutes = openMin + Math.floor((e.clientY - rect.top) / PX_PER_MIN / 15) * 15', 'const gridStep = 15\n    const minutes = openMin + Math.floor((e.clientY - rect.top) / PX_PER_MIN / gridStep) * gridStep', 1)
s = s.replace("staff.length>3", "workingStaff.length>3").replace("staff.length-3", "workingStaff.length-3")
# Render the existing professional level under each staff name.
staff_header = s.index('data-staff-header')
rank_anchor = '{s.name}</span>'
rank_at = s.find(rank_anchor, staff_header)
if rank_at < 0: raise RuntimeError('Staff name in calendar header is missing')
rank_at += len(rank_anchor)
s = s[:rank_at] + '\n                      <span className="block truncate text-[10px] font-medium text-ivory-3">{{trainee:"Стажер",junior:"Молодший барбер",barber:"Барбер",senior:"Старший барбер"}[s.professionalLevel ?? "barber"]}</span>' + s[rank_at:]
s = s.replace('top: (m - openMin) * PX_PER_MIN', 'top: (m - openMin) * PX_PER_MIN - (m === closeMin ? 3 : 0)', 1)
p.write_text(s, encoding='utf-8')

# Calendar settings action and date-specific staff-schedule action.
p = root / 'src/lib/data/settings-actions.ts'
s = p.read_text(encoding='utf-8')
insert = '''
export async function saveStaffDateSchedule(staffId: string, day: string, works: boolean, shifts: {start:string;end:string}[]): Promise<Result> {
  await assertPanelSession()
  if (!DAY.test(day) || !(await db()).staff.some((m)=>m.id===staffId)) return {ok:false,error:"Revisá la persona y la fecha."}
  const settings=(await db()).shopSettings
  const open=hmToMinutes(settings.calendarOpen), close=hmToMinutes(settings.calendarClose)
  const clean=works?shifts.map((x)=>({start:String(x.start),end:String(x.end)})):[]
  if (clean.length>3 || clean.some((x)=>!HHMM.test(x.start)||!HHMM.test(x.end)||hmToMinutes(x.start)<open||hmToMinutes(x.end)>close||hmToMinutes(x.end)<=hmToMinutes(x.start))) return {ok:false,error:`Elegí hasta tres franjas dentro del horario del local (${settings.calendarOpen}–${settings.calendarClose}).`}
  clean.sort((a,b)=>a.start.localeCompare(b.start))
  for(let i=1;i<clean.length;i++)if(hmToMinutes(clean[i].start)<hmToMinutes(clean[i-1].end))return {ok:false,error:"Las franjas de una misma fecha no pueden pisarse."}
  await store().setStaffDateSchedule(staffId,day,works,clean)
  refresh()
  return {ok:true}
}

export async function saveCalendarSettings(input:{open:string;close:string;step:number;allowOverlaps:boolean}):Promise<Result>{
  await assertPanelSession()
  if(!HHMM.test(input.open)||!HHMM.test(input.close)||hmToMinutes(input.close)<=hmToMinutes(input.open))return {ok:false,error:"Revisá el horario del local."}
  if(![15,30].includes(Number(input.step)))return {ok:false,error:"El paso de la cuadrícula debe ser de 15 o 30 minutos."}
  await store().updateShopSettings({calendarOpen:input.open,calendarClose:input.close,calendarStepMin:input.step,allowStaffOverlaps:!!input.allowOverlaps})
  refresh()
  return {ok:true}
}
'''.replace('+','')
if 'export async function saveDepositSettings' not in s: raise RuntimeError('Settings action insertion point missing')
s = s.replace('export async function saveDepositSettings', insert+'\nexport async function saveDepositSettings', 1)
p.write_text(s, encoding='utf-8')

# Staff-only overlapping appointments; public booking continues to use freeSlots.
p = root / 'src/lib/data/actions.ts'
s = p.read_text(encoding='utf-8')
s = s.replace('''    const check = checkManualBooking({ day: input.day, time: input.time, durationMin: duration, service, staff, appointments: s.appointments, now: await now() })''', '''    const check = checkManualBooking({ day: input.day, time: input.time, durationMin: duration, service, staff, appointments: s.appointments, now: await now(), allowOverlap: s.shopSettings.allowStaffOverlaps })''', 1)
s = s.replace('''      newClient: input.clientId
        ? undefined
        : { name: name!, phone: input.newClient?.phone?.trim() || null, channel: "whatsapp", notes: null, preferredStaffId: staff.id },'''.replace('+',''), '''      allowOverlap: !!grid.manual && s.shopSettings.allowStaffOverlaps,
      newClient: input.clientId
        ? undefined
        : { name: name!, phone: input.newClient?.phone?.trim() || null, channel: "whatsapp", notes: null, preferredStaffId: staff.id },'''.replace('+',''), 1)
p.write_text(s, encoding='utf-8')

# Calendar configuration screen.
component = '''"use client"
import { useState, useTransition } from "react"
import { toast } from "sonner"
import { saveCalendarSettings } from "@/lib/data/settings-actions"
import type { ShopSettings } from "@/lib/domain/types"

export function CalendarSettings({settings}:{settings:ShopSettings}) {
 const [open,setOpen]=useState(settings.calendarOpen),[close,setClose]=useState(settings.calendarClose),[step,setStep]=useState(settings.calendarStepMin),[overlaps,setOverlaps]=useState(settings.allowStaffOverlaps),[pending,start]=useTransition()
 return <div className="space-y-5 rounded-xl border border-line bg-surface-1 p-4">
  <div className="grid grid-cols-2 gap-3"><label className="text-sm">El local abre<input type="time" value={open} onChange={e=>setOpen(e.target.value)} className="mt-1 h-11 w-full rounded-lg border border-line bg-surface-2 px-3"/></label><label className="text-sm">El local cierra<input type="time" value={close} onChange={e=>setClose(e.target.value)} className="mt-1 h-11 w-full rounded-lg border border-line bg-surface-2 px-3"/></label></div>
  <label className="block text-sm">Paso de la cuadrícula del calendario<select value={step} onChange={e=>setStep(Number(e.target.value))} className="mt-1 h-11 w-full rounded-lg border border-line bg-surface-2 px-3"><option value={15}>Cada 15 minutos</option><option value={30}>Cada 30 minutos</option></select></label>
  <label className="flex items-start gap-3 rounded-lg border border-line p-3"><input type="checkbox" checked={overlaps} onChange={e=>setOverlaps(e.target.checked)} className="mt-1 size-4"/><span><b className="block text-sm">Permitir turnos superpuestos para el equipo</b><span className="text-xs text-ivory-3">Sólo el personal del panel puede usarlos. La reserva pública sigue bloqueando las horas ya ocupadas.</span></span></label>
  <button disabled={pending} onClick={()=>start(async()=>{const r=await saveCalendarSettings({open,close,step,allowOverlaps:overlaps});r.ok?toast.success("Configuración del calendario guardada"):toast.error(r.error)})} className="h-11 w-full rounded-lg bg-ivory font-semibold text-obsidian">{pending?"Guardando…":"Guardar configuración"}</button>
 </div>
}
'''
(root/'src/components/settings/calendar-settings.tsx').write_text(component,encoding='utf-8')

# Date-by-date schedule planner for each staff member.
component = '''"use client"
import { useState,useTransition } from "react"
import { ChevronLeft,ChevronRight } from "lucide-react"
import { toast } from "sonner"
import { saveStaffDateSchedule } from "@/lib/data/settings-actions"
import type { Staff } from "@/lib/domain/types"

const names=["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"]
const key=(d:Date)=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`
export function StaffSchedulePlanner({staff,today}:{staff:Staff[];today:string}) {
 const [month,setMonth]=useState(()=>new Date(today+"T12:00:00")),[member,setMember]=useState(staff[0]?.id||""),[day,setDay]=useState(today),[works,setWorks]=useState(true),[start,setStart]=useState(staff[0]?.calendarOpen||"11:00"),[end,setEnd]=useState(staff[0]?.calendarClose||"20:00"),[pending,run]=useTransition()
 const current=staff.find(x=>x.id===member)
 const monthName=new Intl.DateTimeFormat("uk-UA",{month:"long",year:"numeric"}).format(month)
 const first=new Date(month.getFullYear(),month.getMonth(),1), offset=(first.getDay()+6)%7, days=new Date(month.getFullYear(),month.getMonth()+1,0).getDate()
 const pick=(date:string)=>{setDay(date);const item=current?.dateSchedule?.find(x=>x.day===date);setWorks(item?.works??true);setStart(item?.shifts[0]?.start??current?.calendarOpen??"10:00");setEnd(item?.shifts[0]?.end??current?.calendarClose??"20:00")}
 return <div className="space-y-4 rounded-xl border border-line bg-surface-1 p-4">
  <label className="block text-sm">Працівник<select value={member} onChange={e=>{setMember(e.target.value);setDay("")}} className="mt-1 h-11 w-full rounded-lg border border-line bg-surface-2 px-3">{staff.filter(s=>s.active).map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
  <div className="flex items-center justify-between"><button aria-label="Попередній місяць" onClick={()=>setMonth(new Date(month.getFullYear(),month.getMonth()-1,1))} className="grid size-10 place-items-center rounded-lg border border-line"><ChevronLeft/></button><b className="capitalize">{monthName}</b><button aria-label="Наступний місяць" onClick={()=>setMonth(new Date(month.getFullYear(),month.getMonth()+1,1))} className="grid size-10 place-items-center rounded-lg border border-line"><ChevronRight/></button></div>
  <div className="grid grid-cols-7 gap-1 text-center">{["Пн","Вт","Ср","Чт","Пт","Сб","Нд"].map(n=><span key={n} className="py-1 text-xs text-ivory-3">{n}</span>)}{Array.from({length:offset},(_,i)=><span key={"x"+i}/>)}{Array.from({length:days},(_,i)=>{const date=key(new Date(month.getFullYear(),month.getMonth(),i+1));const savedDay=current?.dateSchedule?.find(x=>x.day===date);return <button key={date} onClick={()=>pick(date)} aria-pressed={day===date} className={`min-h-10 rounded-lg border text-sm ${day===date?"border-ivory bg-surface-3":"border-line"} ${savedDay?"font-bold text-sky-300":""}`}>{i+1}</button>})}</div>
  {day&&<div className="space-y-3 rounded-lg border border-line p-3"><p className="font-semibold">{new Intl.DateTimeFormat("uk-UA",{dateStyle:"full"}).format(new Date(day+"T12:00:00"))}</p><label className="flex items-center gap-2"><input type="checkbox" checked={works} onChange={e=>setWorks(e.target.checked)}/>Працює цього дня</label>{works&&<div className="grid grid-cols-2 gap-3"><label className="text-sm">Початок<input type="time" value={start} onChange={e=>setStart(e.target.value)} className="mt-1 h-11 w-full rounded-lg border border-line bg-surface-2 px-3"/></label><label className="text-sm">Кінець<input type="time" value={end} onChange={e=>setEnd(e.target.value)} className="mt-1 h-11 w-full rounded-lg border border-line bg-surface-2 px-3"/></label></div>}<button disabled={pending} onClick={()=>run(async()=>{const r=await saveStaffDateSchedule(member,day,works,works?[{start,end}]:[]);r.ok?toast.success("Графік на дату збережено"):toast.error(r.error)})} className="h-11 w-full rounded-lg bg-ivory font-semibold text-obsidian">{pending?"Зберігаємо…":"Зберегти графік на дату"}</button></div>}
 </div>
}
'''
(root/'src/components/settings/staff-schedule-planner.tsx').write_text(component,encoding='utf-8')

# Keep the in-memory/demo snapshot aligned with persistent settings.
edit('src/lib/data/seed.ts', 'slotStepMin: 60, timezone: \"Europe/Berlin\" },', 'slotStepMin: 60, timezone: \"Europe/Berlin\", calendarOpen: \"11:00\", calendarClose: \"20:00\", calendarStepMin: 15, allowStaffOverlaps: false },', 1)

# Add separate calendar and staff schedule settings tabs.
p = root/'src/app/(panel)/ajustes/page.tsx'
s = p.read_text(encoding='utf-8')
if 'id: \"horarios\"' not in s:
    s, n = re.subn(r'(const TABS = \[.*?)(\] as const)', r'\1  { id: "horarios", label: "Графік працівників" },\n  { id: "calendario", label: "Календар" },\2', s, count=1, flags=re.S)
    if n != 1: raise RuntimeError('Settings tabs insertion point missing')
s = s.replace('] as const', ']', 1)
s = s.replace('import { ServicesEditor } from "@/components/settings/services-editor"', 'import { ServicesEditor } from "@/components/settings/services-editor"\nimport { CalendarSettings } from "@/components/settings/calendar-settings"\nimport { StaffSchedulePlanner } from "@/components/settings/staff-schedule-planner"',1)
s = s.replace('{tab === "fijos" && <FixedSlotsEditor', '{tab === "horarios" && <StaffSchedulePlanner staff={s.staff} today={dayKey(await now())} />}\n\n        {tab === "calendario" && <div className="space-y-5"><Panel title="Години роботи та сітка календаря"><CalendarSettings settings={s.shopSettings} /></Panel></div>}\n\n        {tab === "fijos" && <FixedSlotsEditor',1)
p.write_text(s,encoding='utf-8')

# Pass calendar settings to the agenda, use configured hours and interval for
# grid size, line spacing, and tap-to-create rounding.
p = root/'src/lib/data/queries.ts'
s = p.read_text(encoding='utf-8')
start=s.index('export async function getAgenda(day: string)')
tail=s[start:]
tail=tail.replace('''    staff: s.staff,
    services: s.services,''', '''    staff: s.staff,
    shopSettings: s.shopSettings,
    services: s.services,''', 1)
tail=tail.replace('s.staff.some(m=>m.active && m.schedule?.some(shift=>shift.weekday===weekday(day)))', 's.staff.some(m=>m.active && (m.dateSchedule?.some(x=>x.day===day&&x.works) || m.schedule?.some(shift=>shift.weekday===weekday(day))))', 1)
tail=tail.replace('s.staff.some(m=>m.active&&m.schedule?.some(shift=>shift.weekday===weekday(d)))', 's.staff.some(m=>m.active&&(m.dateSchedule?.some(x=>x.day===d&&x.works)||m.schedule?.some(shift=>shift.weekday===weekday(d))))', 1)
s=s[:start]+tail
p.write_text(s,encoding='utf-8')
p = root/'src/app/(panel)/agenda/page.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('''<DayGrid day={d.day} isToday={isToday} now={d.now} staff={d.staff} staffPhotoIds={staffPhotoIds}''', '''<DayGrid day={d.day} isToday={isToday} now={d.now} staff={d.staff} shopSettings={d.shopSettings} staffPhotoIds={staffPhotoIds}''', 1)
p.write_text(s,encoding='utf-8')
p = root/'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('  staffPhotoIds=[],\n  services,', '  staffPhotoIds=[],\n  shopSettings,\n  services,',1)
s = s.replace('  staffPhotoIds?: string[]\n  services:', '  staffPhotoIds?: string[]\n  shopSettings: import("@/lib/domain/types").ShopSettings\n  services:',1)
s = s.replace('''  const lower=Math.min(hmToMinutes(BRAND.openingHours.open),...shiftBounds,...appointmentBounds)
  const upper=Math.max(hmToMinutes(BRAND.openingHours.close),...shiftBounds,...appointmentBounds)'''.replace('+',''), '''  const lower=Math.min(hmToMinutes(shopSettings.calendarOpen),...shiftBounds,...appointmentBounds)
  const upper=Math.max(hmToMinutes(shopSettings.calendarClose),...shiftBounds,...appointmentBounds)'''.replace('+',''),1)
s = s.replace('Math.floor((e.clientY - rect.top) / PX_PER_MIN / gridStep) * gridStep', 'Math.floor((e.clientY - rect.top) / PX_PER_MIN / shopSettings.calendarStepMin) * shopSettings.calendarStepMin',1)
s = s.replace('const gridStep = 15\n    ', '',1)
s = s.replace('{hours.slice(0, -1).map((m) => (', '{Array.from({length:Math.ceil((closeMin-openMin)/shopSettings.calendarStepMin)},(_,i)=>openMin+(i+1)*shopSettings.calendarStepMin).filter(m=>m<closeMin).map((m) => (',1)
s = s.replace('top: (m + 30 - openMin) * PX_PER_MIN', 'top: (m - openMin) * PX_PER_MIN',1)
s = s.replace('top: (m - openMin) * PX_PER_MIN', 'top: (m - openMin) * PX_PER_MIN + 8',1)
p.write_text(s,encoding='utf-8')

# Migration adds specific-date schedules, shop operating hours, calendar step,
# and opt-in staff overlaps. Replace the global exclusion with guarded writes.
sql = '''ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS calendar_open text NOT NULL DEFAULT '11:00';
ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS calendar_close text NOT NULL DEFAULT '20:00';
ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS calendar_step_min smallint NOT NULL DEFAULT 15 CHECK (calendar_step_min IN (15,30));
ALTER TABLE shop_settings ADD COLUMN IF NOT EXISTS allow_staff_overlaps boolean NOT NULL DEFAULT false;
CREATE TABLE IF NOT EXISTS staff_schedule_overrides (
  staff_id uuid NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
  business_day date NOT NULL,
  works boolean NOT NULL DEFAULT true,
  shifts jsonb NOT NULL DEFAULT '[]'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (staff_id,business_day)
);
ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_no_overlap;
CREATE INDEX IF NOT EXISTS staff_schedule_overrides_day_idx ON staff_schedule_overrides(business_day);
'''
(Path('/tmp/booking-patch/0016_calendar_schedules.sql')).write_text(sql,encoding='utf-8')
p = Path('/tmp/booking-patch/migrate-booking.mjs')
s = p.read_text(encoding='utf-8')
s = s.replace('\"0013_staff_avatars.sql\",\"0014_booking_checkins.sql\"', '\"0013_staff_avatars.sql\",\"0014_booking_checkins.sql\",\"0015_timezone.sql\",\"0016_calendar_schedules.sql\"', 1)
p.write_text(s,encoding='utf-8')

# Enforce collision rules under a per-staff/day transaction lock. Only manual
# panel bookings can opt out of collision blocking; web and agent stay strict.
p = root/'src/lib/data/store/memory.ts'
s = p.read_text(encoding='utf-8')
s = s.replace('async createAppointment({ appointment, newClient, linkConversationId, allowOverlap = false }) {', 'async createAppointment({ appointment, newClient, linkConversationId, allowOverlap = false }) {',1)
p.write_text(s,encoding='utf-8')

# Copy/apply migration and this source transformation as the final build patch.
css_path = root / 'src/app/globals.css'
css = css_path.read_text(encoding='utf-8')
css += '''
@media(max-width:767px){
 [data-booking-workspace="calendar"] .panel{overflow-x:clip!important;overflow-y:visible!important;}
 [data-booking-workspace="calendar"] [data-calendar-scroll]{overflow-x:clip!important;overflow-y:visible!important;}
 [data-booking-workspace="calendar"] [data-staff-header]{position:sticky;top:calc(env(safe-area-inset-top) + 48px);z-index:40;background-color:#151515;backdrop-filter:blur(10px);}
 [data-booking-workspace="calendar"] [data-calendar-grid]{padding-bottom:2px;}
 [data-booking-workspace="calendar"] [data-time-rail]{z-index:20;}
}
'''
css_path.write_text(css, encoding='utf-8')
print('CALENDAR_RIGHT_DRAWER_SCHEDULES_SETTINGS_INSTALLED')


# Calendar readability pass from the latest mobile screenshots.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = re.sub(r'const PX_PER_MIN = [0-9.]+', 'const PX_PER_MIN = 1.35', s, count=1)
s = s.replace('gridTemplateColumns: "44px repeat(', 'gridTemplateColumns: "40px repeat(')
# Keep the closing-hour label just inside the rounded lower edge and add half-hour labels.
rail_start = s.index('data-time-rail')
rail_end = s.index('</div>', s.index('{hours.map', rail_start))
rail = s[rail_start:rail_end]
rail, n = re.subn(r'style=\{\{\s*top:\s*\(m - openMin\) \* PX_PER_MIN[^}]*\}\}', 'style={{ top: (m - openMin) * PX_PER_MIN + (m === closeMin ? -9 : 8) }}', rail, count=1)
if n != 1: raise RuntimeError('Could not align the calendar hour labels')
if 'half-' not in rail:
    rail += '''
                {Array.from({length:Math.ceil((closeMin-openMin)/60)},(_,i)=>openMin+i*60+30).filter(m=>m<closeMin).map((m)=>(
                  <span key={`half-${m}`} aria-hidden className="num absolute right-2 -translate-y-1/2 text-[10px] text-ivory-3/80" style={{top:(m-openMin)*PX_PER_MIN}}>30</span>
                ))}
'''
s = s[:rail_start] + rail + s[rail_end:]
# Move the left arrow into the first barber-header cell and reserve the right edge too.
s = s.replace('className="absolute left-1 top-1/2 z-50 grid size-7', 'className="absolute left-[41px] top-1/2 z-50 grid size-7', 1)
old_staff_cell = '<div key={s.id} className="flex items-center gap-1.5 border-l border-line px-1.5 py-2">'
new_staff_cell = '<div key={s.id} style={{paddingLeft:mobileMode&&staffPage>0&&s.id===visibleStaff[0]?.id?38:undefined,paddingRight:mobileMode&&staffPage<workingStaff.length-3&&s.id===visibleStaff[visibleStaff.length-1]?.id?38:undefined}} className="flex min-w-0 items-center gap-1.5 border-l border-line px-1.5 py-2">'
if old_staff_cell not in s: raise RuntimeError('Could not reserve space in the barber header')
s = s.replace(old_staff_cell, new_staff_cell, 1)
# Slightly smaller photos leave room for names and controls.
s = s.replace('className="grid size-9 shrink-0 place-items-center overflow-hidden rounded-full', 'className="grid size-8 shrink-0 place-items-center overflow-hidden rounded-full', 1)
s = s.replace('width={36} height={36}', 'width={32} height={32}', 1)
# Match appointment time text to its status color for faster scanning.
s = s.replace('<span className="num block truncate text-[10px] font-semibold text-ivory-2">{hm(a.startsAt)}–{hm(a.endsAt)}</span>', '<span className={cn("num block truncate text-[10px] font-bold",a.status==="en_curso"&&"text-emerald-300",a.status==="completado"&&"text-amber-300",a.status==="pendiente"&&"text-sky-300",a.status==="confirmado"&&"text-sky-300",(a.status==="cancelado"||a.status==="no_show")&&"text-rose-300")}>{hm(a.startsAt)}–{hm(a.endsAt)}</span>',1)
p.write_text(s, encoding='utf-8')

css_path = root / 'src/app/globals.css'
css = css_path.read_text(encoding='utf-8')
css = css.replace('[data-booking-workspace="calendar"] [data-time-rail]{z-index:20;}', '[data-booking-workspace="calendar"] [data-time-rail]{z-index:20;width:40px;}')
css += '''
@media(max-width:767px){
 [data-booking-workspace="calendar"] [data-staff-header] > div:not(:first-child) {min-width:0;}
 [data-booking-workspace="calendar"] [data-time-rail] > span:first-child {font-weight:700;color:#e5e7eb;}
 [data-booking-workspace="calendar"] [data-calendar-grid]{padding-bottom:8px!important;}
}
'''
css_path.write_text(css, encoding='utf-8')

# Keep the date toolbar above time labels as the page scrolls.
p = root / 'src/app/(panel)/agenda/page.tsx'
s = p.read_text(encoding='utf-8')
s, n = re.subn(r'className="sticky top-0 z-20 -mx-2 border-b border-line bg-obsidian/95', 'className="sticky top-0 z-50 -mx-2 border-b border-line bg-obsidian', s, count=1)
if n != 1: raise RuntimeError('Could not raise the sticky date toolbar above the timeline')
p.write_text(s, encoding='utf-8')
print('CALENDAR_TIMELINE_LABELS_AND_HEADER_SPACING_UPDATED')


# Match the staff header to the supplied calendar references: names/roles only,
# compact portrait above the text, balanced side gutters, and one paging control
# in the currently available side gutter.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace(
    'gridTemplateColumns: "40px repeat("+visibleStaff.length+", minmax(0,1fr))"',
    'gridTemplateColumns: "40px repeat("+visibleStaff.length+", minmax(0,1fr)) 40px"',
)
# The header and grid share 40px side gutters, matching the hour rail.
if s.count('gridTemplateColumns: "40px repeat("+visibleStaff.length+", minmax(0,1fr)) 40px"') < 2:
    raise RuntimeError("Calendar side gutters were not added to both header and timeline")

# Drop appointment counts and earnings from each staff header.
header_start = s.index('data-staff-header')
header_end = s.index('{/* Grilla */}', header_start)
header = s[header_start:header_end]
header, removed = re.subn(r'\n\s*<span className="num block text-\[11\.5px\] text-ivory-3">[\s\S]*?</span>', '', header, count=1)
if removed != 1:
    # Some builds use a slightly different font size; remove the header-only
    # statistics span by its class and its appointment count expression.
    header, removed = re.subn(r'\n\s*<span className="[^"]*num[^"]*">(?:(?!</span>)[\s\S])*?(?:mine\.length|turnos|appointments)[\s\S]*?</span>', '', header, count=1)
if removed != 1:
    raise RuntimeError("Staff appointment-count markup was not found")
header = header.replace(
    'const mine = appointments.filter((a) => a.staffId === s.id && a.status !== "cancelado" && a.status !== "no_show")\n                ',
    '',
    1,
)
# Reference layout: small photo first, then name and role below.
header = header.replace(
    'className="flex min-w-0 items-center gap-1.5 border-l border-line px-1.5 py-2"',
    'className="flex min-w-0 min-h-[112px] flex-col items-start justify-center gap-1 border-l border-line px-2 py-2"',
    1,
)
# Remove the old per-cell padding that reserved arrow space inside barber columns.
header = re.sub(r' style=\{\{paddingLeft:mobileMode&&staffPage>0&&s\.id===visibleStaff\[0\]\?38:undefined,paddingRight:mobileMode&&staffPage<workingStaff\.length-3&&s\.id===visibleStaff\[visibleStaff\.length-1\]\?38:undefined\}\}', '', header, count=1)
# The hour rail and right edge are dedicated arrow gutters. Only the valid
# direction appears at any one time.
header = header.replace(
    'className="absolute left-[41px] top-1/2 z-50',
    'className="absolute left-1 top-1/2 z-50',
    1,
)
header = header.replace(
    'className="absolute right-1 top-1/2 z-50',
    'className="absolute right-1 top-1/2 z-50',
    1,
)
# A quiet darker panel at the far edge visually completes the right inset;
# the arrow remains above it.
header = header.replace(
    '              {visibleStaff.map((s) => {',
    '              <div aria-hidden className="pointer-events-none absolute inset-y-0 right-0 z-30 w-10 border-l border-line bg-obsidian/95" />\n              {visibleStaff.map((s) => {',
    1,
)
s = s[:header_start] + header + s[header_end:]

# Keep a matching right gutter visible for the full calendar grid and stop the
# rightmost barber column before it.
grid_anchor = '              {visibleStaff.map((s) => (\n                <div\n                  key={s.id}\n                  onClick={(e) => clickEmpty(s.id, e)}'
if grid_anchor not in s:
    raise RuntimeError("Calendar barber grid columns were not found")
s = s.replace(
    grid_anchor,
    '              <div aria-hidden className="pointer-events-none absolute inset-y-0 right-0 z-10 w-10 border-l border-line bg-obsidian/95" />\n' + grid_anchor,
    1,
)
# Keep the smaller portrait size and align its text to the same left edge.
s = s.replace('className="grid size-9 shrink-0 place-items-center overflow-hidden rounded-full', 'className="grid size-8 shrink-0 place-items-center overflow-hidden rounded-md', 1)
s = s.replace('width={36} height={36}', 'width={32} height={32}', 1)
p.write_text(s, encoding='utf-8')

# A compact, raised sticky staff strip stays visible as the timeline scrolls.
css_path = root / 'src/app/globals.css'
css = css_path.read_text(encoding='utf-8')
css += '''
@media(max-width:767px){
 [data-booking-workspace="calendar"] [data-staff-header]{
   position:sticky!important;
   top:calc(env(safe-area-inset-top) + 48px)!important;
   z-index:45!important;
   background:#151515!important;
   box-shadow:0 4px 10px rgb(0 0 0/.24);
 }
 [data-booking-workspace="calendar"] [data-staff-header] > div:not(:first-child){
   min-height:112px;
   padding:8px 8px;
   align-items:flex-start;
   justify-content:center;
 }
 [data-booking-workspace="calendar"] [data-staff-header] .num{display:none!important;}
}
'''
css_path.write_text(css, encoding='utf-8')
print('CALENDAR_STAFF_HEADER_MATCHES_REFERENCE_LAYOUT')


# Keep the previous-page arrow inside the sticky left header gutter so it
# stays attached to the pinned barber strip instead of scrolling as an overlay.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s, n = re.subn(
    r'\s*\{mobileMode && workingStaff\.length>3 && staffPage>0 && <button type="button" aria-label="Попередні барбери".*?</button>\}',
    '',
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError("Previous-staff arrow overlay was not found")
old_gutter = '<div className="sticky left-0 z-30 bg-obsidian" />'
new_gutter = '''<div data-staff-prev-gutter style={{top:"calc(env(safe-area-inset-top) + 48px)"}} className="sticky left-0 z-[60] flex items-center justify-center bg-obsidian">
                {mobileMode && workingStaff.length>3 && staffPage>0 && <button type="button" aria-label="Попередні барбери" onClick={()=>setStaffPage((page)=>Math.max(0,page-1))} className="grid size-7 place-items-center rounded-full border border-line-strong bg-surface-2 shadow"><ChevronLeft className="size-4"/></button>}
              </div>'''
if old_gutter not in s:
    raise RuntimeError("Sticky left header gutter was not found")
s = s.replace(old_gutter, new_gutter, 1)
p.write_text(s, encoding='utf-8')

css_path = root / 'src/app/globals.css'
css = css_path.read_text(encoding='utf-8')
css += '''
@media(max-width:767px){
 [data-booking-workspace="calendar"] [data-staff-prev-gutter]{
   position:sticky!important;
   top:calc(env(safe-area-inset-top) + 48px)!important;
   left:0!important;
   z-index:60!important;
   align-self:stretch;
 }
 [data-booking-workspace="calendar"] [data-staff-header]{isolation:isolate;}
}
'''
css_path.write_text(css, encoding='utf-8')
print('CALENDAR_PREVIOUS_BARBER_ARROW_PINNED_TO_STICKY_HEADER')


# Final mobile barber-header polish: balanced compact gutters, one header surface,
# aligned two-line names/roles, small portraits, and slim full-height arrows.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')

old_track = 'gridTemplateColumns: "40px repeat("+visibleStaff.length+", minmax(0,1fr)) 40px"'
if s.count(old_track) < 2:
    raise RuntimeError("Expected both calendar header and timeline side gutters")
s = s.replace(old_track, 'gridTemplateColumns: "40px repeat("+visibleStaff.length+", minmax(0,1fr)) 32px"')

# Apply the same dark surface to every header cell, including the arrow gutters.
s = s.replace('className="relative grid border-b border-line bg-surface-1 shadow-sm"', 'className="relative grid border-b border-line bg-[#151515] shadow-sm"', 1)
s = s.replace('className="sticky left-0 z-[60] flex items-center justify-center bg-obsidian"', 'className="sticky left-0 z-[60] flex items-center justify-center bg-[#151515]"', 1)
s = s.replace('className="flex min-w-0 min-h-[112px] flex-col items-start justify-center gap-1 border-l border-line px-2 py-2"', 'className="flex min-w-0 min-h-[112px] flex-col items-start justify-center gap-1 border-l border-line bg-[#151515] px-2 py-2"', 1)

# Make each portrait/name/role stack use the same compact dimensions and baseline.
s = s.replace('grid size-8 shrink-0 place-items-center overflow-hidden rounded-md', 'grid size-7 shrink-0 place-items-center overflow-hidden rounded-md', 1)
s = s.replace('width={32} height={32}', 'width={28} height={28}', 1)
s = s.replace('block truncate text-[14px] font-medium text-ivory', 'block h-[30px] w-full overflow-hidden break-words text-[13px] leading-[15px] font-medium text-ivory', 1)
s = s.replace('block truncate text-[10px] font-medium text-ivory-3', 'block h-[14px] w-full truncate text-[11px] leading-[14px] font-medium text-ivory-3', 1)

# Previous/next controls are narrow arrow-only strips, visible only when movement exists.
s = s.replace('className="grid size-7 place-items-center rounded-full border border-line-strong bg-surface-2 shadow"', 'className="flex h-full w-full items-center justify-center bg-[#151515] text-ivory-2"', 1)
s = s.replace('<ChevronLeft className="size-4"/>', '<ChevronLeft className="size-5"/>', 1)
s = s.replace('className="absolute right-1 top-1/2 z-50 grid size-7 -translate-y-1/2 place-items-center rounded-full border border-line-strong bg-surface-2 shadow"', 'className="absolute inset-y-0 right-0 z-50 flex w-8 items-center justify-center bg-[#151515] text-ivory-2"', 1)
s = s.replace('<ChevronRight className="size-4"/>', '<ChevronRight className="size-5"/>', 1)

# Both right-hand spacers match the new 32px grid track and header background.
s = s.replace('z-30 w-10 border-l border-line bg-obsidian/95', 'z-30 w-8 border-l border-line bg-[#151515]', 1)
s = s.replace('z-10 w-10 border-l border-line bg-obsidian/95', 'z-10 w-8 border-l border-line bg-obsidian/95', 1)

p.write_text(s, encoding='utf-8')

css_path = root / 'src/app/globals.css'
css = css_path.read_text(encoding='utf-8')
css += '''
@media(max-width:767px){
 [data-booking-workspace="calendar"] [data-staff-header]{
   background:#151515!important;
 }
 [data-booking-workspace="calendar"] [data-staff-header] > [data-staff-prev-gutter],
 [data-booking-workspace="calendar"] [data-staff-header] > div[aria-hidden]{
   background:#151515!important;
 }
 [data-booking-workspace="calendar"] [data-staff-header] > div[aria-hidden]{
   width:32px!important;
 }
 [data-booking-workspace="calendar"] [data-staff-header] > div:not(:first-child){
   background:#151515!important;
 }
}
'''
css_path.write_text(css, encoding='utf-8')
print('CALENDAR_BARBER_HEADER_COMPACT_AND_ALIGNED')


# Pin the hour rail to the left and keep its labels below the date toolbar;
# make the calendar utility drawer consistently enter from the right.
p = root / 'src/components/shell/booking-workspace-shell.tsx'
s = p.read_text(encoding='utf-8')
s, n = re.subn(
    r'(<aside className=\{"fixed inset-y-0 )left-0(.*?\+\(open\?"visible translate-x-0":"invisible )-translate-x-full',
    r'\1right-0\2translate-x-full',
    s,
    count=1,
    flags=re.S,
)
# It may already be right-aligned from the earlier device pass; in either case,
# keep the drawer on the right and close it with a rightward swipe.
if n == 0 and 'fixed inset-y-0 right-0' not in s:
    raise RuntimeError("Calendar drawer could not be anchored to the right")
s = s.replace('border-r border-line bg-obsidian p-4', 'border-l border-line bg-obsidian p-4', 1)
if 'onTouchEnd={(event)=>' not in s:
    needle = 'aria-label="Calendar menu" aria-hidden={!open} inert={!open}>'
    if needle not in s:
        raise RuntimeError("Calendar drawer touch handler insertion point missing")
    s = s.replace(needle, '''aria-label="Calendar menu" aria-hidden={!open} inert={!open}
       onTouchStart={(event)=>{const t=event.touches[0];menuTouch.current={x:t.clientX,y:t.clientY}}}
       onTouchEnd={(event)=>{const start=menuTouch.current;menuTouch.current=null;if(!start)return;const t=event.changedTouches[0];const dx=t.clientX-start.x;const dy=t.clientY-start.y;if(dx>56&&Math.abs(dx)>Math.abs(dy))setOpen(false)}}>''',1)
if 'menuTouch=useRef' not in s:
    s = s.replace(' const [open,setOpen]=useState(false)', ' const [open,setOpen]=useState(false)\n const menuTouch=useRef<{x:number;y:number}|null>(null)',1)
    s = s.replace('import { useState } from "react"', 'import { useRef, useState } from "react"',1)
p.write_text(s, encoding='utf-8')

css_path = root / 'src/app/globals.css'
css = css_path.read_text(encoding='utf-8')
css += '''
@media(max-width:767px){
 [data-booking-workspace="calendar"] [data-time-rail]{
   position:sticky!important;
   left:0!important;
   z-index:8!important;
   background:#090909!important;
 }
 [data-booking-workspace="calendar"] [data-staff-header]{
   z-index:45!important;
   background:#151515!important;
 }
 [data-booking-workspace="calendar"] [data-calendar-toolbar]{
   position:sticky!important;
   top:0!important;
   z-index:80!important;
   background:#090909!important;
 }
}
'''
css_path.write_text(css, encoding='utf-8')

# Mark the date row explicitly so the time gutter cannot float over its content.
p = root / 'src/app/(panel)/agenda/page.tsx'
s = p.read_text(encoding='utf-8')
if 'data-calendar-toolbar' not in s:
    s, n = re.subn(r'(<div className="sticky top-0 z-50 -mx-2 border-b border-line bg-obsidian[^"]*")', r'\1 data-calendar-toolbar', s, count=1)
    if n != 1:
        raise RuntimeError("Calendar sticky date toolbar not found")
    p.write_text(s, encoding='utf-8')
print('CALENDAR_TIME_RAIL_LEFT_AND_RIGHT_DRAWER_ENFORCED')


# Current-time marker: keep one live line aligned with the sticky hour rail.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
if 'const [currentClock,setCurrentClock]' not in s:
    anchor = '  const [mobileMode,setMobileMode] = useState(false)'
    if anchor not in s:
        raise RuntimeError("Calendar mobile mode state not found for live clock")
    s = s.replace(anchor, anchor + '''
  const [currentClock,setCurrentClock] = useState(()=>new Date())
  useEffect(()=>{const tick=()=>setCurrentClock(new Date());tick();const timer=window.setInterval(tick,15000);return()=>window.clearInterval(timer)},[])
''', 1)

# Use one clock source for both the badge and rule, and anchor the badge to the
# actual hour rail instead of estimating the barber-header height.
s = s.replace('const nowMin = minutesOfDay(now)', 'const nowMin = currentClock.getHours()*60+currentClock.getMinutes()', 1)
rail_anchor = 'data-time-rail className="sticky left-0 z-20 bg-obsidian">'
if rail_anchor not in s:
    raise RuntimeError("Calendar time rail not found")
rail_anchor = 'data-time-rail className="sticky left-0 z-20 bg-obsidian relative">'
s = s.replace('data-time-rail className="sticky left-0 z-20 bg-obsidian">', rail_anchor, 1)

# The existing timeline marker is the only line. Keep it one pixel, aligned
# to the first barber column, and remove its old decorative dot.
s = s.replace(
    'className="pointer-events-none absolute right-0 left-[50px] z-20 flex items-center"',
    'className="pointer-events-none absolute left-[40px] right-[32px] z-30"',
    1,
)
s = s.replace(
    '<span className="size-[7px] rounded-full bg-gold shadow-[0_0_10px_2px_rgb(214_179_106/0.5)]" />',
    '',
    1,
)
s = s.replace(
    '<span className="h-px flex-1 bg-gold" />',
    '<span className="block h-px w-full bg-white/65" />',
    1,
)

badge = '''
                {isToday && nowMin >= openMin && nowMin < closeMin && <span aria-hidden data-current-time-badge className="pointer-events-none absolute left-0 z-[100] box-border flex w-full max-w-full -translate-y-1/2 justify-center overflow-hidden rounded-sm border border-line-strong bg-[#202020] px-0.5 py-0.5 font-mono text-[10px] font-semibold leading-[14px] text-amber-300 shadow-md" style={{top:(nowMin-openMin)*PX_PER_MIN}}>{String(currentClock.getHours()).padStart(2,"0")}:{String(currentClock.getMinutes()).padStart(2,"0")}</span>}
'''
s = s.replace(rail_anchor, rail_anchor + badge, 1)
p.write_text(s, encoding='utf-8')

# Render the drawer through a body portal. This escapes the calendar page's
# overflow/stacking contexts so the overlay covers even the date and app bars.
p = root / 'src/components/shell/booking-workspace-shell.tsx'
s = p.read_text(encoding='utf-8')
if 'from "react-dom"' not in s:
    s=s.replace('import { useRef, useState } from "react"', 'import { useEffect, useRef, useState } from "react"\nimport { createPortal } from "react-dom"', 1)
if 'const [portalReady,setPortalReady]' not in s:
    s=s.replace(' const {open:openBooking}=useNewAppointment()', ' const [portalReady,setPortalReady]=useState(false)\n useEffect(()=>setPortalReady(true),[])\n const {open:openBooking}=useNewAppointment()',1)

# Strip the old in-tree backdrop; the portal owns a full-viewport scrim.
s, scrim_removed = re.subn(r'\s*\{open&&<button type="button" aria-label="Close calendar menu" onClick=\{\(\)=>setOpen\(false\)\} className="fixed inset-0 z-\[90\] bg-black/60 transition-opacity duration-300"/>\}', '', s, count=1)
if scrim_removed > 1:
    raise RuntimeError("Multiple in-tree calendar scrims found")
aside_at=s.find('<aside className={')
aside_end=s.find('</aside>',aside_at)
if aside_at<0 or aside_end<0:
    raise RuntimeError("Calendar drawer element not found")
aside_end += len('</aside>')
aside=s[aside_at:aside_end]
aside=aside.replace('fixed inset-y-0 right-0 z-[100]', 'absolute inset-y-0 right-0 z-10',1)
aside, slide_count = re.subn(
    r'\(open\?"visible translate-x-0(?: pointer-events-auto)?":"invisible translate-x-full pointer-events-none"\)',
    '(open?"translate-x-0 pointer-events-auto":"translate-x-full pointer-events-none")',
    aside,
    count=1,
)
if slide_count != 1 or 'translate-x-full pointer-events-none' not in aside:
    raise RuntimeError("Calendar drawer right-slide state is missing")
aside=aside.replace('absolute inset-y-0 right-0 z-10', 'absolute inset-y-0 right-0 z-10 transition-transform duration-300 ease-out', 1)
portal='''{portalReady && createPortal(
       <div data-calendar-menu-layer className={"fixed inset-0 z-[9999] "+(open?"pointer-events-auto":"pointer-events-none")}>
         <button type="button" aria-label="Close calendar menu" onClick={()=>setOpen(false)} aria-hidden={!open} className={"absolute inset-0 z-0 bg-black/60 transition-opacity duration-300 "+(open?"opacity-100 pointer-events-auto":"opacity-0 pointer-events-none")}/>
         '''+aside+'''
       </div>,
       document.body
     )}'''
s=s[:aside_at]+portal+s[aside_end:]
p.write_text(s, encoding='utf-8')

css_path = root / 'src/app/globals.css'
css = css_path.read_text(encoding='utf-8')
css += '''
@media(max-width:767px){
 [data-booking-workspace="calendar"] [data-current-time-indicator]{
   display:block!important;
   z-index:55!important;
 }
 [data-booking-workspace="calendar"] [data-current-time-badge]{
   display:flex!important;
   z-index:100!important;
   box-sizing:border-box!important;
   width:100%!important;
   min-width:0!important;
   max-width:100%!important;
   padding-left:2px!important;
   padding-right:2px!important;
   font-size:10px!important;
   line-height:14px!important;
   overflow:hidden!important;
   white-space:nowrap!important;
 }
 [data-calendar-menu-layer]{
   position:fixed!important;
   inset:0!important;
   z-index:9999!important;
   isolation:isolate;
 }
 [data-calendar-menu-layer] aside[aria-label="Calendar menu"]{
   position:absolute!important;
   top:0!important;
   right:0!important;
   bottom:0!important;
   z-index:10!important;
   width:min(88vw,360px)!important;
   max-height:100dvh;
   padding-bottom:calc(12px + env(safe-area-inset-bottom));
   overflow-y:auto;
   background:#090909;
   box-shadow:-12px 0 40px rgb(0 0 0/.42);
 }
 [data-calendar-menu-layer] aside[aria-label="Calendar menu"] button,
 [data-calendar-menu-layer] aside[aria-label="Calendar menu"] a{touch-action:manipulation;}
}
'''
css_path.write_text(css, encoding='utf-8')
print('CALENDAR_LIVE_TIME_BADGE_IN_STICKY_RAIL_AND_BODY_PORTAL_DRAWER_INSTALLED')



# Dense, readable day grid: fit 09:00 of schedule on mobile, display
# appointment status/time in a compact colored header, and lane overlaps.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('const PX_PER_MIN = 1.25', 'const PX_PER_MIN = 1.0', 1)
if 'Clock3' not in s.split('from "lucide-react"')[0]:
    s = s.replace('{ Bot, Footprints, MessageCircle, Phone, Pin, Scissors, Sparkles, StickyNote }', '{ Bot, Check, Clock3, Footprints, MessageCircle, Phone, Pin, Scissors, Sparkles, StickyNote, X }', 1)
# Give every intersecting appointment its own lane, but let isolated cards
# use the full barber column.
layout_anchor = '  const paid = new Set(paidIds)\n'
layout_code = '''  const paid = new Set(paidIds)
  const appointmentLayout = new Map<string, { lane: number; count: number }>()
  for (const member of staff) {
    const items = appointments.filter((a) => a.staffId === member.id)
      .map((a) => ({ a, start: minutesOfDay(a.startsAt), end: minutesOfDay(a.endsAt) }))
      .sort((x, y) => x.start - y.start || x.end - y.end)
    let cluster: typeof items = []
    let clusterEnd = -1
    const placeCluster = () => {
      if (!cluster.length) return
      const laneEnds: number[] = []
      const assigned: { id: string; lane: number }[] = []
      for (const item of cluster) {
        let lane = laneEnds.findIndex((end) => end <= item.start)
        if (lane < 0) lane = laneEnds.length
        laneEnds[lane] = item.end
        assigned.push({ id: item.a.id, lane })
      }
      assigned.forEach(({ id, lane }) => appointmentLayout.set(id, { lane, count: laneEnds.length }))
      cluster = []
      clusterEnd = -1
    }
    for (const item of items) {
      if (cluster.length && item.start >= clusterEnd) placeCluster()
      cluster.push(item)
      clusterEnd = Math.max(clusterEnd, item.end)
    }
    placeCluster()
  }
'''
if 'const appointmentLayout = new Map' not in s:
    if layout_anchor not in s: raise RuntimeError('Appointment layout anchor missing')
    s = s.replace(layout_anchor, layout_code, 1)

s = s.replace('const short = (end - start) * PX_PER_MIN < 38', 'const short = (end - start) * PX_PER_MIN < 20', 1)
s = s.replace('''                      const short = (end - start) * PX_PER_MIN < 20
                      return (''', '''                      const short = (end - start) * PX_PER_MIN < 20
                      const layout = appointmentLayout.get(a.id) ?? { lane: 0, count: 1 }
                      const timeIcon = a.status === "completado"
                        ? <Check className="size-3 shrink-0" aria-label="Завершено" />
                        : (a.status === "cancelado" || a.status === "no_show")
                          ? <X className="size-3 shrink-0" aria-label="Скасовано" />
                          : <Clock3 className="size-3 shrink-0" aria-label={a.status === "en_curso" ? "Триває" : "Ще не розпочато"} />
                      return (''', 1)

s = s.replace('"absolute inset-x-0.5 overflow-hidden rounded-md border-l-[3px] px-2 text-left shadow-sm transition-[background-color,transform] hover:z-10 hover:-translate-y-px"',
              '"absolute overflow-hidden rounded-md border-l-[3px] text-left shadow-sm transition-[background-color,transform] hover:z-10 hover:-translate-y-px"', 1)
s = s.replace('short ? "flex items-center py-0" : "py-1.5"', '"flex flex-col p-0"', 1)
# A compact status band, with a clear start–end range and matching icon.
old = '''<span className="block min-w-0">
                            <span className={cn("num block truncate text-[10px] font-bold",a.status==="en_curso"&&"text-emerald-300",a.status==="completado"&&"text-amber-300",a.status==="pendiente"&&"text-sky-300",a.status==="confirmado"&&"text-sky-300",(a.status==="cancelado"||a.status==="no_show")&&"text-rose-300")}>{hm(a.startsAt)}–{hm(a.endsAt)}</span>
                            <span className="block truncate text-[12px] font-semibold leading-4 text-ivory">{client?.name||"Client"}</span>
                          </span>'''
new = '''<span className={cn("flex h-[16px] min-w-0 shrink-0 items-center justify-between gap-1 px-1.5 text-[10px] leading-none",
                            a.status === "en_curso" && "bg-emerald-600 text-white",
                            a.status === "completado" && "bg-amber-600 text-white",
                            a.status === "confirmado" && "bg-sky-600 text-white",
                            a.status === "pendiente" && "bg-sky-700 text-white",
                            (a.status === "cancelado" || a.status === "no_show") && "bg-rose-700 text-white"
                          )}>
                            <span className="num min-w-0 truncate font-bold">{hm(a.startsAt)}–{hm(a.endsAt)}</span>
                            {timeIcon}
                          </span>
                          {!short && <span className="min-h-0 min-w-0 flex-1 overflow-hidden px-1.5 py-0.5">
                            <span className="block truncate text-[11px] font-semibold leading-[13px] text-ivory">{client?.name || "Client"}</span>
                            {(end - start) * PX_PER_MIN >= 42 && <span className="block truncate text-[10px] leading-3 text-ivory-3">{service.name}</span>}
                            {reward && <Sparkles className="absolute bottom-1 right-1 size-3 text-gold" aria-label="Le toca el 50%" />}
                          </span>}'''
if old not in s:
    raise RuntimeError('Expected compact appointment content missing')
s = s.replace(old, new, 1)
s = s.replace('''style={{ top: (start - openMin) * PX_PER_MIN + 1, height: (end - start) * PX_PER_MIN - 2 }}''',
'''style={{
                            top: (start - openMin) * PX_PER_MIN + 1,
                            height: Math.max((end - start) * PX_PER_MIN - 2, 14),
                            left: `calc(${layout.lane * 100 / layout.count}% + 4px)`,
                            width: `calc(${100 / layout.count}% - 8px)`,
                          }}''',1)
# Soft amber glow only on the active booking crossed by the current-time line.
s = s.replace('''(a.status === "cancelado" || a.status === "no_show") && "border-l-rose-500 bg-rose-500/10 opacity-70 ring-1 ring-rose-500/20 ring-inset"
                          )}''',
'''(a.status === "cancelado" || a.status === "no_show") && "border-l-rose-500 bg-rose-500/10 opacity-70 ring-1 ring-rose-500/20 ring-inset",
                            isToday && start <= nowMin && end > nowMin && "z-[25] outline outline-1 outline-amber-300/70 shadow-[0_0_12px_2px_rgba(245,158,11,0.28)]"
                          )}''',1)

p.write_text(s, encoding='utf-8')
print('CALENDAR_SCALE_STATUS_BANDS_OVERLAP_LANES_ACTIVE_GLOW_INSTALLED')


# Make the new card layout resilient to upstream import and whitespace variants.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
def ensure_calendar_icons(match):
    names = [name.strip() for name in match.group(1).split(',') if name.strip()]
    for name in ('Check', 'Clock3', 'X'):
        if name not in names: names.append(name)
    return 'import { ' + ', '.join(names) + ' } from "lucide-react"'
s, import_count = re.subn(r'import\s*\{([^}]+)\}\s*from\s*"lucide-react"', ensure_calendar_icons, s, count=1)
if import_count != 1: raise RuntimeError('Lucide icon import not found for appointment status header')
if 'const layout = appointmentLayout.get(a.id)' not in s:
    marker = 'const timeIcon = a.status === "completado"'
    if marker not in s: raise RuntimeError('Appointment status icon insertion point missing')
    s = s.replace(marker, 'const layout = appointmentLayout.get(a.id) ?? { lane: 0, count: 1 }\n                      ' + marker, 1)
p.write_text(s, encoding='utf-8')
print('CALENDAR_CARD_LAYOUT_IMPORTS_FIXED')


# Avoid a stale intermediate JSX binding and read each appointment lane directly.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('left: `calc(${layout.lane * 100 / layout.count}% + 4px)`',
              'left: `calc(${((appointmentLayout.get(a.id)?.lane ?? 0) * 100) / (appointmentLayout.get(a.id)?.count ?? 1)}% + 4px)`')
s = s.replace('width: `calc(${100 / layout.count}% - 8px)`',
              'width: `calc(${100 / (appointmentLayout.get(a.id)?.count ?? 1)}% - 8px)`')
p.write_text(s, encoding='utf-8')
print('CALENDAR_OVERLAP_LANES_BOUND_PER_CARD')


# Give the per-card renderer an explicit binding for lane calculations.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
match = re.search(r'\.map\(\(a\) => \{\s*const start = minutesOfDay\(a\.startsAt\).*?\n\s{20}\}\)', s, flags=re.S)
if not match: raise RuntimeError('Appointment card map not found for explicit binding')
card = match.group(0).replace('.map((a) => {', '.map((appointment) => {', 1).replace('a.', 'appointment.')
s = s[:match.start()] + card + s[match.end():]
p.write_text(s, encoding='utf-8')
print('CALENDAR_APPOINTMENT_RENDERER_BINDING_EXPLICIT')


# Resolve the card layout using stable visible fields, avoiding JSX alias capture.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
key_block = '''  const appointmentLayoutByKey = new Map<string, { lane: number; count: number }>()
  for (const item of appointments) {
    const layout = appointmentLayout.get(item.id)
    if (layout) appointmentLayoutByKey.set(`${minutesOfDay(item.startsAt)}:${minutesOfDay(item.endsAt)}:${item.clientId}:${item.serviceId}`, layout)
  }
'''
if 'const appointmentLayoutByKey' not in s:
    anchor = '  const serviceOf = (id: string) => services.find((s) => s.id === id)!\n'
    if anchor not in s: raise RuntimeError('Calendar appointment helper insertion point missing')
    s = s.replace(anchor, key_block + anchor, 1)
layout_marker = 'const timeIcon = appointment.status === "completado"'
if 'const cardLayout = appointmentLayoutByKey.get' not in s:
    if layout_marker not in s: raise RuntimeError('Calendar appointment status icon not found')
    s = s.replace(layout_marker, 'const cardLayout = appointmentLayoutByKey.get(`${start}:${end}:${client?.id}:${service.id}`) ?? { lane: 0, count: 1 }\n                      ' + layout_marker, 1)
s = re.sub(r'left: `calc\(\$\{.*?\}% \+ 4px\)`', 'left: `calc(${cardLayout.lane * 100 / cardLayout.count}% + 4px)`', s, count=1)
s = re.sub(r'width: `calc\(\$\{.*?\}% - 8px\)`', 'width: `calc(${100 / cardLayout.count}% - 8px)`', s, count=1)
p.write_text(s, encoding='utf-8')
print('CALENDAR_CARD_LANES_RESOLVED_WITH_SCOPED_LAYOUT')


# Inline the composite lane lookup at the card position (no alias-dependent binding).
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
lane_expr = 'appointmentLayoutByKey.get(start + ":" + end + ":" + client?.id + ":" + service.id)'
s = s.replace('left: `calc(${cardLayout.lane * 100 / cardLayout.count}% + 4px)`',
              'left: `calc(${((' + lane_expr + '?.lane ?? 0) * 100) / (' + lane_expr + '?.count ?? 1)}% + 4px)`')
s = s.replace('width: `calc(${100 / cardLayout.count}% - 8px)`',
              'width: `calc(${100 / (' + lane_expr + '?.count ?? 1)}% - 8px)`')
p.write_text(s, encoding='utf-8')
print('CALENDAR_CARD_LANES_INLINE_LOOKUP')


# Key lanes by the start/end times available in the timeline cell renderer.
p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = s.replace('appointmentLayoutByKey.set(`${minutesOfDay(item.startsAt)}:${minutesOfDay(item.endsAt)}:${item.clientId}:${item.serviceId}`, layout)',
              'appointmentLayoutByKey.set(`${minutesOfDay(item.startsAt)}:${minutesOfDay(item.endsAt)}`, layout)')
s = s.replace('appointmentLayoutByKey.get(`${start}:${end}:${client?.id}:${service.id}`)', 'appointmentLayoutByKey.get(start + ":" + end)')
s = s.replace('appointmentLayoutByKey.get(start + ":" + end + ":" + client?.id + ":" + service.id)', 'appointmentLayoutByKey.get(start + ":" + end)')
p.write_text(s, encoding='utf-8')
print('CALENDAR_OVERLAP_LANES_KEYED_BY_INTERVAL')


p = root / 'src/components/agenda/day-grid.tsx'
s = p.read_text(encoding='utf-8')
s = re.sub(r'^\s*const cardLayout = appointmentLayoutByKey\.get\(.*?\) \?\? \{ lane: 0, count: 1 \}\n', '', s, count=1, flags=re.M)
p.write_text(s, encoding='utf-8')
print('CALENDAR_UNUSED_CARD_LAYOUT_BINDING_REMOVED')
