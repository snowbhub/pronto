from pathlib import Path
import re
root=Path("/app/src")
layout=root/"app/(panel)/layout.tsx"
s=layout.read_text(encoding="utf-8")
if 'from "next/headers"' not in s:
    s='import { cookies } from "next/headers"\n'+s
if 'normalizeLocale' not in s:
    s='import { normalizeLocale } from "@/i18n/messages"\n'+s
anchor='  const shell = await getShell()'
assert anchor in s,"Layout shell data anchor missing"
s=s.replace(anchor,anchor+'\n  const initialLocale=normalizeLocale((await cookies()).get("booking_locale")?.value)',1)
old='<Topbar info={shell} now={shell.now} simulated={shell.simulated} />'
assert old in s,"Topbar render changed"
s=s.replace(old,'<Topbar info={shell} now={shell.now} simulated={shell.simulated} initialLocale={initialLocale} />',1)
old='<MobileNav info={shell} />'
assert old in s,"Mobile navigation render changed"
s=s.replace(old,'<MobileNav info={shell} initialLocale={initialLocale} />',1)
layout.write_text(s,encoding="utf-8")

top=root/"components/shell/topbar.tsx"
s=top.read_text(encoding="utf-8")
s=s.replace('"use client"','"use client"\nimport { normalizeLocale, translateText, type Locale } from "@/i18n/messages"',1)
old='export function Topbar({ info, now, simulated }: { info: ShellInfo; now: string; simulated: boolean }) {'
new='export function Topbar({ info, now, simulated, initialLocale }: { info: ShellInfo; now: string; simulated: boolean; initialLocale: Locale }) {'
assert old in s,"Topbar props changed"
s=s.replace(old,new,1)
anchor='  const pathname = usePathname()'
assert anchor in s
state='''  const [locale,setLocale]=useState<Locale>(initialLocale)
  useEffect(()=>{
    const sync=()=>setLocale(normalizeLocale(localStorage.getItem("booking_locale")||document.documentElement.lang||initialLocale))
    window.addEventListener("booking:locale",sync)
    return ()=>window.removeEventListener("booking:locale",sync)
  },[initialLocale])
'''
s=s.replace(anchor,anchor+'\n'+state,1)
old='{title}</span>'
assert old in s,"Topbar title changed"
s=s.replace(old,'{translateText(title,locale)}</span>',1)
s=s.replace('<span className="font-display text-[15px] text-ivory lg:hidden">','<span data-i18n-skip="true" className="font-display text-[15px] text-ivory lg:hidden">',1)
top.write_text(s,encoding="utf-8")

nav=root/"components/shell/mobile-nav.tsx"
s=nav.read_text(encoding="utf-8")
assert 'import { useState } from "react"' in s
s=s.replace('import { useState } from "react"','import { useEffect, useState } from "react"',1)
s=s.replace('"use client"','"use client"\nimport { normalizeLocale, type Locale } from "@/i18n/messages"',1)
old='export function MobileNav({ info }: { info: ShellInfo }) {'
new='export function MobileNav({ info, initialLocale }: { info: ShellInfo; initialLocale: Locale }) {'
assert old in s,"MobileNav props changed"
s=s.replace(old,new,1)
anchor='  const pathname = usePathname()'
assert anchor in s
state='''  const [locale,setLocale]=useState<Locale>(initialLocale)
  useEffect(()=>{
    const sync=()=>setLocale(normalizeLocale(localStorage.getItem("booking_locale")||document.documentElement.lang||initialLocale))
    window.addEventListener("booking:locale",sync)
    return ()=>window.removeEventListener("booking:locale",sync)
  },[initialLocale])
  const labels={
    en:{today:"Today",schedule:"Schedule",inbox:"Inbox",more:"More",moreSections:"More sections",signOut:"Sign out"},
    de:{today:"Heute",schedule:"Kalender",inbox:"Posteingang",more:"Mehr",moreSections:"Weitere Bereiche",signOut:"Abmelden"},
    uk:{today:"Сьогодні",schedule:"Календар",inbox:"Вхідні",more:"Ще",moreSections:"Інші розділи",signOut:"Вийти"},
  }[locale]
'''
s=s.replace(anchor,anchor+'\n'+state,1)
patterns=[
(r'(href="/"\s+label=)"[^"]+"',r'\g<1>{labels.today}'),
(r'(href="/agenda"\s+label=)"[^"]+"',r'\g<1>{labels.schedule}'),
(r'(href="/bandeja"\s+label=)"[^"]+"',r'\g<1>{labels.inbox}'),
]
for pattern,target in patterns:
    s,n=re.subn(pattern,target,s,count=1)
    if n!=1:raise RuntimeError("Mobile navigation tab "+pattern+" missing")
# Ensure the locale-controlled React-owned footer texts are not mutated by the DOM bridge.
s=s.replace('''        {label}
        {badge > 0''','''        <span data-i18n-skip="true">{label}</span>
        {badge > 0''',1)
s,n=re.subn(r'(\s*)(?:More|Más)(\s*</button>)',r'\1<span data-i18n-skip="true">{labels.more}</span>\2',s,count=1)
if n!=1:raise RuntimeError("More button title missing")
s,n=re.subn(r'(<SheetTitle[^>]*>)(?:More sections|Más secciones)(</SheetTitle>)',r'\1{labels.moreSections}\2',s,count=1)
if n!=1:raise RuntimeError("More sheet heading missing")
s,n=re.subn(r'(</LogOut>|/>)(?:\s*)(?:Sign out|Salir del panel|Log out)(\s*</button>)',r'\1 <span data-i18n-skip="true">{labels.signOut}</span>\2',s,count=1)
if n!=1:raise RuntimeError("Log out footer title missing")
nav.write_text(s,encoding="utf-8")

page=root/"app/(panel)/clientes/page.tsx"
s=page.read_text(encoding="utf-8")
# Unicode-safe, exact template replacement; do not alter customer names.
old='${d.rows.length} клієнтів · ${frequent} постійних'
new='${d.rows.length} ${d.rows.length%100>=11&&d.rows.length%100<=14?"клієнтів":d.rows.length%10===1?"клієнт":d.rows.length%10>=2&&d.rows.length%10<=4?"клієнти":"клієнтів"} · ${frequent} постійних'
assert old in s,"Ukrainian client count summary not found"
s=s.replace(old,new,1)
page.write_text(s,encoding="utf-8")
print("BOOKING_SHELL_REACT_NATIVE_LOCALES_AND_CLIENT_PLURALS_OK")
