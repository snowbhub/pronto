from pathlib import Path

ROOT = Path("/app")
BUNDLE = Path("/tmp/booking-patch")

# Add one-time, single-use invite keys. Only a SHA-256 digest is stored; the
# raw key is returned once to the authenticated administrator.
actions = ROOT / "src/lib/auth/staff-actions.ts"
body = actions.read_text(encoding="utf-8")
body = body.replace('import { cookies } from "next/headers"', 'import { cookies } from "next/headers"\nimport { createHash, randomBytes } from "node:crypto"', 1)
if 'export async function createStaffInvite' in body:
    raise RuntimeError("staff invite actions already installed")
body += '''

export async function createStaffInvite(staffId: string): Promise<{ ok: true; key: string; expiresAt: string } | { ok: false; error: string }> {
 await assertPanelSession()
 if(!/^[0-9a-f-]{36}$/i.test(staffId))return {ok:false,error:"Choose an active staff member."}
 const sql=sqlClient()
 const staff=await sql`select id from staff where id=${staffId} and active=true`
 if(!staff.length)return {ok:false,error:"Choose an active staff member."}
 const key=randomBytes(24).toString("base64url")
 const tokenHash=createHash("sha256").update(key).digest("hex")
 const expiresAt=new Date(Date.now()+48*60*60*1000).toISOString()
 await sql.begin(async tx=>{
  const locked=await tx`select id from staff where id=${staffId} and active=true for update`
  if(!locked.length)throw new Error("Choose an active staff member.")
  await tx`update booking_staff_invites set revoked_at=now() where staff_id=${staffId} and used_at is null and revoked_at is null`
  await tx`insert into booking_staff_invites(staff_id,token_hash,expires_at) values(${staffId},${tokenHash},${expiresAt})`
 })
 revalidatePath("/staff-accounts")
 return {ok:true,key,expiresAt}
}

export async function registerStaffByInvite(input: { key: string; username: string; password: string }): Promise<{ok:true}|{ok:false;error:string}> {
 const key=String(input.key||"").trim()
 const username=String(input.username||"").trim().toLowerCase()
 const password=String(input.password||"")
 if(!/^[A-Za-z0-9_-]{30,50}$/.test(key))return {ok:false,error:"This invite is invalid, expired or already used."}
 if(!/^[a-z0-9._-]{3,40}$/.test(username))return {ok:false,error:"Choose a username with 3–40 letters, numbers, dots, underscores or hyphens."}
 if(password.length<12||password.length>128)return {ok:false,error:"Use at least 12 characters for your password."}
 const tokenHash=createHash("sha256").update(key).digest("hex")
 const passwordHash=hashStaffPassword(password)
 const sql=sqlClient()
 try {
  await sql.begin(async tx=>{
   const invites=await tx`select id,staff_id from booking_staff_invites where token_hash=${tokenHash} and used_at is null and revoked_at is null and expires_at>now() for update`
   if(!invites.length)throw new Error("INVITE_INVALID")
   const invite=invites[0]
   const staff=await tx`select id from staff where id=${invite.staff_id} and active=true for update`
   if(!staff.length)throw new Error("INVITE_STAFF_INACTIVE")
   const accounts=await tx`select staff_id from booking_staff_accounts where staff_id=${invite.staff_id}`
   if(accounts.length)throw new Error("INVITE_ALREADY_REGISTERED")
   await tx`insert into booking_staff_accounts(staff_id,username,password_hash,active) values(${invite.staff_id},${username},${passwordHash},true)`
   await tx`update booking_staff_invites set used_at=now(),used_by_username=${username} where id=${invite.id} and used_at is null and revoked_at is null`
  })
  return {ok:true}
 } catch(error) {
  const message=String((error as Error)?.message||"")
  if(message.includes("INVITE_STAFF_INACTIVE"))return {ok:false,error:"The invite is no longer valid for an active employee."}
  if(message.includes("INVITE_ALREADY_REGISTERED"))return {ok:false,error:"This invite is invalid, expired or already used."}
  if(message.includes("INVITE_INVALID"))return {ok:false,error:"This invite is invalid, expired or already used."}
  if((error as {code?:string})?.code==="23505")return {ok:false,error:"That username is already in use."}
  throw error
 }
}
'''
actions.write_text(body, encoding="utf-8")

