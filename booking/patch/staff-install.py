from pathlib import Path
root=Path("/app")
source=Path("/tmp/booking-patch")
paths={
 "staff-auth.ts":"src/lib/auth/staff-session.ts",
 "staff-login-actions.ts":"src/lib/auth/staff-actions.ts",
 "staff-login-form.tsx":"src/app/staff-login/form.tsx",
 "staff-login-page.tsx":"src/app/staff-login/page.tsx",
 "staff-accounts-page.tsx":"src/app/(panel)/staff-accounts/page.tsx",
 "staff-booking-actions.ts":"src/lib/staff/booking-actions.ts",
 "staff-booking-form.tsx":"src/app/staff/booking-form.tsx",
 "staff-page.tsx":"src/app/staff/page.tsx",
}
for src,dst in paths.items():
 p=root/dst
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((source/src).read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/proxy.ts"
s=p.read_text(encoding="utf-8")
s=s.replace('import { isValidSession, PANEL_COOKIE } from "@/lib/auth/session"','import { isValidSession, PANEL_COOKIE } from "@/lib/auth/session"\nimport { STAFF_COOKIE,staffIdFromCookie } from "@/lib/auth/staff-session"')
s=s.replace("|login|reservar|","|login|staff-login|reservar|")
s=s.replace('export function proxy(request: NextRequest) {','''export function proxy(request: NextRequest) {
  const pathname=request.nextUrl.pathname
  if(pathname==="/staff-login")return NextResponse.next()
  if(pathname==="/staff"||pathname.startsWith("/staff/")){
    if(staffIdFromCookie(request.cookies.get(STAFF_COOKIE)?.value))return NextResponse.next()
    return NextResponse.redirect(new URL("/staff-login",request.url))
  }''')
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8").replace('<div className="mt-5 max-w-3xl">','''<div className="mt-5 max-w-3xl">
        <Link href="/staff-accounts" className="mb-4 flex min-h-12 items-center justify-between rounded-xl border border-line-strong bg-surface-1 px-4 text-sm font-semibold text-ivory">Staff logins · Individual passwords <span aria-hidden>→</span></Link>''')
p.write_text(s,encoding="utf-8")
p=root/"src/components/shell/mobile-nav.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('CalendarDays, Ellipsis, House, LogOut, MessagesSquare, Plus, Package','CalendarDays, Ellipsis, House, LogOut, MessagesSquare, Plus, Package, Users')
s=s.replace('{ href: "/inventory", label: "Inventory", icon: Package },','{ href: "/inventory", label: "Inventory", icon: Package }, {href:"/staff-accounts", label:"Staff access", icon:Users},')
p.write_text(s,encoding="utf-8")
print("BOOKING_STAFF_RBAC_ISOLATED")


# Present level, credentials and commission together in every employee's card.
p=root/"src/components/settings/team-editor.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('import { useState, useTransition } from "react"',
'''import { useState, useTransition } from "react"
import { setStaffLevel } from "@/lib/ranks/actions"
import { saveStaffAccount, setStaffAccountActive } from "@/lib/auth/staff-actions"
import Link from "next/link"''')
s=s.replace('export function TeamEditor({ staff, timeOff, today }: { staff: Staff[]; timeOff: TimeOffEntry[]; today: string }) {',
'''export function TeamEditor({ staff, timeOff, today, accounts=[] }: { staff: Staff[]; timeOff: TimeOffEntry[]; today: string; accounts?: {staffId:string;username:string;active:boolean}[] }) {''')
anchor='''          <div className="space-y-4 px-5 pb-5">
            {/* La key'''
section='''          <div className="space-y-4 px-5 pb-5">
            <details className="min-w-0 rounded-xl border border-line-strong bg-surface-2 p-3">
              <summary className="cursor-pointer text-sm font-semibold text-ivory">Rank, commission & login · Edit employee</summary>
              <div className="mt-4 space-y-4">
                <p className="text-xs text-ivory-3">Change employee name, commission and profile details using the pencil above.</p>
                <form action={setStaffLevel} className="flex min-w-0 gap-2">
                  <input type="hidden" name="staffId" value={m.id} />
                  <label className="min-w-0 flex-1 text-xs text-ivory-2">Professional level
                    <select name="level" defaultValue={m.professionalLevel || "barber"} className="mt-1 h-11 w-full min-w-0 rounded-lg border border-line-strong bg-surface-1 px-2 text-sm text-ivory">
                      <option value="trainee">Trainee</option><option value="junior">Junior barber</option>
                      <option value="barber">Barber</option><option value="senior">Senior barber</option>
                    </select>
                  </label>
                  <button className="self-end rounded-lg border border-line-strong px-3 py-3 text-xs text-ivory">Save</button>
                </form>
                <form action={saveStaffAccount} className="space-y-2">
                  <input type="hidden" name="staffId" value={m.id} />
                  <p className="text-xs font-semibold text-ivory-2">Employee login</p>
                  <input required pattern="[a-z0-9._-]{3,40}" name="username" placeholder="Username" defaultValue={accounts.find(a=>a.staffId===m.id)?.username || ""} autoComplete="off" className="h-11 w-full min-w-0 rounded-lg border border-line-strong bg-surface-1 px-3 text-base text-ivory"/>
                  <input type="password" required minLength={12} maxLength={128} name="password" placeholder="New password (12+ characters)" autoComplete="new-password" className="h-11 w-full min-w-0 rounded-lg border border-line-strong bg-surface-1 px-3 text-base text-ivory"/>
                  <button className="h-11 w-full rounded-lg bg-ivory text-sm font-semibold text-obsidian">Create / update staff login</button>
                </form>
                {accounts.some(a=>a.staffId===m.id) && <form action={setStaffAccountActive}>
                  <input type="hidden" name="staffId" value={m.id}/>
                  <input type="hidden" name="active" value={accounts.find(a=>a.staffId===m.id)?.active?"false":"true"}/>
                  <button className="w-full rounded-lg border border-line-strong p-3 text-sm text-ivory">{accounts.find(a=>a.staffId===m.id)?.active?"Disable employee login":"Enable employee login"}</button>
                </form>}
                <Link href="/payroll" className="block rounded-lg border border-line-strong p-3 text-center text-sm font-semibold text-ivory">View earnings and payouts →</Link>
              </div>
            </details>
            {/* La key'''
details = "            <details" + section.split("<details",1)[1].split("            {/* La key",1)[0]
if "          </header>" not in s: raise RuntimeError("Employee header missing")
s=s.replace("          </header>", "          </header>\n"+details,1)
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
s='import { sqlClient } from "@/lib/data/store/postgres"\n'+s
s=s.replace('const s = await db()', 'const s = await db()') 
s=s.replace('{tab === "equipo" && <TeamEditor staff={s.staff} timeOff={s.timeOff} today={dayKey(await now())} />}',
'''{tab === "equipo" && <TeamEditor staff={s.staff} timeOff={s.timeOff} today={dayKey(await now())}
          accounts={(await sqlClient()`select staff_id,username,active from booking_staff_accounts`).map(a=>({staffId:String(a.staff_id),username:String(a.username),active:Boolean(a.active)}))} />}''')
p.write_text(s,encoding="utf-8")
print("BOOKING_UNIFIED_STAFF_CARDS_READY")
