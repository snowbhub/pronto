from pathlib import Path
import re, json
ROOT = Path('/app')
BUNDLE = Path('/tmp/booking-patch')
ROWS = []
for p in sorted(BUNDLE.glob('rows*.json')):
    ROWS.extend(json.loads(p.read_text(encoding='utf-8')))
ROWS = [tuple(x) for x in ROWS]
ROWS.sort(key=lambda x: len(x[0]), reverse=True)

def english_source(s: str) -> str:
    for es, en, _, _ in ROWS:
        s = s.replace(json.dumps(es, ensure_ascii=False), json.dumps(en, ensure_ascii=False))
        if "'" not in es and "'" not in en:
            s = s.replace("'" + es + "'", "'" + en + "'")
        s = s.replace('>' + es + '<', '>' + en + '<')
        # Long phrases are safe to normalize inside template literals and split JSX text.
        if len(es) >= 6 and (' ' in es or any(ch in es for ch in ".,!?¿¡:;—")):
            s = s.replace(es, en)
    s = s.replace('Virex Barber Shop', 'Booking').replace('VIREX', 'BOOKING').replace('Virex', 'Booking')
    s = s.replace('virex.ar/reservar', '/reservar').replace('@virex_barbershop', '@booking')
    return s

for p in list((ROOT/'src').rglob('*.ts')) + list((ROOT/'src').rglob('*.tsx')):
    old = p.read_text(encoding='utf-8')
    new = english_source(old)
    if new != old:
        p.write_text(new, encoding='utf-8')

(ROOT/'src/config/brand.ts').write_text('''/** Product / tenant defaults. */
export const BRAND = {
  name: "Booking",
  fullName: "Booking",
  tagline: "Appointments made simple",
  claim: "Simple. Clear. On time.",
  address: "Your business address",
  city: "",
  timezone: "America/Argentina/Buenos_Aires",
  currency: "ARS",
  instagram: "",
  whatsappLink: "#",
  openingHours: { days: [2,3,4,5,6], open: "11:00", close: "20:00" },
  booking: { slotStepMin: 60 },
  loyalty: { stampsRequired: 5, rewardDiscountPct: 50 },
} as const
export type Brand = typeof BRAND
''', encoding='utf-8')

(ROOT/'src/components/brand/virex-mark.tsx').write_text(r'''"use client"
import { cn } from "@/lib/utils"
export function BookingMark({ size=32, className, title="Booking" }: { size?:number; detail?:boolean; animated?:boolean; className?:string; title?:string }) {
  return <svg viewBox="0 0 64 64" width={size} height={size} role="img" aria-label={title} className={cn("shrink-0 text-ivory",className)} fill="none">
    <rect x="7" y="9" width="50" height="48" rx="13" stroke="currentColor" strokeWidth="3"/>
    <path d="M18 5v10M46 5v10M8.5 23h47" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>
    <path d="m22 39 7 7 14-17" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
}
''', encoding='utf-8')

p = ROOT/'src/app/(panel)/layout.tsx'
s = p.read_text(encoding='utf-8').replace('import { IntroOverlay } from "@/components/brand/intro"\n','').replace('      <IntroOverlay />\n','')
p.write_text(s,encoding='utf-8')
for rel in ['src/components/shell/sidebar.tsx','src/app/login/page.tsx','src/app/reservar/page.tsx']:
    p=ROOT/rel
    s=p.read_text(encoding='utf-8')
    s=re.sub(r'import \{ OperonBadge \} from "@/components/brand/operon-badge"\n','',s)
    s=re.sub(r'\s*<OperonBadge(?:\s+className="[^"]*")?\s*/>','',s)
    s=s.replace('>BOOKING<','>Booking<').replace('text-gold-metal','text-ivory')
    p.write_text(s,encoding='utf-8')

(ROOT/'src/components/shell/nav.ts').write_text(r'''import { Bot, CalendarDays, ChartNoAxesColumn, House, MessagesSquare, Settings2, Users, Wallet, type LucideIcon } from "lucide-react"
export interface NavItem { href:string; label:string; icon:LucideIcon; badge?:"unread"|"agent" }
export const NAV:{group:string;items:NavItem[]}[]=[
  {group:"Daily",items:[{href:"/",label:"Today",icon:House},{href:"/agenda",label:"Schedule",icon:CalendarDays},{href:"/bandeja",label:"Inbox",icon:MessagesSquare,badge:"unread"},{href:"/clientes",label:"Clients",icon:Users}]},
  {group:"Finance",items:[{href:"/caja",label:"Cash",icon:Wallet},{href:"/finanzas",label:"Finance",icon:ChartNoAxesColumn}]},
  {group:"Automation",items:[{href:"/agente",label:"AI Agent",icon:Bot,badge:"agent"}]},
]
export const SETTINGS_ITEM:NavItem={href:"/ajustes",label:"Settings",icon:Settings2}
export function isActive(pathname:string,href:string){return href==="/"?pathname==="/":pathname===href||pathname.startsWith(href+"/")}
''',encoding='utf-8')

