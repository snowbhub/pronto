"use server"
import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { revalidatePath } from "next/cache"
import { assertPanelSession } from "@/lib/auth/guard"
import { sqlClient } from "@/lib/data/store/postgres"
import { STAFF_COOKIE,hashStaffPassword,verifyStaffPassword,staffCookieFor } from "@/lib/auth/staff-session"

export async function staffLogin(form:FormData):Promise<{ok:false;error:string}>{
 const username=String(form.get("username")||"").trim().toLowerCase()
 const password=String(form.get("password")||"")
 if(!username||!password)return {ok:false,error:"Enter username and password."}
 const sql=sqlClient()
 const rows=await sql`select a.staff_id,a.password_hash from booking_staff_accounts a
 join staff s on s.id=a.staff_id
 where a.username=${username} and a.active=true and s.active=true`
 if(!rows.length||!verifyStaffPassword(password,String(rows[0].password_hash)))
  return {ok:false,error:"Invalid credentials."}
 const jar=await cookies()
 jar.set(STAFF_COOKIE,staffCookieFor(String(rows[0].staff_id)),{
  httpOnly:true,secure:process.env.NODE_ENV==="production",sameSite:"lax",path:"/",maxAge:12*60*60
 })
 redirect("/staff")
}
export async function staffLogout(){
 const jar=await cookies()
 jar.delete(STAFF_COOKIE)
 redirect("/staff-login")
}
export async function saveStaffAccount(form:FormData){
 await assertPanelSession()
 const staffId=String(form.get("staffId")||"")
 const username=String(form.get("username")||"").trim().toLowerCase()
 const password=String(form.get("password")||"")
 if(!/^[0-9a-f-]{36}$/.test(staffId)||!/^[a-z0-9._-]{3,40}$/.test(username))
  throw new Error("Invalid staff or username")
 const sql=sqlClient()
 const staff=await sql`select id from staff where id=${staffId} and active=true`
 if(!staff.length)throw new Error("Staff member not active")
 const secret=hashStaffPassword(password)
 await sql`insert into booking_staff_accounts(staff_id,username,password_hash,active) values
  (${staffId},${username},${secret},true)
  on conflict(staff_id) do update set username=excluded.username,password_hash=excluded.password_hash,active=true,updated_at=now()`
 revalidatePath("/staff-accounts")
}
export async function setStaffAccountActive(form:FormData){
 await assertPanelSession()
 const staffId=String(form.get("staffId")||"")
 if(!/^[0-9a-f-]{36}$/.test(staffId))throw new Error("Invalid staff")
 const active=String(form.get("active"))==="true"
 const sql=sqlClient()
 await sql`update booking_staff_accounts set active=${active},updated_at=now() where staff_id=${staffId}`
 revalidatePath("/staff-accounts")
}
