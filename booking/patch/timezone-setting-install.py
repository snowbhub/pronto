from pathlib import Path

ROOT = Path("/app")
def edit(rel, old, new, label):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise RuntimeError(f"{label}: anchor missing in {rel}")
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")

# Runtime timezone. Keeping the zone mutable lets the server and hydrated client
# use the persisted business setting; all Intl formatters must be created lazily.
p = ROOT / "src/lib/time.ts"
s = p.read_text(encoding="utf-8")
old = 'export const TZ = process.env.NEXT_PUBLIC_BOOKING_TIME_ZONE || "Europe/Berlin"'
if old not in s: raise RuntimeError("timezone-i18n patch must run before timezone-setting patch")
s = s.replace(old, '''export let TZ = process.env.NEXT_PUBLIC_BOOKING_TIME_ZONE || "Europe/Berlin"

export function setTimeZone(value: string): void {
  const zone = String(value || "").trim()
  // Intl validates IANA names and rejects arbitrary offsets / invalid input.
  new Intl.DateTimeFormat("en", { timeZone: zone })
  TZ = zone
}''', 1)
s = s.replace("return dayKeyFmt.format(toDate(d))", '''return new Intl.DateTimeFormat("en-CA", {
    timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit",
  }).format(toDate(d))''', 1)
s = s.replace("return hmFmt.format(toDate(d))", '''return new Intl.DateTimeFormat("en-GB", {
    timeZone: TZ, hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  }).format(toDate(d))''', 1)
s = s.replace('return longFmt.format(at(day, "12:00"))', '''return new Intl.DateTimeFormat("es-AR", {
    timeZone: TZ, weekday: "long", day: "numeric", month: "long",
  }).format(at(day, "12:00"))''', 1)
s = s.replace('return shortFmt.format(at(day, "12:00")).replace(/\\./g, "")', '''return new Intl.DateTimeFormat("es-AR", {
    timeZone: TZ, weekday: "short", day: "numeric", month: "short",
  }).format(at(day, "12:00")).replace(/\\./g, "")''', 1)
s = s.replace('return monthFmt.format(at(`${month}-15`, "12:00"))', 'return new Intl.DateTimeFormat("es-AR", { timeZone: TZ, month: "long", year: "numeric" }).format(at(month + "-15", "12:00"))', 1)
p.write_text(s, encoding="utf-8")

# Persisted domain setting.
edit("src/lib/domain/types.ts",
     "  slotStepMin: number\n}", "  slotStepMin: number\n  /** IANA zone used for business hours, calendars and booking slots. */\n  timezone: string\n}",
     "shop settings type")
edit("src/lib/data/store/postgres.ts",
     "        slotStepMin: Number(shop[0].slot_step_min ?? 60),",
     "        slotStepMin: Number(shop[0].slot_step_min ?? 60),\n        timezone: String(shop[0].timezone ?? \"Europe/Berlin\"),",
     "shop settings database mapping")
edit("src/lib/data/store/postgres.ts",
     "    if (patch.slotStepMin !== undefined) row.slot_step_min = patch.slotStepMin",
     "    if (patch.slotStepMin !== undefined) row.slot_step_min = patch.slotStepMin\n    if (patch.timezone !== undefined) row.timezone = patch.timezone",
     "shop settings database update")
edit("src/lib/data/seed.ts",
     "shopSettings: { openingCash: 20000, depositEnabled: false, depositAmount: 0, depositHoldMin: 15, remindersEnabled: false, slotStepMin: 60 },",
     "shopSettings: { openingCash: 20000, depositEnabled: false, depositAmount: 0, depositHoldMin: 15, remindersEnabled: false, slotStepMin: 60, timezone: \"Europe/Berlin\" },",
     "demo settings default")

# Load the business timezone before server-side calendar/availability calculations.
edit("src/lib/data/repo.ts",
     'import { dayKey } from "@/lib/time"',
     'import { dayKey, setTimeZone } from "@/lib/time"',
     "repo timezone import")
edit("src/lib/data/repo.ts",
     "  const s = await store().snapshot()",
     "  const s = await store().snapshot()\n  setTimeZone(s.shopSettings.timezone || \"Europe/Berlin\")",
     "repo timezone initialization")

