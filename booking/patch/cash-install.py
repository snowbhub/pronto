from pathlib import Path
root=Path("/app")
bundle=Path("/tmp/booking-patch")
(root/"src/lib/cash-management").mkdir(parents=True,exist_ok=True)
(root/"src/lib/cash-management/actions.ts").write_text((bundle/"cash-actions.ts").read_text(encoding="utf-8"),encoding="utf-8")
(root/"src/app/(panel)/cash-management").mkdir(parents=True,exist_ok=True)
(root/"src/app/(panel)/cash-management/page.tsx").write_text((bundle/"cash-page.tsx").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/components/shell/mobile-nav.tsx"
s=p.read_text(encoding="utf-8").replace('Wallet, BarChart3 }','Wallet, BarChart3, Banknote }')
s=s.replace('{href:"/analytics", label:"Analytics", icon:BarChart3},','{href:"/analytics", label:"Analytics", icon:BarChart3}, {href:"/cash-management", label:"Cash & expenses", icon:Banknote},')
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('<div className="mt-5 max-w-3xl">','''<div className="mt-5 max-w-3xl">
        <Link href="/cash-management" className="mb-4 flex min-h-12 items-center justify-between rounded-xl border border-line-strong bg-surface-1 px-4 text-sm font-semibold text-ivory">Cash collections · Expenses <span aria-hidden>→</span></Link>''')
p.write_text(s,encoding="utf-8")
print("BOOKING_CASH_MANAGEMENT_WIRED")
