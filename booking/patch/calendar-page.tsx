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
 return <section className="mx-auto flex w-full max-w-[1540px] min-w-0 flex-col gap-2 px-2 pb-4 pt-0 sm:gap-3 sm:px-5 sm:pt-3">
   <div className="sticky top-0 z-20 -mx-2 border-b border-line bg-obsidian/95 px-2 pb-2 pt-1 backdrop-blur sm:static sm:mx-0 sm:rounded-2xl sm:border sm:p-3">
     <div className="flex min-w-0 items-center justify-between gap-2">
       <div className="flex min-w-0 items-center gap-0.5">
         <Link href={link(addDays(d.day,mode==="week"?-7:-1))} aria-label="Previous date" className="grid size-9 shrink-0 place-items-center rounded-lg border border-line-strong"><ChevronLeft className="size-4"/></Link>
         <div className="min-w-0 px-2 text-center">
           <h1 className="max-w-[175px] truncate text-sm font-semibold capitalize text-ivory sm:max-w-none sm:text-base">{formatDayLong(d.day)}</h1>
         </div>
         <Link href={link(addDays(d.day,mode==="week"?7:1))} aria-label="Next date" className="grid size-9 shrink-0 place-items-center rounded-lg border border-line-strong"><ChevronRight className="size-4"/></Link>
       </div>
       <nav aria-label="Calendar views" className="inline-grid shrink-0 grid-cols-2 rounded-lg border border-line-strong bg-surface-1 p-0.5">
         <Link href={link(d.day,"day")} aria-current={mode==="day"?"page":undefined} className={cn("rounded-md px-3 py-2 text-xs font-semibold",mode==="day"?"bg-surface-3 text-ivory":"text-ivory-3")}>Day</Link>
         <Link href={link(d.day,"week")} aria-current={mode==="week"?"page":undefined} className={cn("rounded-md px-3 py-2 text-xs font-semibold",mode==="week"?"bg-surface-3 text-ivory":"text-ivory-3")}>Week</Link>
       </nav>
     </div>
     <nav aria-label="Select day" className="mt-2 grid grid-cols-7 gap-0.5">
       {d.week.map(w=>{
         const active=w.day===d.day
         return <Link key={w.day} href={link(w.day)} aria-current={active?"date":undefined}
           className={cn("grid min-w-0 place-items-center gap-1 rounded-lg px-0.5 py-1.5 text-center transition-colors",active?"bg-surface-3 text-ivory ring-1 ring-line-strong":"text-ivory-2",!w.open&&"opacity-50")}>
           <span className="text-[10px] uppercase leading-4">{WEEKDAY_SHORT[weekday(w.day)]}</span>
           <span className="num text-sm font-semibold leading-5">{Number(w.day.slice(8))}</span>
           <span className={cn("size-1 rounded-full",w.count>0?"bg-ivory":"bg-transparent")} aria-label={w.count+" bookings"}/>
         </Link>
       })}
     </nav>
   </div>
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
