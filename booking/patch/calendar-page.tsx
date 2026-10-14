import Link from "next/link"
import { ChevronLeft, ChevronRight, CalendarDays } from "lucide-react"
import { DayGrid } from "@/components/agenda/day-grid"
import { NewAppointmentButton } from "@/components/agenda/new-appointment-button"
import { getAgenda } from "@/lib/data/queries"
import { now, db } from "@/lib/data/repo"
import { addDays,dayKey,formatDayLong,WEEKDAY_SHORT,weekday,hm } from "@/lib/time"
import { cn } from "@/lib/utils"

export const metadata={title:"Calendar | Booking"}
export default async function AgendaPage({searchParams}:PageProps<"/agenda">){
 const params=await searchParams
 const today=dayKey(await now())
 const requested=typeof params.dia==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(params.dia)?params.dia:today
 const d=await getAgenda(requested)
 const mode=params.view==="week"?"week":"day"
 const isToday=d.day===d.today
 const weekly=mode==="week"?await db():null
 const paidSet=new Set(weekly?.payments.filter(p=>p.kind==="servicio"&&p.appointmentId).map(p=>p.appointmentId)||[])
 const link=(day:string,view=mode)=>`/agenda?dia=${day}&view=${view}`
 return <section className="mx-auto flex w-full max-w-[1540px] min-w-0 flex-col px-2 pb-4 pt-3 sm:px-5">
   <div className="mb-3 flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-line bg-surface-1 p-3">
     <div className="flex min-w-0 items-center gap-1.5">
       <Link href={link(addDays(d.day,mode==="week"?-7:-1))} aria-label="Previous date" className="grid size-10 shrink-0 place-items-center rounded-xl border border-line-strong"><ChevronLeft className="size-5"/></Link>
       <div className="min-w-0 px-1.5">
         <p className="text-[10px] uppercase tracking-[0.13em] text-ivory-3">{isToday?"Today":"Selected date"}</p>
         <h1 className="max-w-[170px] truncate text-sm font-semibold capitalize leading-6 text-ivory sm:max-w-none sm:text-lg">{formatDayLong(d.day)}</h1>
       </div>
       <Link href={link(addDays(d.day,mode==="week"?7:1))} aria-label="Next date" className="grid size-10 shrink-0 place-items-center rounded-xl border border-line-strong"><ChevronRight className="size-5"/></Link>
     </div>
     <div className="flex shrink-0 items-center gap-1.5">
       <Link href="/agenda" className="hidden h-10 items-center rounded-xl border border-line-strong px-3 text-xs font-semibold sm:inline-flex">Today</Link>
       <NewAppointmentButton day={d.day}/>
     </div>
   </div>
   <div className="mb-3 flex w-full items-center justify-between gap-2">
     <nav aria-label="Calendar views" className="inline-grid grid-cols-2 rounded-xl border border-line-strong bg-surface-1 p-1">
      <Link href={link(d.day,"day")} aria-current={mode==="day"?"page":undefined} className={cn("rounded-lg px-5 py-2 text-xs font-semibold",mode==="day"?"bg-surface-3 text-ivory":"text-ivory-3")}>Day</Link>
      <Link href={link(d.day,"week")} aria-current={mode==="week"?"page":undefined} className={cn("rounded-lg px-5 py-2 text-xs font-semibold",mode==="week"?"bg-surface-3 text-ivory":"text-ivory-3")}>Week</Link>
     </nav>
     <span className="flex items-center gap-1 text-xs text-ivory-3"><CalendarDays className="size-4"/> {d.staff.length} staff</span>
   </div>
   <nav aria-label="Select day" className="mb-3 grid min-w-0 grid-cols-7 gap-1.5 sm:gap-2">
    {d.week.map(w=>{
     const active=w.day===d.day
     return <Link key={w.day} href={link(w.day)} aria-current={active?"date":undefined}
      className={cn("min-w-0 rounded-xl border px-0.5 py-2 text-center transition-colors",active?"border-ivory-2 bg-surface-3 text-ivory":"border-line bg-surface-1 text-ivory-2",!w.open&&"opacity-50")}>
       <span className="block truncate text-[10px] uppercase">{w.day===d.today?"Today":WEEKDAY_SHORT[weekday(w.day)]}</span>
       <strong className="num mt-1 block text-base font-semibold">{Number(w.day.slice(8))}</strong>
       <span className="mt-1 block text-[10px] text-ivory-3">{w.count} {w.count===1?"booking":"bookings"}</span>
      </Link>
    })}
   </nav>
   {mode==="week"?<div className="grid min-w-0 grid-cols-1 items-start gap-2 sm:grid-cols-2 xl:grid-cols-4">
    {d.week.map(w=>{
      const bookings=(weekly?.appointments||[]).filter(a=>dayKey(a.startsAt)===w.day&&a.status!=="cancelado").sort((a,b)=>a.startsAt.localeCompare(b.startsAt))
      return <section key={w.day} className="min-w-0 overflow-hidden rounded-2xl border border-line bg-surface-1">
        <Link href={link(w.day,"day")} className="flex min-h-16 items-center justify-between gap-2 border-b border-line px-4 py-3">
          <div><h2 className="text-sm font-semibold">{WEEKDAY_SHORT[weekday(w.day)]} · {Number(w.day.slice(8))}</h2>
          <p className="text-xs text-ivory-3">{w.open?"View daily schedule":"Closed"}</p></div>
          <span className="num rounded-full bg-surface-3 px-2 py-1 text-sm font-semibold">{bookings.length}</span>
        </Link>
        <div className="space-y-1.5 p-2">
          {bookings.length===0&&<p className="p-3 text-center text-xs text-ivory-3">No appointments</p>}
          {bookings.map(a=>{
            const worker=weekly?.staff.find(m=>m.id===a.staffId)
            const service=weekly?.services.find(m=>m.id===a.serviceId)
            const client=weekly?.clients.find(m=>m.id===a.clientId)
            return <Link key={a.id} href={link(w.day,"day")+"#"+a.id} className="flex min-w-0 items-start gap-2 rounded-xl border border-line bg-surface-2 p-3">
              <span className="num shrink-0 text-xs font-semibold">{hm(a.startsAt)}</span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-xs font-semibold">{client?.name||"Client"}</span>
                <span className="block truncate text-[11px] text-ivory-3">{service?.name||"Service"} · {worker?.name||"Staff"}</span>
              </span>
              <span className={cn("shrink-0 rounded px-1 py-0.5 text-[10px] font-semibold",paidSet.has(a.id)?"bg-ok/15 text-ok":"bg-surface-3 text-ivory-3")}>{paidSet.has(a.id)?"Paid":"Unpaid"}</span>
            </Link>
          })}
        </div>
      </section>
    })}
   </div>:d.open?<DayGrid day={d.day} isToday={isToday} now={d.now} staff={d.staff}
       services={d.services} clients={d.clients} appointments={d.appointments}
       fixed={d.fixed} paidIds={d.paidAppointmentIds} loyalty={d.loyalty}/>
    :<div className="grid min-h-44 place-items-center rounded-2xl border border-line bg-surface-1 p-6 text-center">
       <div><p className="text-lg font-semibold">Closed on this date</p><p className="mt-2 text-sm text-ivory-3">Choose another day to see appointments.</p>
       <Link href={link(addDays(d.day,1))} className="mt-4 inline-flex rounded-xl border border-line-strong px-4 py-3 text-sm font-semibold">Next day</Link></div>
     </div>}
 </section>
}
