from pathlib import Path
import re

ROOT = Path("/app")

def edit(rel: str, old: str, new: str, label: str, count: int = 1):
    path = ROOT / rel
    body = path.read_text(encoding="utf-8")
    if old not in body:
        raise RuntimeError(f"{label}: source anchor missing in {rel}")
    path.write_text(body.replace(old, new, count), encoding="utf-8")

# Keep the root render lightweight: it only needs the two settings used by
# runtime date and money formatting. The previous root layout loaded the full
# multi-month snapshot before every route, even pages with narrow queries.
edit("src/lib/domain/types.ts", "  timezone: string\n}", "  timezone: string\n  currency: CurrencyCode\n}", "shop currency type")
edit("src/lib/domain/types.ts", "export interface ShopSettings {", 'export type CurrencyCode = "EUR" | "UAH" | "USD" | "ARS"\n\nexport interface ShopSettings {', "currency type")
edit("src/lib/data/store/types.ts", "  shellSummary?(): Promise<{ unread: number; needsHuman: number; agentEnabled: boolean }>\n", "  shellSummary?(): Promise<{ unread: number; needsHuman: number; agentEnabled: boolean }>\n  runtimeSettings?(): Promise<{ timezone: string; currency: import(\"@/lib/domain/types\").CurrencyCode; depositEnabled: boolean }>\n", "runtime settings interface")
edit("src/lib/data/seed.ts", 'slotStepMin: 60, timezone: "Europe/Berlin",', 'slotStepMin: 60, timezone: "Europe/Berlin", currency: "ARS",', "demo currency default")
edit("src/lib/data/store/memory.ts", '  async now() {\n    const s = state()', '  async runtimeSettings() {\n    const settings = state().shopSettings\n    return { timezone: settings.timezone || "Europe/Berlin", currency: settings.currency || "ARS", depositEnabled: settings.depositEnabled }\n  },\n\n  async now() {\n    const s = state()', "memory runtime settings")
edit("src/lib/data/store/postgres.ts", '  async shellSummary() {\n', '  async runtimeSettings() {\n    const sql = sqlClient()\n    const rows = await sql`select timezone, currency_code, deposit_enabled from shop_settings where id=1`\n    return { timezone: String(rows[0]?.timezone ?? "Europe/Berlin"), currency: String(rows[0]?.currency_code ?? "ARS") as import("@/lib/domain/types").CurrencyCode, depositEnabled: Boolean(rows[0]?.deposit_enabled) }\n  },\n\n  async shellSummary() {\n', "postgres runtime settings")
edit("src/lib/data/store/postgres.ts", 'timezone:String(shop.timezone??"Europe/Berlin"),calendarOpen:', 'timezone:String(shop.timezone??"Europe/Berlin"),currency:String(shop.currency_code??"ARS") as import("@/lib/domain/types").CurrencyCode,calendarOpen:', "agenda currency map")
edit("src/lib/data/store/postgres.ts", '        timezone: String(shop[0].timezone ?? "Europe/Berlin"),', '        timezone: String(shop[0].timezone ?? "Europe/Berlin"),\n        currency: String(shop[0].currency_code ?? "ARS") as import("@/lib/domain/types").CurrencyCode,', "snapshot currency map")
edit("src/lib/data/store/postgres.ts", '    if (patch.timezone !== undefined) row.timezone = patch.timezone', '    if (patch.timezone !== undefined) row.timezone = patch.timezone\n    if (patch.currency !== undefined) row.currency_code = patch.currency', "currency write")

edit("src/lib/data/repo.ts", 'export async function now(): Promise<Date> {', '''let runtimeSettingsCache: { value: { timezone: string; currency: import("@/lib/domain/types").CurrencyCode; depositEnabled: boolean }; expiresAt: number } | null = null

export function clearRuntimeSettingsCache() {
  runtimeSettingsCache = null
}

export async function runtimeSettings() {
  if (runtimeSettingsCache && runtimeSettingsCache.expiresAt > Date.now()) {
    setTimeZone(runtimeSettingsCache.value.timezone || "Europe/Berlin")
    return runtimeSettingsCache.value
  }
  await connection()
  const repository = store()
  const settings = repository.runtimeSettings
    ? await repository.runtimeSettings()
    : (await db()).shopSettings
  setTimeZone(settings.timezone || "Europe/Berlin")
  runtimeSettingsCache = { value: settings, expiresAt: Date.now() + 5 * 60 * 1000 }
  return settings
}

export async function now(): Promise<Date> {'''.replace("+", ""), "fast runtime settings helper")

