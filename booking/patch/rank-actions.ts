"use server"
import { revalidatePath } from "next/cache"
import { assertPanelSession } from "@/lib/auth/guard"
import { sqlClient } from "@/lib/data/store/postgres"

const LEVELS = ["trainee","junior","barber","senior"] as const
function validLevel(s:string){if(!(LEVELS as readonly string[]).includes(s))throw new Error("Invalid professional level");return s}

export async function setStaffLevel(form:FormData){
 await assertPanelSession()
 const id=String(form.get("staffId")||"")
 const level=validLevel(String(form.get("level")||""))
 if(!/^[0-9a-f-]{36}$/.test(id))throw new Error("Invalid staff member")
 const sql=sqlClient()
 await sql`insert into booking_staff_levels(staff_id,professional_level)
 values(${id},${level}) on conflict(staff_id) do update set
 professional_level=excluded.professional_level,updated_at=now()`
 revalidatePath("/ajustes");revalidatePath("/ranks");revalidatePath("/reservar")
}
export async function setServiceRank(form:FormData){
 await assertPanelSession()
 const serviceId=String(form.get("serviceId")||"")
 const level=validLevel(String(form.get("level")||""))
 const available=String(form.get("available"))==="yes"
 if(!/^[0-9a-f-]{36}$/.test(serviceId))throw new Error("Invalid service")
 const sql=sqlClient()
 await sql`insert into booking_service_levels(service_id,professional_level,available)
 values(${serviceId},${level},${available})
 on conflict(service_id,professional_level) do update set available=excluded.available`
 revalidatePath("/ranks");revalidatePath("/reservar");revalidatePath("/agenda")
}
