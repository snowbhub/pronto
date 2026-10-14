from pathlib import Path
p=Path("/app/src/i18n/controls.tsx")
s=p.read_text(encoding="utf-8")
a='import { useEffect,useState } from "react"'
if a not in s:raise RuntimeError("controls import changed")
s=s.replace(a,a+'\nimport { createPortal } from "react-dom"\nimport { usePathname } from "next/navigation"')
a='export function LocaleThemeControls(){const[locale,setLocale]'
b='export function LocaleThemeControls(){const pathname=usePathname();const[target,setTarget]=useState<HTMLElement|null>(null);const[locale,setLocale]'
if a not in s:raise RuntimeError("controls hook signature changed")
s=s.replace(a,b)
a='useEffect(()=>{setLocale(localeNow());setTheme(themeNow())},[]);'
b='useEffect(()=>{setLocale(localeNow());setTheme(themeNow())},[]);useEffect(()=>{setTarget(document.getElementById("booking-header-actions")||document.getElementById("booking-public-header-actions"))},[pathname]);'
if a not in s:raise RuntimeError("controls effect not found")
s=s.replace(a,b)
a='document.cookie="booking_locale="+x+"; Path=/; Max-Age=31536000; SameSite=Lax";'
if a not in s:raise RuntimeError("locale chooser absent")
s=s.replace(a,a+'setLocale(x);')
a='return <div className="fixed right-3 top-3 z-[90] flex items-center gap-0.5 rounded-full border border-line-strong bg-surface-1/95 p-1 shadow-lg backdrop-blur"'
b='const content=<div className={(target?"relative z-40":"fixed right-3 top-3 z-[90]")+" flex items-center gap-0.5 rounded-full border border-line-strong bg-surface-1/95 p-1 shadow-lg backdrop-blur"}'
if a not in s:raise RuntimeError("controls class did not match final patch")
s=s.replace(a,b)
if not s.endswith("</div>}\n"):raise RuntimeError("Unexpected JSX controls ending")
s=s[:-len('</div>}\n')]+'</div>;return target?createPortal(content,target):content}\n'
p.write_text(s,encoding="utf-8")
print("BOOKING_CONTROLS_ANCHORED_IN_HEADER", "createPortal" in s)
