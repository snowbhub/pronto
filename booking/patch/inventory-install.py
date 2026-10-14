from pathlib import Path
root=Path("/app")
bundle=Path("/tmp/booking-patch")
(root/"src/lib/inventory").mkdir(parents=True,exist_ok=True)
(root/"src/lib/inventory/actions.ts").write_text((bundle/"inventory-actions.ts").read_text(encoding="utf-8"),encoding="utf-8")
(root/"src/app/(panel)/inventory").mkdir(parents=True,exist_ok=True)
(root/"src/app/(panel)/inventory/page.tsx").write_text((bundle/"inventory-page.tsx").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/components/shell/mobile-nav.tsx"
s=p.read_text(encoding="utf-8").replace('CalendarDays, Ellipsis, House, LogOut, MessagesSquare, Plus','CalendarDays, Ellipsis, House, LogOut, MessagesSquare, Plus, Package')
s=s.replace('const rest = [...NAV.flatMap((g) => g.items), SETTINGS_ITEM].filter(', 'const rest = [...NAV.flatMap((g) => g.items), { href: "/inventory", label: "Inventory", icon: Package }, SETTINGS_ITEM].filter(')
p.write_text(s,encoding="utf-8")
# Add discoverability in settings without modifying existing settings editor.
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('<div className="mt-5 max-w-3xl">','''<div className="mt-5 max-w-3xl">
        <Link href="/inventory" className="mb-4 flex min-h-12 items-center justify-between rounded-xl border border-line-strong bg-surface-1 px-4 text-sm font-semibold text-ivory">Inventory · Products, stock & sales <span aria-hidden>→</span></Link>''')
p.write_text(s,encoding="utf-8")
print("BOOKING_INVENTORY_WIRED")