pt=ROOT/'src/lib/time.ts'
s=pt.read_text(encoding='utf-8')
s=s.replace('"es-AR"','"en-GB"')
s=s.replace('export const WEEKDAY_SHORT = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]','export const WEEKDAY_SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]')
s=s.replace('return "ahora"','return "now"').replace('return ' + chr(96) + 'hace $' + '{diffMin} min' + chr(96), 'return String(diffMin) + " min ago"').replace('return "ayer"','return "yesterday"')
pt.write_text(s,encoding='utf-8')

idir=ROOT/'src/i18n'; idir.mkdir(parents=True,exist_ok=True)
rows=[{'es':es,'en':en,'de':de,'uk':uk} for es,en,de,uk in ROWS]
(idir/'messages.ts').write_text('export type Locale = "en" | "de" | "uk"\nexport const SUPPORTED_LOCALES:Locale[]=["en","de","uk"]\nexport const ROWS='+json.dumps(rows,ensure_ascii=False,indent=2)+' as const\n'+r'''
export function normalizeLocale(value:string|null|undefined):Locale{const v=(value||"").toLowerCase();if(v.startsWith("de"))return"de";if(v.startsWith("uk")||v.startsWith("ua"))return"uk";return"en"}
export function translateText(value:string,locale:Locale):string{let out=value;for(const row of ROWS)if(out.includes(row.es))out=out.split(row.es).join(row.en);if(locale==="en")return out;const sorted=[...ROWS].sort((a,b)=>b.en.length-a.en.length);for(const row of sorted){const target=locale==="de"?row.de:row.uk;if(out.includes(row.en))out=out.split(row.en).join(target)}return out}
''',encoding='utf-8')

(idir/'bridge.tsx').write_text(r'''"use client"
import { useEffect } from "react"
import { normalizeLocale, translateText, type Locale } from "./messages"
const ATTRS=["aria-label","title","placeholder"] as const
function selectedLocale():Locale{try{const s=localStorage.getItem("booking_locale");if(s)return normalizeLocale(s)}catch{}const c=document.cookie.match(/(?:^|;\s*)booking_locale=([^;]+)/)?.[1];if(c)return normalizeLocale(decodeURIComponent(c));return normalizeLocale(navigator.language)}
function apply(root:ParentNode,locale:Locale){const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n:Node|null;while((n=walker.nextNode())){const p=n.parentElement;if(!p||["SCRIPT","STYLE","CODE","PRE"].includes(p.tagName))continue;const v=n.nodeValue||"";if(!v.trim())continue;const x=translateText(v,locale);if(x!==v)n.nodeValue=x}if("querySelectorAll" in root)(root as ParentNode).querySelectorAll<HTMLElement>("*").forEach(el=>ATTRS.forEach(a=>{const v=el.getAttribute(a);if(v)el.setAttribute(a,translateText(v,locale))}))}
export function LocaleBridge(){useEffect(()=>{const l=selectedLocale();document.documentElement.lang=l;apply(document.documentElement,l);const o=new MutationObserver(rs=>{for(const r of rs){if(r.type==="characterData"&&r.target.parentNode)apply(r.target.parentNode,l);for(const n of r.addedNodes){if(n instanceof Element)apply(n,l);else if(n.parentNode)apply(n.parentNode,l)}}});o.observe(document.documentElement,{subtree:true,childList:true,characterData:true});return()=>o.disconnect()},[]);return null}
''',encoding='utf-8')