edit("src/lib/data/settings-actions.ts", 'import { db, now, store } from "./repo"', 'import { clearRuntimeSettingsCache, db, now, store } from "./repo"', "runtime cache invalidation import")
edit("src/lib/data/settings-actions.ts", 'const refresh = () => revalidatePath("/", "layout")', 'const refresh = () => { clearRuntimeSettingsCache(); revalidatePath("/", "layout") }', "runtime cache invalidation on settings save")

# Carry the persisted currency and current language into both server and client
# formatting. The function name stays as a compatibility alias for upstream UI.
money = ROOT / "src/lib/money.ts"
body = money.read_text(encoding="utf-8")
start = body.index('const ars = new Intl.NumberFormat')
stop = body.index('/** Upstream implementation note. */\nexport function formatNumber', start)
body = body[:start] + '''import type { CurrencyCode } from "@/lib/domain/types"
import type { Locale } from "@/i18n/messages"

const LOCALES: Record<Locale, string> = { en: "en-GB", de: "de-DE", uk: "uk-UA" }
const plain = () => new Intl.NumberFormat(LOCALES[currentLocale()], { maximumFractionDigits: 0 })
const CURRENCIES: readonly CurrencyCode[] = ["EUR", "UAH", "USD", "ARS"]
let serverCurrency: CurrencyCode = "ARS"
let serverLocale: Locale = "en"

function validCurrency(value: string | undefined): CurrencyCode {
  return CURRENCIES.includes(value as CurrencyCode) ? value as CurrencyCode : "ARS"
}
function currentCurrency(): CurrencyCode {
  if (typeof document !== "undefined") return validCurrency(document.documentElement.dataset.currency || undefined)
  return serverCurrency
}
function currentLocale(): Locale {
  if (typeof document !== "undefined") {
    const value = document.documentElement.dataset.locale
    if (value === "de" || value === "uk" || value === "en") return value
  }
  return serverLocale
}
export function configureMoney(currency: CurrencyCode, locale: Locale): void {
  serverCurrency = validCurrency(currency)
  serverLocale = locale
}
export function currencySymbol(currency: CurrencyCode, locale: Locale = "en"): string {
  return new Intl.NumberFormat(LOCALES[locale], { style: "currency", currency, currencyDisplay: "narrowSymbol", maximumFractionDigits: 0 }).formatToParts(0).find((part) => part.type === "currency")?.value || currency
}

/** Compatibility name retained for existing screens; formats in the shop's configured currency. */
export function formatARS(amount: number): string {
  return new Intl.NumberFormat(LOCALES[currentLocale()], { style: "currency", currency: currentCurrency(), maximumFractionDigits: 2 }).format(Number.isFinite(amount) ? amount : 0)
}

''' + body[stop:]
body = body.replace('const plain = new Intl.NumberFormat("es-AR", { maximumFractionDigits: 0 })', 'const plain = () => new Intl.NumberFormat(LOCALES[currentLocale()], { maximumFractionDigits: 0 })')
body = body.replace('return plain.format(Math.round(amount))', 'return plain().format(Math.round(amount))')
body = body.replace('return `$${(amount / 1_000_000).toLocaleString("es-AR", { maximumFractionDigits: 1 })}M`', 'return `${currencySymbol(currentCurrency(), currentLocale())}${(amount / 1_000_000).toLocaleString(LOCALES[currentLocale()], { maximumFractionDigits: 1 })}M`')
body = body.replace('return `$${Math.round(amount / 1_000)}k`', 'return `${currencySymbol(currentCurrency(), currentLocale())}${Math.round(amount / 1_000)}k`')
body = body.replace('return `$${amount}`', 'return `${currencySymbol(currentCurrency(), currentLocale())}${amount}`')
money.write_text(body, encoding="utf-8")

