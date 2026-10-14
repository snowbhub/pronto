"use server"
import { revalidatePath } from "next/cache"
import { assertPanelSession } from "@/lib/auth/guard"
import { sqlClient } from "@/lib/data/store/postgres"

export async function setAppointmentCheckIn(id:string,arrived:boolean):Promise<{ok:boolean;error?:string}> {
 await assertPanelSession()
 if(!/^[a-f0-9]{8}-[a-f0-9-]{27}$/i.test(id))return {ok:false,error:"Invalid appointment."}
 const sql=sqlClient()
 const appointments=await sql`select id,status from appointments where id=${id}`
 if(!appointments.length)return {ok:false,error:"Appointment not found."}
 if(["cancelado","no_show"].includes(String(appointments[0].status)))
  return {ok:false,error:"A cancelled or missed appointment cannot be checked in."}
 if(arrived)
  await sql`insert into booking_checkins(appointment_id) values(${id}) on conflict(appointment_id) do update set arrived_at=now()`
 else
  await sql`delete from booking_checkins where appointment_id=${id}`
 revalidatePath("/agenda")
 revalidatePath("/")
 return {ok:true}
}