(idir/'controls.tsx').write_text(r'''"use client"
import { useEffect,useState } from "react"
import { Languages,Moon,Sun } from "lucide-react"
import { normalizeLocale,type Locale } from "./messages"
type Theme="dark"|"light"
function localeNow():Locale{return typeof window==="undefined"?"en":normalizeLocale(localStorage.getItem("booking_locale")||navigator.language)}
function themeNow():Theme{if(typeof window==="undefined")return"dark";const x=localStorage.getItem("booking_theme");if(x==="dark"||x==="light")return x;return matchMedia("(prefers-color-scheme: light)").matches?"light":"dark"}
export function LocaleThemeControls(){const[locale,setLocale]=useState<Locale>("en");const[theme,setTheme]=useState<Theme>("dark");useEffect(()=>{setLocale(localeNow());setTheme(themeNow())},[]);const choose=(x:Locale)=>{localStorage.setItem("booking_locale",x);document.cookie="booking_locale="+x+"; Path=/; Max-Age=31536000; SameSite=Lax";location.reload()};const toggle=()=>{const x:Theme=theme==="dark"?"light":"dark";setTheme(x);localStorage.setItem("booking_theme",x);document.documentElement.dataset.theme=x;document.documentElement.classList.toggle("dark",x==="dark")};return <div className="fixed right-3 bottom-20 z-[90] flex items-center gap-1 rounded-xl border border-line-strong bg-surface-1/95 p-1 shadow-lg backdrop-blur lg:right-5 lg:bottom-5"><span className="grid size-8 place-items-center text-ivory-3" aria-hidden><Languages className="size-4"/></span>{(["en","de","uk"] as Locale[]).map(x=><button key={x} type="button" onClick={()=>choose(x)} aria-label={"Language "+x.toUpperCase()} className={"h-8 rounded-lg px-2 text-[11px] font-semibold tracking-wide transition-colors "+(locale===x?"bg-ivory text-obsidian":"text-ivory-2 hover:bg-surface-3 hover:text-ivory")}>{x==="uk"?"UA":x.toUpperCase()}</button>)}<span className="mx-0.5 h-5 w-px bg-line-strong"/><button type="button" onClick={toggle} aria-label={theme==="dark"?"Use light theme":"Use dark theme"} title={theme==="dark"?"Light theme":"Dark theme"} className="grid size-8 place-items-center rounded-lg text-ivory-2 transition-colors hover:bg-surface-3 hover:text-ivory">{theme==="dark"?<Sun className="size-4"/>:<Moon className="size-4"/>}</button></div>}
''',encoding='utf-8')

(ROOT/'public/booking-boot.js').write_text(r'''(()=>{try{const s=localStorage.getItem("booking_theme"),t=s==="light"||s==="dark"?s:(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark");document.documentElement.dataset.theme=t;document.documentElement.classList.toggle("dark",t==="dark");const a=localStorage.getItem("booking_locale"),c=document.cookie.match(/(?:^|;\s*)booking_locale=([^;]+)/)?.[1],r=a||(c?decodeURIComponent(c):navigator.language),l=/^de/i.test(r)?"de":/^(uk|ua)/i.test(r)?"uk":"en";document.documentElement.dataset.locale=l;document.documentElement.lang=l}catch{document.documentElement.dataset.theme="dark";document.documentElement.classList.add("dark")}})();''',encoding='utf-8')

(ROOT/'src/app/layout.tsx').write_text(r'''import type { Metadata,Viewport } from "next"
import { Archivo } from "next/font/google"
import { Toaster } from "@/components/ui/sonner"
import { TooltipProvider } from "@/components/ui/tooltip"
import { LocaleBridge } from "@/i18n/bridge"
import { LocaleThemeControls } from "@/i18n/controls"
import "./globals.css"
const archivo=Archivo({subsets:["latin","latin-ext"],axes:["wdth"],variable:"--font-archivo",display:"swap"})
export const metadata:Metadata={title:{default:"Booking · Panel",template:"%s · Booking"},description:"Booking — appointments, clients, cash and automation.",robots:{index:false,follow:false}}
export const viewport:Viewport={themeColor:[{media:"(prefers-color-scheme: dark)",color:"#050505"},{media:"(prefers-color-scheme: light)",color:"#ffffff"}]}
export default function RootLayout({children}:LayoutProps<"/">){return <html lang="en" className={archivo.variable+" h-full"} suppressHydrationWarning><head><script src="/booking-boot.js"/></head><body className="min-h-full"><TooltipProvider>{children}</TooltipProvider><LocaleBridge/><LocaleThemeControls/><Toaster position="bottom-right"/></body></html>}
''',encoding='utf-8')

