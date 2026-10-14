from pathlib import Path
r=Path("/app")
def change(rel,replacements):
 p=r/rel
 s=p.read_text(encoding="utf-8")
 for a,b in replacements:s=s.replace(a,b)
 p.write_text(s,encoding="utf-8")
change("src/app/(panel)/ajustes/page.tsx",[
 ('Panel title="Horarios que se ofrecen"','Panel title="Available appointment intervals"'),
 ('value="Argentina (UTC−3)"','value={TZ}'),
 ('import { dayKey } from "@/lib/time"','import { dayKey, TZ } from "@/lib/time"'),
 ('label="Zona horaria"','label="Time zone"'),
])
change("src/components/caja/caja-view.tsx",[
 (">Contado</dt>",">Cash counted</dt>"),
])
for path in ["src/components/caja/charge-dialog.tsx","src/components/caja/quick-charge-dialog.tsx"]:
 change(path,[("Tarjeta completa: 50% de descuento","Loyalty card complete: 50% discount")])
change("src/components/finance/week-view.tsx",[
 ("Cortes, products, drinks and tips.","Haircuts, products, drinks and tips."),
 ("Cortes, productos, bebidas y propinas.","Haircuts, products, drinks and tips."),
 ("Cortes","Haircuts"),
])
change("src/components/settings/team-editor.tsx",[
 ('aria-label="Quitar franco"','aria-label="Remove day off"'),
 ('"Franco quitado"','"Day off removed"'),
])
print("BOOKING_LAST_SIX_SPANISH_UI_STRINGS_FIXED")

change("src/components/shell/sidebar.tsx",[
 (">Santi</span>",">Administrator</span>"),
 (">Dueño</span>",">Owner</span>"),
])
change("src/app/(panel)/page.tsx",[
 ('${greeting}, Santi','${greeting}'),
])
print("BOOKING_OWNER_NAME_DEMO_COPY_REMOVED")

change("src/components/clients/clients-view.tsx",[
 (" visitas</span>"," visits</span>"),
])
change("src/components/hoy/day-timeline.tsx",[
 (">fijo</span>",">Fixed</span>"),
])
change("src/components/settings/team-editor.tsx",[
 ("\n                          a\n","\n                          to\n"),
 (" al ${formatDayShort(last)}"," to ${formatDayShort(last)}"),
 (" a ${hm(to)}"," to ${hm(to)}"),
])
print("BOOKING_SMALL_DYNAMIC_UI_SPANISH_REMOVED")
