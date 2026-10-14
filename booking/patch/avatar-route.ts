import { sqlClient } from "@/lib/data/store/postgres"
export const runtime="nodejs"
export async function GET(_request:Request,ctx:{params:Promise<{id:string}>}){
 const {id}=await ctx.params
 if(!/^[a-f0-9-]{36}$/.test(id))return new Response("Not found",{status:404})
 const sql=sqlClient()
 const rows=await sql`select mime_type,image_data,updated_at from booking_staff_avatars where staff_id=${id}`
 if(!rows.length)return new Response("Not found",{status:404})
 const bytes=rows[0].image_data as Uint8Array
 return new Response(new Uint8Array(bytes),{headers:{"Content-Type":String(rows[0].mime_type),"Cache-Control":"public, max-age=300, stale-while-revalidate=3600","X-Content-Type-Options":"nosniff"}})
}