css=ROOT/'src/app/globals.css'
css.write_text(css.read_text(encoding='utf-8')+r'''

/* BOOKING — neutral black/white visual system. */
:root,html[data-theme="dark"]{--obsidian:#050505;--surface-1:#0d0d0d;--surface-2:#151515;--surface-3:#202020;--line:rgb(255 255 255/.08);--line-strong:rgb(255 255 255/.16);--ivory:#fff;--ivory-2:#cfcfcf;--ivory-3:#8f8f8f;--gold:#fff;--gold-bright:#fff;--gold-deep:#9d9d9d;--gold-metal:linear-gradient(135deg,#777,#f5f5f5 45%,#fff 52%,#bdbdbd);--background:var(--obsidian);--foreground:var(--ivory);--card:var(--surface-1);--card-foreground:var(--ivory);--popover:var(--surface-2);--popover-foreground:var(--ivory);--primary:var(--ivory);--primary-foreground:var(--obsidian);--secondary:var(--surface-3);--secondary-foreground:var(--ivory);--muted:var(--surface-2);--muted-foreground:var(--ivory-3);--accent:var(--surface-3);--accent-foreground:var(--ivory);--border:var(--line);--input:var(--line-strong);--ring:rgb(255 255 255/.45);--chart-1:#fff;--chart-2:#c7c7c7;--chart-3:#8c8c8c;--chart-5:#5a5a5a;color-scheme:dark}
html[data-theme="light"]{--obsidian:#fff;--surface-1:#fafafa;--surface-2:#f2f2f2;--surface-3:#e8e8e8;--line:rgb(0 0 0/.08);--line-strong:rgb(0 0 0/.16);--ivory:#0a0a0a;--ivory-2:#363636;--ivory-3:#6f6f6f;--gold:#0a0a0a;--gold-bright:#000;--gold-deep:#585858;--gold-metal:linear-gradient(135deg,#777,#1d1d1d 45%,#000 52%,#555);--background:var(--obsidian);--foreground:var(--ivory);--card:var(--surface-1);--card-foreground:var(--ivory);--popover:#fff;--popover-foreground:var(--ivory);--primary:#0a0a0a;--primary-foreground:#fff;--secondary:var(--surface-3);--secondary-foreground:var(--ivory);--muted:var(--surface-2);--muted-foreground:var(--ivory-3);--accent:var(--surface-3);--accent-foreground:var(--ivory);--border:var(--line);--input:var(--line-strong);--ring:rgb(0 0 0/.3);--chart-1:#0a0a0a;--chart-2:#444;--chart-3:#777;--chart-5:#aaa;color-scheme:light}
html[data-theme="light"] .bg-obsidian\/85{background-color:rgb(255 255 255/.88)}
html[data-theme="light"] .bg-\[\#1d1a14\]{background-color:#f4f4f4}
''',encoding='utf-8')

(ROOT/'src/app/icon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#050505"/><rect x="10" y="13" width="44" height="41" rx="11" fill="none" stroke="#fff" stroke-width="3"/><path d="M20 9v10M44 9v10M11 25h42" stroke="#fff" stroke-width="3" stroke-linecap="round"/><path d="m23 40 6 6 13-16" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>''',encoding='utf-8')

p=ROOT/'src/lib/agent/prompt.ts'
s=p.read_text(encoding='utf-8')
s=re.sub(r'const TONE:[\s\S]*?\n}\n\nexport function buildSystemPrompt', '''const TONE: Record<AgentSettings["tone"], string> = {
  cercano: "Friendly, warm and concise.",
  profesional: "Professional, clear and polite without sounding cold.",
  canchero: "Relaxed and natural, but still respectfulful and concise.",
}

export function buildSystemPrompt''', s, count=1)
s=s.replace('# How you speak', '# Supported languages\nOnly Ukrainian, German and English are supported. Reply in the customer’s language when it is one of these three. If the language is unclear or unsupported, use English. Do not mix languages unless asked to translate.\n\n# How you speak')
s=s.replace('# Cómo hablás', '# Supported languages\nOnly Ukrainian, German and English are supported. Reply in the customer’s language when it is one of these three. If the language is unclear or unsupported, use English. Do not mix languages unless asked to translate.\n\n# How you speak')
p.write_text(english_source(s),encoding='utf-8')

markers=re.compile(r'[¿¡áéíóúñü]|\b(?:turno|turnos|barbero|barberos|cliente|clientes|caja|finanzas|ajustes|bandeja|agente|fidelidad|gasto|gastos|seña|guardar|elegí|revisá|dueño|hoy|mañana|servicio|servicios|efectivo|transferencia|propina|horario|semana|mes)\b',re.I)
res=[]
for p in list((ROOT/'src').rglob('*.tsx'))+list((ROOT/'src').rglob('*.ts')):
    for i,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if markers.search(line) and any(x in line for x in ['"',"'",'>','<']):
            res.append(f'{p.relative_to(ROOT)}:{i}: {line.strip()[:220]}')
print(f'BOOKING_REBRAND_APPLIED rows={len(ROWS)} residual_candidates={len(res)}')
for x in res[:260]: print('I18N_RESIDUAL',x)