# The register form is intentionally separate from panel and staff sessions.
(ROOT / "src/components/staff/invite-code-button.tsx").parent.mkdir(parents=True, exist_ok=True)
(ROOT / "src/components/staff/invite-code-button.tsx").write_text('''"use client"
import { useState, useTransition } from "react"
import { createStaffInvite } from "@/lib/auth/staff-actions"

export function InviteCodeButton({staffId,expiresAt: initialExpiry}:{staffId:string;expiresAt?:string|null}) {
 const [pending,start]=useTransition()
 const [invite,setInvite]=useState<{key:string;expiresAt:string}|null>(null)
 const [error,setError]=useState("")
 const [copied,setCopied]=useState(false)
 const link=invite?`${typeof window === "undefined" ? "" : window.location.origin}/staff-register?key=${encodeURIComponent(invite.key)}`:""
 return <div className="space-y-2">
  <button type="button" disabled={pending} onClick={()=>{setError("");setInvite(null);start(async()=>{const result=await createStaffInvite(staffId);if(result.ok)setInvite({key:result.key,expiresAt:result.expiresAt});else setError(result.error)})}} className="min-h-11 w-full rounded-xl border border-line-strong px-3 text-sm font-semibold text-ivory disabled:opacity-50">{pending?"Creating…":"Generate invite link"}</button>
  {error&&<p role="alert" className="text-xs text-danger">{error}</p>}
  {invite&&<div className="space-y-2 rounded-xl border border-line-strong bg-surface-2 p-3"><label className="block text-xs text-ivory-3">Registration link<input readOnly value={link} onFocus={e=>e.currentTarget.select()} className="mt-1 h-11 w-full rounded-lg border border-line-strong bg-surface-1 px-2 text-xs text-ivory"/></label><button type="button" onClick={async()=>{try{await navigator.clipboard.writeText(link);setCopied(true)}catch{setCopied(false)}}} className="h-10 w-full rounded-lg bg-ivory text-sm font-semibold text-obsidian">{copied?"Copied":"Copy link"}</button><p className="text-[11px] text-ivory-3">Invite expires {new Date(invite.expiresAt).toLocaleString()}</p></div>}
  {!invite&&initialExpiry&&<p className="text-[11px] text-ivory-3">Invite expires {new Date(initialExpiry).toLocaleString()}</p>}
 </div>
}
''', encoding="utf-8")

(ROOT / "src/components/staff/register-form.tsx").write_text('''"use client"
import { useState,useTransition } from "react"
import { useRouter } from "next/navigation"
import { registerStaffByInvite } from "@/lib/auth/staff-actions"

export function StaffRegisterForm({inviteKey}:{inviteKey:string}) {
 const router=useRouter()
 const [error,setError]=useState("")
 const [pending,start]=useTransition()
 return <form className="mt-6 space-y-4" onSubmit={event=>{event.preventDefault();setError("");const form=new FormData(event.currentTarget);start(async()=>{const result=await registerStaffByInvite({key:String(form.get("key")||""),username:String(form.get("username")||""),password:String(form.get("password")||"")});if(result.ok)router.replace("/staff-login?registered=1");else setError(result.error)})}}>
  <label className="block text-sm font-medium">Invite key<input name="key" required defaultValue={inviteKey} autoComplete="off" className="mt-2 h-12 w-full rounded-xl border border-line-strong bg-surface-1 px-4 text-base"/></label>
  <label className="block text-sm font-medium">Username<input name="username" required minLength={3} maxLength={40} pattern="[a-z0-9._-]{3,40}" autoComplete="username" className="mt-2 h-12 w-full rounded-xl border border-line-strong bg-surface-1 px-4 text-base"/></label>
  <label className="block text-sm font-medium">Password (12–128 characters)<input name="password" type="password" required minLength={12} maxLength={128} autoComplete="new-password" className="mt-2 h-12 w-full rounded-xl border border-line-strong bg-surface-1 px-4 text-base"/></label>
  {error&&<p role="alert" className="text-sm text-danger">{error}</p>}
  <button disabled={pending||inviteKey.length<30} className="h-12 w-full rounded-xl bg-ivory font-semibold text-obsidian disabled:opacity-50">{pending?"Creating…":"Create account"}</button>
 </form>
}
''', encoding="utf-8")

