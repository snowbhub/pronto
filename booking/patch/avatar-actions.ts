"use server"
import { revalidatePath } from "next/cache"
import { assertPanelSession } from "@/lib/auth/guard"
import { sqlClient } from "@/lib/data/store/postgres"

export async function uploadStaffAvatar(form:FormData):Promise<{ok:boolean;error?:string}>{
 await assertPanelSession()
 const staffId=String(form.get("staffId")||"")
 const file=form.get("photo")
 if(!/^[a-f0-9-]{36}$/.test(staffId)||!(file instanceof File))
  return {ok:false,error:"Choose a valid staff member and image."}
 if(file.type!=="image/jpeg"||file.size<100||file.size>350000)
  return {ok:false,error:"Please use a JPEG image smaller than 350 KB."}
 const buf=Buffer.from(await file.arrayBuffer())
 if(buf[0]!==0xff||buf[1]!==0xd8||buf[2]!==0xff)
  return {ok:false,error:"This file is not a valid JPEG."}
 const sql=sqlClient()
 const existing=await sql`select id from staff where id=${staffId} and active=true`
 if(!existing.length)return {ok:false,error:"Staff member not found."}
 await sql`insert into booking_staff_avatars(staff_id,mime_type,image_data,updated_at)
   values(${staffId},'image/jpeg',${buf},now())
   on conflict(staff_id) do update set mime_type=excluded.mime_type,image_data=excluded.image_data,updated_at=now()`
 revalidatePath("/ajustes")
 revalidatePath("/reservar")
 return {ok:true}
}
