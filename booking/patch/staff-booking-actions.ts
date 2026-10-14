"use server"
import { cookies } from "next/headers"
import { revalidatePath } from "next/cache"
import { STAFF_COOKIE,staffIdFromCookie } from "@/lib/auth/staff-session"
import { sqlClient } from "@/lib/data/store/postgres"
import { db,store,now } from "@/lib/data/repo"
import { at } from "@/lib/time"
import { freeSlots } from "@/lib/domain/slots"

export async function currentActiveStaffId():Promise<string|null>{
 const jar=await cookies()
 const id=staffIdFromCookie(jar.get(STAFF_COOKIE)?.value)
 if(!id)return null
 const sql=sqlClient()
 const matches=await sql`select 1 from booking_staff_accounts a join staff s on s.id=a.staff_id
  where a.staff_id=${id} and a.active=true and s.active=true`
 return matches.length?id:null
}
export async function createStaffAppointment(form:FormData):Promise<{ok:boolean;error?:string}>{
 const staffId=await currentActiveStaffId()
 if(!staffId)return {ok:false,error:"Session expired. Sign in again."}
 const chosen=String(form.get("slot")||"")
 const [serviceId,day,time]=chosen.split("|")
 const name=String(form.get("name")||"").trim().slice(0,80)
 const phone=String(form.get("phone")||"").replace(/[^+\d]/g,"").slice(0,30)
 if(!/^[0-9a-f-]{36}$/.test(serviceId||"")||!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(day||"")||!/^[0-2][0-9]:[0-5][0-9]$/.test(time||""))
  return {ok:false,error:"Choose a valid service and time."}
 if(name.length<2||phone.replace(/\D/g,"").length<8)return {ok:false,error:"Enter a name and a valid phone number."}
 const data=await db()
 const staff=data.staff.find(x=>x.id===staffId&&x.active)
 const service=data.services.find(x=>x.id===serviceId&&x.active)
 if(!staff||!service)return {ok:false,error:"Service or staff unavailable."}
 const slots=freeSlots({day,staff,service,appointments:data.appointments,now:await now(),stepMin:data.shopSettings.slotStepMin})
 if(!slots.includes(time))return {ok:false,error:"This appointment slot is no longer available."}
 const start=at(day,time)
 try{
  await store().createAppointment({
    appointment:{staffId,serviceId,startsAt:start.toISOString(),
     endsAt:new Date(start.getTime()+service.durationMin*60000).toISOString(),
     status:"confirmado",source:"panel",price:service.price,notes:null,conversationId:null,holdExpiresAt:null},
    newClient:{name,phone,channel:"whatsapp",notes:null,preferredStaffId:staffId}
  })
 }catch{
  return {ok:false,error:"Unable to save booking. The selected slot may already be taken."}
 }
 revalidatePath("/staff")
 revalidatePath("/agenda")
 return {ok:true}
}