(ROOT / "src/app/staff-register/page.tsx").parent.mkdir(parents=True, exist_ok=True)
(ROOT / "src/app/staff-register/page.tsx").write_text('''import Link from "next/link"
import { StaffRegisterForm } from "@/components/staff/register-form"
export const metadata={title:"Create staff account",robots:{index:false,follow:false},referrer:"no-referrer" as const}
export default async function StaffRegisterPage({searchParams}:{searchParams:Promise<{key?:string}>}) {
 const {key=""}=await searchParams
 return <main className="flex min-h-dvh items-center justify-center bg-obsidian px-5 text-ivory"><section className="w-full max-w-sm rounded-3xl border border-line-strong bg-surface-1 p-6"><div className="mb-6 grid size-14 place-items-center rounded-2xl bg-surface-3 text-2xl">✂</div><h1 className="text-2xl font-bold">Create your staff account</h1><p className="mt-2 text-sm text-ivory-3">Enter the one-time invite key from your manager.</p><StaffRegisterForm inviteKey={key}/><Link href="/staff-login" className="mt-5 block text-center text-sm text-ivory-3 underline underline-offset-4">Staff sign in</Link></section></main>
}
''', encoding="utf-8")

# Allow the registration and existing staff sign-in pages without a panel cookie.
proxy=ROOT/"src/proxy.ts"
body=proxy.read_text(encoding="utf-8")
body=body.replace('if(pathname==="/staff-login")return NextResponse.next()', 'if(pathname==="/staff-login"||pathname==="/staff-register")return NextResponse.next()')
body=body.replace('|staff-login|reservar|','|staff-login|staff-register|reservar|')
proxy.write_text(body,encoding="utf-8")

# Show each staff member's newest invite state and a create-link action in the
# existing account administration screen.
page=ROOT/"src/app/(panel)/staff-accounts/page.tsx"
body=page.read_text(encoding="utf-8")
body=body.replace('import { saveStaffAccount,setStaffAccountActive } from "@/lib/auth/staff-actions"', 'import { saveStaffAccount,setStaffAccountActive } from "@/lib/auth/staff-actions"\nimport { InviteCodeButton } from "@/components/staff/invite-code-button"')
body=body.replace('''const accounts=await sql`select s.id,s.name,s.active as staff_active,a.username,a.active as account_active,a.created_at
  from staff s left join booking_staff_accounts a on a.staff_id=s.id order by s.name`''', '''const accounts=await sql`select s.id,s.name,s.active as staff_active,a.username,a.active as account_active,a.created_at,invite.expires_at as invite_expires_at,invite.used_at as invite_used_at,invite.used_by_username
  from staff s left join booking_staff_accounts a on a.staff_id=s.id
  left join lateral (select expires_at,used_at,used_by_username from booking_staff_invites i where i.staff_id=s.id order by i.created_at desc limit 1) invite on true
  order by s.name`''')
body=body.replace('''    <form action={saveStaffAccount} className="grid grid-cols-2 gap-2">''', '''    {a.invite_used_at&&<p className="text-xs text-ivory-3">Registered through invite as {String(a.used_by_username||a.username)} · {new Date(String(a.invite_used_at)).toLocaleDateString()}</p>}
    <InviteCodeButton staffId={String(a.id)} expiresAt={a.invite_expires_at?String(a.invite_expires_at):null}/>
    <form action={saveStaffAccount} className="grid grid-cols-2 gap-2">'''.replace("+", ""))
