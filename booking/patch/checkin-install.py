from pathlib import Path
root=Path("/app")
a=root/"src/lib/staff/checkin-actions.ts"
a.parent.mkdir(parents=True,exist_ok=True)
a.write_text((Path("/tmp/booking-patch")/"checkin-actions.ts").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/lib/data/queries.ts"
s=p.read_text(encoding="utf-8")
s='import { sqlClient } from "@/lib/data/store/postgres"\nimport { TZ } from "@/lib/time"\n'+s
needle='''  const week = Array.from({ length: 7 }, (_, i) => addDays(day, i - ((new Date(`${day}T12:00:00-03:00`).getUTCDay() + 6) % 7)))'''
# Use an insertion before the existing return, regardless of how the week calculation has been rewritten.
start=s.index("export async function getAgenda(day: string)")
ret=s.index("  return {",start)
insert='''  let arrivedIds: string[]=[]
  if(process.env.DATABASE_URL){
    const sql=sqlClient()
    const checkins=await sql`select c.appointment_id from booking_checkins c
      join appointments a on a.id=c.appointment_id
      where (a.starts_at at time zone ${TZ})::date=${day}::date
        and a.status not in ('cancelado','no_show')`
    arrivedIds=checkins.map(x=>String(x.appointment_id))
  }
'''
s=s[:ret]+insert+s[ret:]
start=s.index("export async function getAgenda(day: string)")
i=s.index("    paidAppointmentIds:",start)
s=s[:i]+'    arrivedIds,\n'+s[i:]
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/agenda/page.tsx"
s=p.read_text(encoding="utf-8")
old='''fixed={d.fixed} paidIds={d.paidAppointmentIds} loyalty={d.loyalty}'''
if old not in s:raise RuntimeError("Current calendar props missing")
s=s.replace(old,'''fixed={d.fixed} paidIds={d.paidAppointmentIds} arrivedIds={d.arrivedIds} loyalty={d.loyalty}''')
p.write_text(s,encoding="utf-8")
p=root/"src/components/agenda/day-grid.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('import { reassignAppointment, setAppointmentStatus } from "@/lib/data/actions"',
'''import { reassignAppointment, setAppointmentStatus } from "@/lib/data/actions"
import { setAppointmentCheckIn } from "@/lib/staff/checkin-actions"''')
s=s.replace('''  paidIds,
  loyalty,
}: {''','''  paidIds,
  arrivedIds,
  loyalty,
}: {''',1)
s=s.replace('''  paidIds: string[]
  loyalty:''','''  paidIds: string[]
  arrivedIds: string[]
  loyalty:''',1)
s=s.replace('''  const paid = new Set(paidIds)''','''  const paid = new Set(paidIds)
  const arrivedSet = new Set(arrivedIds)''',1)
s=s.replace('''        paid={selected ? paid.has(selected.id) : false}''','''        paid={selected ? paid.has(selected.id) : false}
        arrived={selected ? arrivedSet.has(selected.id) : false}''',1)
s=s.replace('''  paid,
  onClose,''','''  paid,
  arrived,
  onClose,''',1)
s=s.replace('''  paid: boolean
  onClose:''','''  paid: boolean
  arrived: boolean
  onClose:''',1)
i=s.index("  function move(status: AppointmentStatus",s.index("function AppointmentSheet"))
s=s[:i]+'''  function toggleCheckIn(next:boolean){
    if(!a)return
    startTransition(async()=>{
      const result=await setAppointmentCheckIn(a.id,next)
      if(!result.ok)toast.error(result.error)
      else{toast.success(next?"Client checked in":"Check-in undone");onClose()}
    })
  }

'''+s[i:]
anchor='''                  {paid?"Paid":"Unpaid"}
                </span>'''
if anchor not in s:raise RuntimeError("Payment status badge expected")
s=s.replace(anchor,anchor+'''
                {arrived && <span className="rounded-full bg-ok/15 px-2 py-0.5 text-[11px] font-semibold text-ok">Arrived</span>}''',1)
i=s.index('''              {a.status === "pendiente" && (''',s.index("function AppointmentSheet"))
s=s[:i]+'''              {["pendiente","confirmado"].includes(a.status) && (
                <Button variant="outline" className="h-11 w-full" disabled={pending} onClick={()=>toggleCheckIn(!arrived)}>
                  {arrived?"Undo check-in":"Client arrived"}
                </Button>
              )}
'''+s[i:]
p.write_text(s,encoding="utf-8")
print("BOOKING_ARRIVAL_AND_PAYMENT_STATE_CONNECTED")
