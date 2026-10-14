from pathlib import Path
p=Path("/app/src/i18n/controls.tsx")
p.write_text(r'''"use client"
import { useEffect, useState } from "react"
import { createPortal } from "react-dom"
import { usePathname } from "next/navigation"
import { Moon, Sun } from "lucide-react"
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
  }
  function toggle() {
    const next: Theme = theme === "dark" ? "light" : "dark"
    setTheme(next)
    localStorage.setItem("booking_theme", next)
    document.documentElement.dataset.theme = next
    document.documentElement.classList.toggle("dark", next === "dark")
  }
  const controls = <div aria-label="Language and appearance" className={
    (target ? "relative z-40" : "fixed right-3 top-3 z-[90]") +
    " flex h-10 shrink-0 items-center gap-0.5 rounded-full border border-line-strong bg-surface-1/95 p-1 shadow-sm backdrop-blur"
  }>
    {(["uk","de","en"] as Locale[]).map(code =>
      <button key={code} type="button" aria-label={"Language " + code.toUpperCase()}
        aria-pressed={locale===code} onClick={()=>choose(code)}
        className={"grid h-8 min-w-7 place-items-center rounded-full px-1.5 text-[11px] font-semibold transition-colors "+
          (locale===code ? "bg-ivory text-obsidian" : "text-ivory-2 hover:bg-surface-3")}>
        {code === "uk" ? "UA" : code.toUpperCase()}
      </button>
    )}
    <span aria-hidden className="mx-0.5 h-5 w-px bg-line-strong"/>
    <button type="button" aria-label={theme==="dark"?"Use light theme":"Use dark theme"}
      onClick={toggle} className="grid size-8 place-items-center rounded-full text-ivory-2 hover:bg-surface-3">
      {theme==="dark"?<Sun className="size-4"/>:<Moon className="size-4"/>}
    </button>
  </div>
  return target ? createPortal(controls,target) : controls
}
''',encoding="utf-8")
print("BOOKING_HEADER_LOCALE_PORTAL_INSTALLED")
