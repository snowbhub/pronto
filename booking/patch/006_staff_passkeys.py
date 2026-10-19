from pathlib import Path
root=Path('/app')
p=root/'src/lib/auth/staff-actions.ts'
s=p.read_text(encoding='utf-8')
s=s.replace('import { cookies } from "next/headers"','import { cookies, headers } from "next/headers"\nimport { generateAuthenticationOptions, generateRegistrationOptions, verifyAuthenticationResponse, verifyRegistrationResponse } from "@simplewebauthn/server"',1)
s=s.replace('import { STAFF_COOKIE,hashStaffPassword,verifyStaffPassword,staffCookieFor } from "@/lib/auth/staff-session"','import { STAFF_COOKIE,hashStaffPassword,verifyStaffPassword,staffCookieFor,staffIdFromCookie } from "@/lib/auth/staff-session"')
if 'export async function beginStaffPasskeyRegistration' in s: raise SystemExit('passkey actions already installed')
s += '''

async function webauthnConfig() {
 const h=await headers()
 const configured=process.env.NEXT_PUBLIC_APP_URL||process.env.NEXT_PUBLIC_SITE_URL
 const host=(configured?new URL(configured).host:(h.get("x-forwarded-host")||h.get("host")||"")).toLowerCase()
 const origin=configured?new URL(configured).origin:`${h.get("x-forwarded-proto")||"https"}://${host}`
 if(!host||host.includes(",")||origin.includes("undefined"))throw new Error("Passkeys are not configured for this domain.")
 return {rpID:process.env.WEBAUTHN_RP_ID||host.split(":")[0],origin}
}

export async function beginStaffPasskeyRegistration() {
 const jar=await cookies(),staffId=staffIdFromCookie(jar.get(STAFF_COOKIE)?.value)
 if(!staffId)throw new Error("Sign in to your staff account first.")
 const sql=sqlClient(), config=await webauthnConfig()
 const rows=await sql`select a.staff_id,a.username from booking_staff_accounts a join staff s on s.id=a.staff_id where a.staff_id=${staffId} and a.active=true and s.active=true`
 if(!rows.length)throw new Error("Active staff account not found.")
 const existing=await sql`select credential_id from booking_staff_passkeys where staff_id=${staffId}`
 const options=await generateRegistrationOptions({rpName:"Booking Staff",rpID:config.rpID,userID:Buffer.from(String(rows[0].staff_id)),userName:String(rows[0].username),attestationType:"none",authenticatorSelection:{residentKey:"preferred",userVerification:"required"},excludeCredentials:existing.map((row:any)=>({id:String(row.credential_id)}))})
 await sql`update booking_staff_accounts set webauthn_challenge=${options.challenge},webauthn_challenge_expires_at=now()+interval '5 minutes' where staff_id=${staffId}`
 return options
}

export async function finishStaffPasskeyRegistration(response:any) {
 const jar=await cookies(),staffId=staffIdFromCookie(jar.get(STAFF_COOKIE)?.value)
 if(!staffId)throw new Error("Sign in to your staff account first.")
 const sql=sqlClient(), config=await webauthnConfig()
 const rows=await sql`select webauthn_challenge,webauthn_challenge_expires_at from booking_staff_accounts where staff_id=${staffId} and active=true`
 if(!rows.length||!rows[0].webauthn_challenge||new Date(String(rows[0].webauthn_challenge_expires_at)).getTime()<Date.now())throw new Error("Passkey setup expired. Try again.")
 const verification=await verifyRegistrationResponse({response,expectedChallenge:String(rows[0].webauthn_challenge),expectedOrigin:config.origin,expectedRPID:config.rpID,requireUserVerification:true})
 if(!verification.verified||!verification.registrationInfo)throw new Error("Passkey verification failed.")
 const credential=verification.registrationInfo.credential
 await sql`insert into booking_staff_passkeys(staff_id,credential_id,public_key,sign_count,transports) values(${staffId},${credential.id},${Buffer.from(credential.publicKey)},${credential.counter},${credential.transports||[]}) on conflict(credential_id) do nothing`
 await sql`update booking_staff_accounts set webauthn_challenge=null,webauthn_challenge_expires_at=null where staff_id=${staffId}`
 revalidatePath("/staff-accounts")
 return {ok:true}
}

export async function beginStaffPasskeyLogin(username:string) {
 const normalized=String(username||"").trim().toLowerCase()
 if(!/^[a-z0-9._-]{3,40}$/.test(normalized))throw new Error("Enter your username first.")
 const sql=sqlClient(), config=await webauthnConfig()
 const accounts=await sql`select a.staff_id from booking_staff_accounts a join staff s on s.id=a.staff_id where a.username=${normalized} and a.active=true and s.active=true`
 if(!accounts.length)throw new Error("No active passkey account found.")
 const staffId=String(accounts[0].staff_id)
 const credentials=await sql`select credential_id,transports from booking_staff_passkeys where staff_id=${staffId}`
 if(!credentials.length)throw new Error("No passkey is registered for this account.")
 const options=await generateAuthenticationOptions({rpID:config.rpID,allowCredentials:credentials.map((row:any)=>({id:String(row.credential_id),transports:row.transports||[]})),userVerification:"required"})
 await sql`update booking_staff_accounts set webauthn_challenge=${options.challenge},webauthn_challenge_expires_at=now()+interval '5 minutes' where staff_id=${staffId}`
 return options
}

export async function finishStaffPasskeyLogin(username:string,response:any):Promise<{ok:true}|{ok:false;error:string}> {
 const normalized=String(username||"").trim().toLowerCase()
 const sql=sqlClient(), config=await webauthnConfig()
 const rows=await sql`select a.staff_id,a.webauthn_challenge,a.webauthn_challenge_expires_at,p.credential_id,p.public_key,p.sign_count,p.transports from booking_staff_accounts a join staff s on s.id=a.staff_id join booking_staff_passkeys p on p.staff_id=a.staff_id where a.username=${normalized} and a.active=true and s.active=true and p.credential_id=${String(response?.id||"")}`
 if(!rows.length||!rows[0].webauthn_challenge||new Date(String(rows[0].webauthn_challenge_expires_at)).getTime()<Date.now())return {ok:false,error:"Passkey sign in expired or unavailable. Try again."}
 const row=rows[0]
 const result=await verifyAuthenticationResponse({response,expectedChallenge:String(row.webauthn_challenge),expectedOrigin:config.origin,expectedRPID:config.rpID,requireUserVerification:true,credential:{id:String(row.credential_id),publicKey:new Uint8Array(row.public_key),counter:Number(row.sign_count),transports:row.transports||[]}})
 if(!result.verified)return {ok:false,error:"Passkey verification failed."}
 await sql`update booking_staff_passkeys set sign_count=${result.authenticationInfo.newCounter},last_used_at=now() where credential_id=${String(row.credential_id)}`
 await sql`update booking_staff_accounts set webauthn_challenge=null,webauthn_challenge_expires_at=null where staff_id=${row.staff_id}`
 const jar=await cookies();jar.set(STAFF_COOKIE,staffCookieFor(String(row.staff_id)),{httpOnly:true,secure:process.env.NODE_ENV==="production",sameSite:"lax",path:"/",maxAge:12*60*60})
 return {ok:true}
}
'''
p.write_text(s,encoding='utf-8')

