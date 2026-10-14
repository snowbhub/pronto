from pathlib import Path
root=Path("/app")
(root/"src/app/(panel)/analytics").mkdir(parents=True,exist_ok=True)
(root/"src/app/(panel)/analytics/page.tsx").write_text((Path("/tmp/booking-patch")/"analytics-page.tsx").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/components/shell/mobile-nav.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('Package, Users, Wallet }','Package, Users, Wallet, BarChart3 }')
s=s.replace('{href:"/payroll", label:"Payroll", icon:Wallet},','{href:"/payroll", label:"Payroll", icon:Wallet}, {href:"/analytics", label:"Analytics", icon:BarChart3},')
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('<div className="mt-5 max-w-3xl">','''<div className="mt-5 max-w-3xl">
        <Link href="/analytics" className="mb-4 flex min-h-12 items-center justify-between rounded-xl border border-line-strong bg-surface-1 px-4 text-sm font-semibold text-ivory">Analytics · Day, week, month, year <span aria-hidden>→</span></Link>''')
p.write_text(s,encoding="utf-8")
print("BOOKING_ANALYTICS_PERIODS_READY")