# Authenticated, validated settings action. Existing records remain UTC instants.
p = ROOT / "src/lib/data/settings-actions.ts"
s = p.read_text(encoding="utf-8")
anchor = "const SLOT_STEPS = [30, 45, 60]"
if anchor not in s: raise RuntimeError("settings action insertion point missing")
action = '''export async function saveShopTimezone(timezone: string): Promise<Result> {
  await assertPanelSession()
  const value = String(timezone ?? "").trim()
  if (!value || value.length > 100) return { ok: false, error: "Elegí una zona horaria válida." }
  try {
    new Intl.DateTimeFormat("en", { timeZone: value })
  } catch {
    return { ok: false, error: "Elegí una zona horaria IANA válida." }
  }
  await store().updateShopSettings({ timezone: value })
  refresh()
  return { ok: true }
}

'''
s = s.replace(anchor, action + anchor, 1)
p.write_text(s, encoding="utf-8")

# Selector with UI copy for all supported app languages.
p = ROOT / "src/components/settings/shop-settings-form.tsx"
s = p.read_text(encoding="utf-8")
s = s.replace('import { useState, useTransition } from "react"', 'import { useEffect, useState, useTransition } from "react"', 1)
s = s.replace('import { saveShopSettings } from "@/lib/data/settings-actions"', 'import { saveShopSettings, saveShopTimezone } from "@/lib/data/settings-actions"', 1)
s += '''
const TIMEZONE_OPTIONS = [
  "Europe/Kyiv",
  "Europe/Berlin",
  "Europe/Warsaw",
  "Europe/Paris",
  "Europe/London",
  "America/Argentina/Buenos_Aires",
  "America/New_York",
  "America/Los_Angeles",
  "Asia/Dubai",
  "Asia/Tokyo",
  "UTC",
] as const

const TIMEZONE_COPY = {
  uk: { label: "Часовий пояс закладу", help: "Час у календарі та доступні слоти бронювання використовують цей часовий пояс.", save: "Зберегти", saving: "Збереження…", saved: "Часовий пояс збережено", error: "Не вдалося зберегти часовий пояс" },
  de: { label: "Zeitzone des Betriebs", help: "Kalenderzeiten und verfügbare Buchungstermine richten sich nach dieser Zeitzone.", save: "Speichern", saving: "Wird gespeichert…", saved: "Zeitzone gespeichert", error: "Zeitzone konnte nicht gespeichert werden" },
  en: { label: "Business time zone", help: "Calendar times and available booking slots use this time zone.", save: "Save", saving: "Saving…", saved: "Time zone saved", error: "Could not save time zone" },
  es: { label: "Zona horaria del local", help: "El calendario y los horarios disponibles para reservar usan esta zona horaria.", save: "Guardar", saving: "Guardando…", saved: "Zona horaria guardada", error: "No se pudo guardar la zona horaria" },
} as const

const ZONE_NAMES = {
  uk: { "Europe/Kyiv": "Київ", "Europe/Berlin": "Берлін", "Europe/Warsaw": "Варшава", "Europe/Paris": "Париж", "Europe/London": "Лондон", "America/Argentina/Buenos_Aires": "Буенос-Айрес", "America/New_York": "Нью-Йорк", "America/Los_Angeles": "Лос-Анджелес", "Asia/Dubai": "Дубай", "Asia/Tokyo": "Токіо", UTC: "UTC" },
  de: { "Europe/Kyiv": "Kyjiw", "Europe/Berlin": "Berlin", "Europe/Warsaw": "Warschau", "Europe/Paris": "Paris", "Europe/London": "London", "America/Argentina/Buenos_Aires": "Buenos Aires", "America/New_York": "New York", "America/Los_Angeles": "Los Angeles", "Asia/Dubai": "Dubai", "Asia/Tokyo": "Tokio", UTC: "UTC" },
  en: { "Europe/Kyiv": "Kyiv", "Europe/Berlin": "Berlin", "Europe/Warsaw": "Warsaw", "Europe/Paris": "Paris", "Europe/London": "London", "America/Argentina/Buenos_Aires": "Buenos Aires", "America/New_York": "New York", "America/Los_Angeles": "Los Angeles", "Asia/Dubai": "Dubai", "Asia/Tokyo": "Tokyo", UTC: "UTC" },
  es: { "Europe/Kyiv": "Kiev", "Europe/Berlin": "Berlín", "Europe/Warsaw": "Varsovia", "Europe/Paris": "París", "Europe/London": "Londres", "America/Argentina/Buenos_Aires": "Buenos Aires", "America/New_York": "Nueva York", "America/Los_Angeles": "Los Ángeles", "Asia/Dubai": "Dubái", "Asia/Tokyo": "Tokio", UTC: "UTC" },
} as const

export function TimeZoneSettingsForm({ value }: { value: string }) {
  type Locale = keyof typeof TIMEZONE_COPY
  const [locale, setLocale] = useState<Locale>("es")
  const [timezone, setTimezone] = useState(value)
  const [pending, startTransition] = useTransition()

  useEffect(() => {
    const language = document.documentElement.lang.slice(0, 2) as Locale
    if (language in TIMEZONE_COPY) setLocale(language)
  }, [])

  const copy = TIMEZONE_COPY[locale]
  const names = ZONE_NAMES[locale]
  const dirty = timezone !== value
  return (
    <div className="mt-4 flex flex-wrap items-end gap-3">
      <label className="min-w-0 flex-1">
        <span className="mb-1.5 block text-[12.5px] text-ivory-2">{copy.label}</span>
        <select
          value={timezone}
          onChange={(event) => setTimezone(event.target.value)}
          className="h-10 w-full max-w-md rounded-lg border border-line-strong bg-surface-2 px-3 text-[14px] text-ivory focus:border-gold/50 focus:outline-none"
        >
          {!TIMEZONE_OPTIONS.includes(timezone as typeof TIMEZONE_OPTIONS[number]) && <option value={timezone}>{timezone}</option>}
          {TIMEZONE_OPTIONS.map((zone) => (
            <option key={zone} value={zone}>{names[zone]} · {zone}</option>
          ))}
        </select>
        <span className="mt-1.5 block text-[12px] text-ivory-3">{copy.help}</span>
      </label>
      {dirty && (
        <Button
          disabled={pending}
          className="h-10"
          onClick={() => startTransition(async () => {
            const result = await saveShopTimezone(timezone)
            if (!result.ok) {
              toast.error(result.error || copy.error)
              return
            }
            toast.success(copy.saved)
            window.location.reload()
          })}
        >
          {pending ? copy.saving : copy.save}
        </Button>
      )}
    </div>
  )
}
'''
p.write_text(s, encoding="utf-8")

