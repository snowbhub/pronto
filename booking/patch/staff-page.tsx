import { redirect } from "next/navigation"
import { db,now } from "@/lib/data/repo"
import { currentActiveStaffId } from "@/lib/staff/booking-actions"
import { staffLogout } from "@/lib/auth/staff-actions"
import { addDays,dayKey,hm,TZ } from "@/lib/time"
import { freeSlots } from "@/lib/domain/slots"
import { StaffBookingForm } from "./booking-form"
export const metadata={title:"My schedule"}
export default async function StaffPage(){
 const staffId=await currentActiveStaffId()
 if(!staffId)redirect("/staff-login")
 const snapshot=await db()
 const member=snapshot.staff.find(x=>x.id===staffId&&x.active)
 if(!member)redirect("/staff-login")
 const rightNow=await now()
 const today=dayKey(rightNow)
 const nextDays=Array.from({length:10},(_,i)=>addDays(today,i))
 const fmt=(date:string)=>new Intl.DateTimeFormat("en-GB",{timeZone:TZ,weekday:"short",day:"numeric",month:"short"}).format(new Date(date+"T12:00:00Z"))
 const available=snapshot.services.filter(x=>x.active&&!member.skipsServiceIds.includes(x.id))
 const slots=nextDays.flatMap(day=>available.flatMap(service=>freeSlots({
  day,service,staff:member,appointments:snapshot.appointments,now:rightNow,stepMin:snapshot.shopSettings.slotStepMin
 }).slice(0,10).map(time=>({value:service.id+"|"+day+"|"+time,label:fmt(day)+" · "+time+" · "+service.name}))))
 const appointments=snapshot.appointments.filter(x=>x.staffId===staffId&&x.startsAt>=new Date(Date.now()-3600000).toISOString()&&x.status!=="cancelado").slice(0,70)
 const clients=new Map(snapshot.clients.map(c=>[c.id,c]))
 const services=new Map(snapshot.services.map(s=>[s.id,s]))
 return <main className="min-h-dvh bg-obsidian text-ivory">
   <div className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-line bg-obsidian/95 px-4 backdrop-blur-xl">
    <div><div className="text-lg font-bold">My schedule</div><div className="text-xs text-ivory-3">{member.name}</div></div>
    <form action={staffLogout}><button className="rounded-xl border border-line-strong px-4 py-2 text-sm">Sign out</button></form>
   </div>
   <div className="mx-auto w-full max-w-xl space-y-5 px-4 pb-12 pt-5">
    <section className="panel p-4"><h1 className="mb-3 text-lg font-semibold">Upcoming appointments</h1>
     {!appointments.length&&<p className="text-sm text-ivory-3">No appointments scheduled yet.</p>}
     <ul className="divide-y divide-line">{appointments.map(a=><li key={a.id} className="flex items-center justify-between gap-3 py-3">
       <div className="min-w-0"><p className="font-medium">{clients.get(a.clientId)?.name||"Client"}</p><p className="text-xs text-ivory-3">{services.get(a.serviceId)?.name||"Service"}</p></div>
       <div className="shrink-0 text-right"><p className="text-sm font-semibold">{hm(a.startsAt)}</p><p className="text-xs text-ivory-3">{fmt(dayKey(a.startsAt))}</p></div>
     </li>)}</ul>
    </section>
    <section className="panel p-4"><h2 className="mb-3 text-lg font-semibold">New appointment</h2><StaffBookingForm options={slots}/></section>
   </div>
 </main>
}
