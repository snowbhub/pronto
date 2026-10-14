from pathlib import Path
root=Path("/app")
(root/"src/app/(panel)/payroll").mkdir(parents=True,exist_ok=True)
(root/"src/app/(panel)/payroll/page.tsx").write_text((Path("/tmp/booking-patch")/"payroll-page.tsx").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/components/shell/mobile-nav.tsx"
s=p.read_text(encoding="utf-8").replace('Package, Users }','Package, Users, Wallet }')
s=s.replace('{href:"/staff-accounts", label:"Staff access", icon:Users},','{href:"/staff-accounts", label:"Staff access", icon:Users}, {href:"/payroll", label:"Payroll", icon:Wallet},')
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8").replace('<div className="mt-5 max-w-3xl">','''<div className="mt-5 max-w-3xl">
        <Link href="/payroll" className="mb-4 flex min-h-12 items-center justify-between rounded-xl border border-line-strong bg-surface-1 px-4 text-sm font-semibold text-ivory">Payroll · Custom date ranges <span aria-hidden>→</span></Link>''')
p.write_text(s,encoding="utf-8")
print("BOOKING_PAYROLL_RANGE_WIRED")