if "InviteCodeButton" not in body or "invite_used_at" not in body:
    raise RuntimeError("staff account invite UI was not installed")
body=body.replace("a.used_at&&", "a.invite_used_at&&")
body=body.replace('    <InviteCodeButton staffId={String(a.id)}', '    {!a.username&&<InviteCodeButton staffId={String(a.id)}')
body=body.replace('expiresAt={a.invite_expires_at?String(a.invite_expires_at):null}/>\n', 'expiresAt={a.invite_expires_at?String(a.invite_expires_at):null}/>}\n')
page.write_text(body,encoding="utf-8")

# Confirm registration to staff members after the existing login succeeds.
login=ROOT/"src/app/staff-login/page.tsx"
body=login.read_text(encoding="utf-8")
body=body.replace('export default function StaffLoginPage(){\n return', 'export default async function StaffLoginPage({searchParams}:{searchParams:Promise<{registered?:string}>}){\n const {registered}=await searchParams\n return')
body=body.replace('<StaffLoginForm/>', '{registered==="1"&&<p role="status" className="mt-4 rounded-xl bg-surface-2 p-3 text-sm text-ivory-2">Registration complete. Sign in with your new credentials.</p>}<StaffLoginForm/>')
login.write_text(body,encoding="utf-8")

# Prevent a currency switch from leaving the ARS-only online deposit flow in an
# invalid state. Users can disable online deposits first, then select UAH/EUR.
settings=ROOT/"src/lib/data/settings-actions.ts"
body=settings.read_text(encoding="utf-8")
anchor='''    if (!["EUR", "UAH", "USD", "ARS"].includes(input.currency)) return { ok: false, error: "Choose a supported currency." }
    patch.currency = input.currency as import("@/lib/domain/types").CurrencyCode'''.replace("+", "")
replacement='''    if (!["EUR", "UAH", "USD", "ARS"].includes(input.currency)) return { ok: false, error: "Choose a supported currency." }
    if (input.currency !== "ARS") {
      const current = await store().runtimeSettings?.()
      if (current?.depositEnabled) return { ok: false, error: "Disable online deposits before changing currency from ARS." }
    }
    patch.currency = input.currency as import("@/lib/domain/types").CurrencyCode'''.replace("+", "")
if anchor not in body:
    raise RuntimeError("currency/deposit compatibility guard insertion point missing")
settings.write_text(body.replace(anchor,replacement,1),encoding="utf-8")

# Guard server-side booking creation even if an old/manual database state has
# online deposits enabled in a non-ARS currency.
actions=ROOT/"src/lib/data/actions.ts"
body=actions.read_text(encoding="utf-8")
anchor='''  const useDeposit = !!grid.requireDeposit && s.shopSettings.depositEnabled
  const start = at(input.day, input.time)'''.replace("+", "")
replacement='''  const useDeposit = !!grid.requireDeposit && s.shopSettings.depositEnabled
  if (useDeposit && s.shopSettings.currency !== "ARS") return { ok: false, error: "Online deposits through Mercado Pago require ARS. Disable the deposit or switch the business currency back to ARS." }
  const start = at(input.day, input.time)'''.replace("+", "")
if anchor not in body:
    raise RuntimeError("online deposit currency guard anchor missing")
actions.write_text(body.replace(anchor,replacement,1),encoding="utf-8")

# The currency installer adds migration 0017 before this script runs.
migrator=BUNDLE/"migrate-booking.mjs"
body=migrator.read_text(encoding="utf-8")
old='"0017_currency.sql"'
if old not in body: raise RuntimeError("staff invite migration insertion point missing")
if '"0018_staff_invites.sql"' not in body: body=body.replace(old,old+',"0018_staff_invites.sql"',1)
migrator.write_text(body,encoding="utf-8")

print("BOOKING_STAFF_ONE_TIME_INVITES_INSTALLED")
