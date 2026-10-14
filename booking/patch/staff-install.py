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