# Validate only explicit ISO codes from the supported set; no arbitrary Intl
# locale/currency values are accepted from a form submission.
actions = ROOT / "src/lib/data/settings-actions.ts"
body = actions.read_text(encoding="utf-8")
body = body.replace('export async function saveShopSettings(input: { openingCash: number }): Promise<Result> {', 'export async function saveShopSettings(input: { openingCash?: number; currency?: string }): Promise<Result> {')
old = '''  const openingCash = Math.round(Number(input.openingCash))
  if (!Number.isFinite(openingCash) || openingCash < 0 || openingCash > 10_000_000) return { ok: false, error: "Check the amount." }
  await store().updateShopSettings({ openingCash })'''
new = '''  const patch: { openingCash?: number; currency?: import("@/lib/domain/types").CurrencyCode } = {}
  if (input.openingCash !== undefined) {
    const openingCash = Math.round(Number(input.openingCash))
    if (!Number.isFinite(openingCash) || openingCash < 0 || openingCash > 10_000_000) return { ok: false, error: "Check the amount." }
    patch.openingCash = openingCash
  }
  if (input.currency !== undefined) {
    if (!["EUR", "UAH", "USD", "ARS"].includes(input.currency)) return { ok: false, error: "Choose a supported currency." }
    patch.currency = input.currency as import("@/lib/domain/types").CurrencyCode
  }
  if (!Object.keys(patch).length) return { ok: false, error: "There are no settings to save." }
  await store().updateShopSettings(patch)'''
if old not in body: raise RuntimeError("currency settings action anchor missing")
actions.write_text(body.replace(old, new, 1), encoding="utf-8")

# Add a separate currency selector so changing display units does not touch the
# existing opening-cash value. Values already saved are never converted.
form = ROOT / "src/components/settings/shop-settings-form.tsx"
body = form.read_text(encoding="utf-8")
body = body.replace('import type { ShopSettings } from "@/lib/domain/types"', 'import type { CurrencyCode, ShopSettings } from "@/lib/domain/types"\nimport { currencySymbol } from "@/lib/money"\nimport { normalizeLocale } from "@/i18n/messages"')
body = body.replace('  const [cash, setCash] = useState(String(settings.openingCash))', '  const [cash, setCash] = useState(String(settings.openingCash))\n  const [currency, setCurrency] = useState<CurrencyCode>(settings.currency || "ARS")')
body = body.replace('          <span className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-[14px] text-ivory-3">$</span>', '          <span className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-[14px] text-ivory-3">{currencySymbol(currency, normalizeLocale(document.documentElement.dataset.locale))}</span>')
anchor = '''      {dirty && (
        <Button'''.replace("+", "")
insert = '''      <label className="min-w-0 flex-1 basis-full sm:basis-auto">
        <span className="mb-1.5 block text-[12.5px] text-ivory-2">Business currency</span>
        <select value={currency} onChange={(event) => setCurrency(event.target.value as CurrencyCode)} className="h-10 w-full max-w-[260px] rounded-lg border border-line-strong bg-surface-2 px-3 text-[14px] text-ivory focus:border-gold/50 focus:outline-none">
          <option value="EUR">Euro (EUR)</option><option value="UAH">Hryvnia (UAH)</option><option value="USD">US dollar (USD)</option><option value="ARS">Argentine peso (ARS)</option>
        </select>
        <span className="mt-1 block max-w-md text-[11px] text-ivory-3">Currency used for prices, bookings and financial reports. Existing amounts are not converted.</span>
      </label>
      {currency !== (settings.currency || "ARS") && <Button disabled={pending} className="h-10" onClick={() => startTransition(async () => {
        const result = await saveShopSettings({ currency })
        if (!result.ok) { toast.error(result.error); return }
        toast.success("Business currency saved")
        window.location.reload()
      })}>{pending ? "Saving…" : "Save currency"}</Button>}

'''.replace("+", "")
if anchor not in body: raise RuntimeError("currency selector insertion point missing")
body = body.replace(anchor, insert + anchor, 1)
# Avoid reading document during SSR in the currency symbol label.
body = body.replace('currencySymbol(currency, normalizeLocale(document.documentElement.dataset.locale))', 'currencySymbol(currency, typeof document === "undefined" ? "en" : normalizeLocale(document.documentElement.dataset.locale))')
# Locale selector in this form is strictly EN/DE/UK; do not ship the legacy ES branch.
body = re.sub(r'  es: \{ label: "Zona horaria del local"[^\n]*\n', '', body)
body = re.sub(r'  es: \{ "Europe/Kyiv": "Kiev"[^\n]*\n', '', body)
body = body.replace('const [locale, setLocale] = useState<Locale>("es")', 'const [locale, setLocale] = useState<Locale>("en")')
body = body.replace('const language = (localStorage.getItem("booking_locale") || document.documentElement.dataset.locale || document.documentElement.lang).slice(0, 2) as Locale\n      if (language in TIMEZONE_COPY) setLocale(language)', 'const language = normalizeLocale(localStorage.getItem("booking_locale") || document.documentElement.dataset.locale || document.documentElement.lang)\n      setLocale(language)')
form.write_text(body, encoding="utf-8")