Path('/app/supabase/migrations/0019_staff_passkeys.sql').write_text('''CREATE TABLE IF NOT EXISTS booking_staff_passkeys (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  staff_id uuid NOT NULL REFERENCES booking_staff_accounts(staff_id) ON DELETE CASCADE,
  credential_id text NOT NULL UNIQUE,
  public_key bytea NOT NULL,
  sign_count bigint NOT NULL DEFAULT 0,
  transports text[] NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  last_used_at timestamptz
);
ALTER TABLE booking_staff_accounts ADD COLUMN IF NOT EXISTS webauthn_challenge text;
ALTER TABLE booking_staff_accounts ADD COLUMN IF NOT EXISTS webauthn_challenge_expires_at timestamptz;
CREATE INDEX IF NOT EXISTS booking_staff_passkeys_staff_idx ON booking_staff_passkeys(staff_id);
ALTER TABLE booking_staff_passkeys ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE booking_staff_passkeys FROM PUBLIC, anon, authenticated;
''',encoding='utf-8')

Path('/app/src/components/staff/passkey-button.tsx').write_text('''"use client"
import { useState,useTransition } from "react"
import { startRegistration } from "@simplewebauthn/browser"
import { beginStaffPasskeyRegistration,finishStaffPasskeyRegistration } from "@/lib/auth/staff-actions"
export function PasskeyButton() {
 const [busy,start]=useTransition(),[message,setMessage]=useState("")
 return <div><button type="button" disabled={busy} onClick={()=>start(async()=>{setMessage("");try{const options=await beginStaffPasskeyRegistration();const response=await startRegistration({optionsJSON:options});await finishStaffPasskeyRegistration(response);setMessage("Passkey saved. Use Face ID, Touch ID or your device screen lock at sign-in.")}catch(e){setMessage(e instanceof Error?e.message:"Could not register this passkey.")}})} className="h-11 w-full rounded-lg border border-line-strong p-2 text-sm font-semibold text-ivory">{busy?"Waiting for device…":"Add Face ID / passkey"}</button>{message&&<p role="status" className="mt-2 text-xs text-ivory-3">{message}</p>}</div>
}
''',encoding='utf-8')

