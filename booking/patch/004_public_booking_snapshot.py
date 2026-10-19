from pathlib import Path

root = Path("/app")

def edit(path: str, old: str, new: str, label: str) -> None:
    p = root / path
    body = p.read_text(encoding="utf-8")
    if old not in body:
        raise RuntimeError(f"{label}: source anchor missing in {path}")
    p.write_text(body.replace(old, new, 1), encoding="utf-8")

edit(
    "src/lib/data/store/types.ts",
    "export interface Store {",
    """export interface PublicBookingSnapshot {
  now: string
  staff: Staff[]
  services: Service[]
  appointments: Appointment[]
  shopSettings: ShopSettings
}

export interface Store {""",
    "public booking snapshot type",
)
edit(
    "src/lib/data/store/types.ts",
    "  agendaSnapshot?(day: string): Promise<AgendaSnapshot>\n",
    "  agendaSnapshot?(day: string): Promise<AgendaSnapshot>\n  publicBookingSnapshot?(fromDay: string, toDay: string): Promise<PublicBookingSnapshot>\n",
    "public booking store method",
)
edit(
    "src/lib/data/store/postgres.ts",
    "type AgendaSnapshot, type Snapshot, type Store",
    "type AgendaSnapshot, type PublicBookingSnapshot, type Snapshot, type Store",
    "public booking snapshot import",
)

method = '''  async publicBookingSnapshot(fromDay: string, toDay: string): Promise<PublicBookingSnapshot> {
    const sql = sqlClient()
    await sweepExpiredHolds(sql)
    const from = at(fromDay, "00:00")
    const to = at(addDays(toDay, 1), "00:00")
    const [staffRows, serviceRows, appointmentRows, shopRows, shifts, dateSchedules, timeOff, fixedRows, rankRows, rankRules] = await Promise.all([
      sql`select s.*, coalesce(array_agg(e.service_id) filter (where e.service_id is not null), '{}') as skips from staff s left join staff_service_exclusions e on e.staff_id=s.id where s.active=true group by s.id order by s.name`,
      sql`select * from services where active=true order by sort,name`,
      sql`select * from appointments where starts_at >= ${from} and starts_at < ${to} and status not in ('cancelado','no_show') order by starts_at`,
      sql`select * from shop_settings where id=1`,
      sql`select staff_id,weekday,to_char(start_time,'HH24:MI') as start,to_char(end_time,'HH24:MI') as "end" from staff_schedules order by weekday,start_time`,
      sql`select staff_id,to_char(business_day,'YYYY-MM-DD') as day,works,shifts from staff_schedule_overrides where business_day >= ${fromDay}::date and business_day <= ${toDay}::date`,
      sql`select id,staff_id,starts_at,ends_at,reason from staff_time_off where starts_at < ${to} and ends_at > ${from} order by starts_at`,
      sql`select id,staff_id,weekday,on_date::text as on_date,to_char(start_time,'HH24:MI') as start,to_char(end_time,'HH24:MI') as "end",label,active from fixed_slots where active=true`,
      sql`select staff_id,professional_level from booking_staff_levels`,
      sql`select service_id,professional_level,available from booking_service_levels`,
    ])
    const shop = shopRows[0]
    setTimeZone(String(shop?.timezone ?? "Europe/Berlin"))
    const levels = new Map(rankRows.map((r) => [String(r.staff_id), String(r.professional_level)]))
    const allowed = new Map<string, Set<string>>()
    for (const rule of rankRules) {
      const id = String(rule.service_id)
      if (!allowed.has(id)) allowed.set(id, new Set())
      if (rule.available) allowed.get(id)!.add(String(rule.professional_level))
    }
    const services = serviceRows.map(toService)
    const staffBase = staffRows.map((row) => {
      const level = levels.get(String(row.id)) || "barber"
      const restricted = services.filter((service) => { const ranks = allowed.get(service.id); return ranks && !ranks.has(level) }).map((service) => service.id)
      return { ...toStaff(row), professionalLevel: level as Staff["professionalLevel"], skipsServiceIds: [...((row.skips as string[] | null) ?? []), ...restricted], schedule: shifts.filter((x) => x.staff_id === row.id).map((x) => ({ weekday: Number(x.weekday), start: String(x.start), end: String(x.end) })), dateSchedule: dateSchedules.filter((x) => x.staff_id === row.id).map((x) => ({ day: String(x.day), works: Boolean(x.works), shifts: (x.shifts as {start:string;end:string}[]) ?? [] })), timeOff: timeOff.filter((x) => x.staff_id === row.id).map((x) => ({ startsAt: isoOr(x.starts_at as Date), endsAt: isoOr(x.ends_at as Date) })) }
    })
    const fixed = fixedRows.map((x) => ({ id: String(x.id), staffId: String(x.staff_id), weekday: x.weekday === null ? null : Number(x.weekday), onDate: (x.on_date as string | null) ?? null, start: String(x.start), end: String(x.end), label: (x.label as string | null) ?? null, active: Boolean(x.active) }))
    const days = Math.max(1, Math.ceil((Date.parse(toDay + "T00:00:00Z") - Date.parse(fromDay + "T00:00:00Z")) / 86400000) + 1)
    const fixedBlocks = expandFixedSlots(fixed, fromDay, days)
    const staff = staffBase.map((member) => ({ ...member, timeOff: [...(member.timeOff ?? []), ...fixedBlocks.filter((block) => block.staffId === member.id).map(({startsAt,endsAt}) => ({startsAt,endsAt}))] }))
    return {
      now: new Date().toISOString(), staff, services,
      appointments: appointmentRows.map(toAppointment),
      shopSettings: { openingCash: Number(shop?.opening_cash ?? 0), depositEnabled: Boolean(shop?.deposit_enabled), depositAmount: Number(shop?.deposit_amount ?? 0), depositHoldMin: Number(shop?.deposit_hold_min ?? 15), remindersEnabled: Boolean(shop?.reminders_enabled), slotStepMin: Number(shop?.slot_step_min ?? 60), timezone: String(shop?.timezone ?? "Europe/Berlin"), currency: String(shop?.currency_code ?? "ARS") as import("@/lib/domain/types").CurrencyCode, calendarOpen: String(shop?.calendar_open ?? "11:00"), calendarClose: String(shop?.calendar_close ?? "20:00"), calendarStepMin: Number(shop?.calendar_step_min ?? 15), allowStaffOverlaps: Boolean(shop?.allow_staff_overlaps) },
    }
  },

'''
edit("src/lib/data/store/postgres.ts", "  async agendaSnapshot(day: string): Promise<AgendaSnapshot> {", method + "  async agendaSnapshot(day: string): Promise<AgendaSnapshot> {", "narrow public booking query")

page = root / "src/app/reservar/page.tsx"
body = page.read_text(encoding="utf-8")
body = body.replace('import { db, now } from "@/lib/data/repo"', 'import { db, now, store } from "@/lib/data/repo"')
old = '''  const s = await db()
  const n = await now()
  const today = dayKey(n)
  const horizon = addDays(today, 15)'''
new = '''  const n = await now()
  const today = dayKey(n)
  const horizon = addDays(today, 15)
  const repository = store()
  const s = repository.publicBookingSnapshot
    ? await repository.publicBookingSnapshot(today, horizon)
    : await db()'''
if old not in body:
    raise RuntimeError("public booking page data loader anchor missing")
page.write_text(body.replace(old, new, 1), encoding="utf-8")

print("BOOKING_PUBLIC_BOOKING_USES_BOUNDED_SNAPSHOT")
