from pathlib import Path
p=Path("/app/src/i18n/controls.tsx")
p.write_text(r'''"use client"
import { useEffect, useState } from "react"
import { createPortal } from "react-dom"
import { usePathname, useRouter } from "next/navigation"
import { Moon, Sun, ChevronDown } from "lucide-react"
import { normalizeLocale, type Locale } from "./messages"

type Theme = "dark" | "light"

function readLocale(): Locale {
  try {
    return normalizeLocale(localStorage.getItem("booking_locale") ||
      document.cookie.match(/(?:^|;\s*)booking_locale=([^;]+)/)?.[1] ||
      navigator.language)
  } catch { return "en" }
}
function readTheme(): Theme {
  try {
    const chosen = localStorage.getItem("booking_theme")
    if (chosen === "dark" || chosen === "light") return chosen
    return matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"
  } catch { return "dark" }
}

export function LocaleThemeControls() {
  const pathname = usePathname()
  const router = useRouter()
  const [target, setTarget] = useState<HTMLElement | null>(null)
  const [locale, setLocale] = useState<Locale>("en")
  const [theme, setTheme] = useState<Theme>("dark")
  useEffect(() => { setLocale(readLocale()); setTheme(readTheme()) }, [])
  useEffect(() => {
    const header = document.getElementById("booking-header-actions") ||
      document.getElementById("booking-public-header-actions")
    setTarget(header)
  }, [pathname])
  function choose(next: Locale) {
    setLocale(next)
    localStorage.setItem("booking_locale", next)
    document.cookie = "booking_locale=" + next + "; Path=/; Max-Age=31536000; SameSite=Lax"
    document.documentElement.dataset.locale = next
    document.documentElement.lang = next
    window.dispatchEvent(new Event("booking:locale"))
    // The client directory has server-provided React translations, not DOM replacements.
    if (pathname === "/clientes") router.refresh()
  }
  function toggle() {
    const next: Theme = theme === "dark" ? "light" : "dark"
    setTheme(next)
    localStorage.setItem("booking_theme", next)
    document.documentElement.dataset.theme = next
    document.documentElement.classList.toggle("dark", next === "dark")
  }
  const controls = <div aria-label="Language and appearance" className={
    (target ? "relative z-30" : "fixed right-3 top-3 z-[90]") +
    " flex h-10 shrink-0 items-center gap-1 rounded-xl border border-line-strong bg-surface-1/95 px-1.5 shadow-sm backdrop-blur"
  }>
    <label className="relative flex h-9 items-center" aria-label="Interface language">
      <select aria-label="Interface language" value={locale} onChange={event=>choose(event.target.value as Locale)}
        className="h-9 w-[48px] cursor-pointer appearance-none rounded-lg bg-transparent pl-1.5 pr-3 text-xs font-semibold text-ivory outline-none focus-visible:ring-2 focus-visible:ring-ivory-2">
        {(["en","de","uk"] as Locale[]).map(code=><option key={code} value={code}>{code==="uk"?"UA":code.toUpperCase()}</option>)}
      </select>
      <ChevronDown aria-hidden className="pointer-events-none absolute right-0 top-3 size-3 text-ivory-3"/>
    </label>
    <span aria-hidden className="h-5 w-px bg-line-strong"/>
    <button type="button" aria-label={theme==="dark"?"Use light theme":"Use dark theme"}
      onClick={toggle} className="grid size-8 place-items-center rounded-lg text-ivory-2 hover:bg-surface-3">
      {theme==="dark"?<Sun className="size-4"/>:<Moon className="size-4"/>}
    </button>
  </div>
  return target ? createPortal(controls,target) : controls
}
''',encoding="utf-8")
print("BOOKING_HEADER_LOCALE_PORTAL_INSTALLED")