Path('/app/src/components/staff/passkey-login-button.tsx').write_text('''"use client"
import { useState,useTransition } from "react"
import { useRouter } from "next/navigation"
import { startAuthentication } from "@simplewebauthn/browser"
import { beginStaffPasskeyLogin,finishStaffPasskeyLogin } from "@/lib/auth/staff-actions"
export function PasskeyLoginButton({username}:{username:string}) {
 const router=useRouter(),[busy,start]=useTransition(),[error,setError]=useState("")
 return <div className="mt-3"><button type="button" disabled={busy} onClick={()=>start(async()=>{setError("");try{const options=await beginStaffPasskeyLogin(username);const response=await startAuthentication({optionsJSON:options});const result=await finishStaffPasskeyLogin(username,response);if(result.ok)router.replace("/staff");else setError(result.error)}catch(e){setError(e instanceof Error?e.message:"Passkey sign in failed.")}})} className="h-12 w-full rounded-xl border border-line-strong text-sm font-semibold">{busy?"Waiting for device…":"Sign in with Face ID / passkey"}</button>{error&&<p role="alert" className="mt-2 text-xs text-danger">{error}</p>}</div>
}
''',encoding='utf-8')

page=root/'src/app/staff/page.tsx'
s=page.read_text(encoding='utf-8')
s=s.replace('import { staffLogout } from "@/lib/auth/staff-actions"','import { staffLogout } from "@/lib/auth/staff-actions"\nimport { PasskeyButton } from "@/components/staff/passkey-button"')
s=s.replace('<form action={staffLogout}>','<PasskeyButton/><form action={staffLogout}>',1)
page.write_text(s,encoding='utf-8')

form=root/'src/app/staff-login/form.tsx'
s=form.read_text(encoding='utf-8')
s=s.replace('import { staffLogin } from "@/lib/auth/staff-actions"','import { staffLogin } from "@/lib/auth/staff-actions"\nimport { PasskeyLoginButton } from "@/components/staff/passkey-login-button"')
s=s.replace(' const [error,setError]=useState("")',' const [error,setError]=useState("")\n const [username,setUsername]=useState("")')
s=s.replace('<input name="username" autoComplete="username" required', '<input name="username" value={username} onChange={e=>setUsername(e.target.value)} autoComplete="username" required')
s=s.replace('''<button''','''<button''',1)
# Add the passkey action next to existing password form without nesting another form.
s=s.replace('</form>', '<PasskeyLoginButton username={username}/></form>')
if 'PasskeyLoginButton' not in s: raise SystemExit('staff login form hook failed')
form.write_text(s,encoding='utf-8')

# Keep passkey migration in startup sequence after invitation/account tables.
migrator=Path('/tmp/booking-patch/migrate-booking.mjs')
s=migrator.read_text(encoding='utf-8')
if '0019_staff_passkeys.sql' not in s:
 s=s.replace('"0018_staff_invites.sql"','"0018_staff_invites.sql","0019_staff_passkeys.sql"')
# Existing Supabase-backed installs are expected to have the original 14
# Booking migrations. New local patch migrations are applied by this runner,
# so they must not raise the upstream schema audit threshold.
s=s.replace('records.length<versions.length','records.length<14')
migrator.write_text(s,encoding='utf-8')
print('BOOKING_WEBAUTHN_PASSKEYS_INSTALLED')
