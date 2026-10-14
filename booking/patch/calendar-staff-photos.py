from pathlib import Path
root=Path("/app/src")
p=root/"app/(panel)/agenda/page.tsx"
s=p.read_text(encoding="utf-8")
anchor='import { DayGrid } from "@/components/agenda/day-grid"'
if anchor not in s: raise RuntimeError("Agenda import moved")
s=s.replace(anchor,anchor+'\nimport { sqlClient } from "@/lib/data/store/postgres"',1)
anchor='const d=await getAgenda(requested)'
if anchor not in s:raise RuntimeError("Agenda loader moved")
s=s.replace(anchor,anchor+'\n const staffPhotoIds=(await sqlClient()`select staff_id from booking_staff_avatars`).map(row=>String(row.staff_id))',1)
anchor='''staff={d.staff}
       services={d.services}'''
if anchor not in s:raise RuntimeError("DayGrid props moved")
s=s.replace(anchor,'''staff={d.staff} staffPhotoIds={staffPhotoIds}
       services={d.services}''',1)
p.write_text(s,encoding="utf-8")

p=root/"components/agenda/day-grid.tsx"
s=p.read_text(encoding="utf-8")
anchor='import Link from "next/link"'
if anchor not in s:raise RuntimeError("Calendar import moved")
s=s.replace(anchor,anchor+'\nimport Image from "next/image"',1)
anchor='''  staff,
  services,
  clients,
  appointments,'''
if anchor not in s:raise RuntimeError("DayGrid destructuring moved")
s=s.replace(anchor,'''  staff,
  staffPhotoIds=[],
  services,
  clients,
  appointments,''',1)
anchor='''  staff: Staff[]
  services: Service[]
  clients: Client[]'''
if anchor not in s:raise RuntimeError("DayGrid prop type moved")
s=s.replace(anchor,'''  staff: Staff[]
  staffPhotoIds?: string[]
  services: Service[]
  clients: Client[]''',1)
anchor='''<span className="grid size-8 place-items-center rounded-full bg-surface-3 font-wide text-[13px] font-semibold text-ivory">
                      {s.name[0]}
                    </span>'''
if anchor not in s:raise RuntimeError("Calendar employee avatar markup moved")
s=s.replace(anchor,'''<span className="grid size-9 shrink-0 place-items-center overflow-hidden rounded-full bg-surface-3 font-wide text-[13px] font-semibold text-ivory">
                      {staffPhotoIds.includes(s.id)
                        ? <Image unoptimized width={36} height={36} alt={s.name} src={`/api/staff-avatar/${s.id}`} className="h-full w-full object-cover" />
                        : s.name[0]}
                    </span>''',1)
p.write_text(s,encoding="utf-8")
print("BOOKING_CALENDAR_AVATAR_MATCHES_EMPLOYEE_PROFILE")