# The request root needs only one small query. Cookie selection establishes the
# same locale for server-rendered amounts and the client formatter.
root = ROOT / "src/app/layout.tsx"
root.write_text('''import type { Metadata,Viewport } from "next"
import { cookies } from "next/headers"
import { Archivo } from "next/font/google"
import { Toaster } from "@/components/ui/sonner"
import { TooltipProvider } from "@/components/ui/tooltip"
import { LocaleBridge } from "@/i18n/bridge"
import { LocaleThemeControls } from "@/i18n/controls"
import { normalizeLocale } from "@/i18n/messages"
import { configureMoney } from "@/lib/money"
import { runtimeSettings } from "@/lib/data/repo"
import { TimeZoneRuntime } from "@/components/settings/timezone-runtime"
import "./globals.css"
const archivo=Archivo({subsets:["latin","latin-ext"],axes:["wdth"],variable:"--font-archivo",display:"swap"})
export const metadata:Metadata={title:{default:"Booking · Panel",template:"%s · Booking"},description:"Booking — appointments, clients, cash and automation.",robots:{index:false,follow:false}}
export const viewport:Viewport={themeColor:[{media:"(prefers-color-scheme: dark)",color:"#050505"},{media:"(prefers-color-scheme: light)",color:"#ffffff"}]}
export default async function RootLayout({children}:LayoutProps<"/">){const [settings,jar]=await Promise.all([runtimeSettings(),cookies()]);const locale=normalizeLocale(jar.get("booking_locale")?.value);configureMoney(settings.currency,locale);return <html lang={locale} data-locale={locale} data-currency={settings.currency} className={archivo.variable+" h-full"} suppressHydrationWarning><head><script src="/booking-boot.js"/></head><body className="min-h-full"><TooltipProvider><TimeZoneRuntime timezone={settings.timezone}/>{children}</TooltipProvider><LocaleBridge/><LocaleThemeControls/><Toaster position="bottom-right"/></body></html>}
''', encoding="utf-8")

bridge = ROOT / "src/i18n/bridge.tsx"
body = bridge.read_text(encoding="utf-8")
body = body.replace('const l=selectedLocale();document.documentElement.lang=l;apply(document.documentElement,l);', 'const l=selectedLocale();document.documentElement.lang=l;document.documentElement.dataset.locale=l;apply(document.documentElement,l);')
bridge.write_text(body, encoding="utf-8")

# Keep the automatic startup migration chain in sync with the copied schema
# files. The calendar schedule patch adds 0016 before this installer runs.
migrator = Path("/tmp/booking-patch/migrate-booking.mjs")
body = migrator.read_text(encoding="utf-8")
old = '"0015_timezone.sql","0016_calendar_schedules.sql"'
if old not in body:
    raise RuntimeError("currency migration insertion point missing")
migrator.write_text(body.replace(old, old + ',"0017_currency.sql"', 1), encoding="utf-8")

print("BOOKING_FAST_RUNTIME_SETTINGS_AND_CURRENCY_INSTALLED")