# Show saved value in Settings instead of the former static Argentina label.
p = ROOT / "src/app/(panel)/ajustes/page.tsx"
s = p.read_text(encoding="utf-8")
s = s.replace('import { ShopSettingsForm } from "@/components/settings/shop-settings-form"',
              'import { ShopSettingsForm, TimeZoneSettingsForm } from "@/components/settings/shop-settings-form"', 1)
s = s.replace('<Item label="Zona horaria" value="Argentina (UTC−3)" />',
              '<Item label="Zona horaria" value={s.shopSettings.timezone} />', 1)
anchor = '''              </dl>
            </Panel>
            <Panel title="Horarios que se ofrecen">'''
if anchor not in s: raise RuntimeError("settings timezone control anchor missing")
s = s.replace(anchor, '''              </dl>
              <TimeZoneSettingsForm value={s.shopSettings.timezone} />
            </Panel>
            <Panel title="Horarios que se ofrecen">''', 1)
p.write_text(s, encoding="utf-8")

# Initialize the client-side date helpers with the saved zone on every app route.
(ROOT / "src/components/settings/timezone-runtime.tsx").write_text('''"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { setTimeZone, TZ } from "@/lib/time"

export function TimeZoneRuntime({ timezone }: { timezone: string }) {
  const router = useRouter()
  useEffect(() => {
    if (TZ === timezone) return
    setTimeZone(timezone)
    router.refresh()
  }, [timezone, router])
  return null
}
''', encoding="utf-8")
p = ROOT / "src/app/layout.tsx"
s = p.read_text(encoding="utf-8")
s = s.replace('import { BRAND } from "@/config/brand"', 'import { BRAND } from "@/config/brand"\nimport { db } from "@/lib/data/repo"\nimport { TimeZoneRuntime } from "@/components/settings/timezone-runtime"', 1)
s = s.replace('export default function RootLayout({ children }: LayoutProps<"/">) {\n  return (',
              'export default async function RootLayout({ children }: LayoutProps<"/">) {\n  const snapshot = await db()\n  return (', 1)
s = s.replace('<TooltipProvider>{children}</TooltipProvider>',
              '<TooltipProvider><TimeZoneRuntime timezone={snapshot.shopSettings.timezone} />{children}</TooltipProvider>', 1)
p.write_text(s, encoding="utf-8")
print("BOOKING_PERSISTENT_TIMEZONE_INSTALLED")
