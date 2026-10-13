import { BRAND } from "@/config/brand"
import { formatARS } from "@/lib/money"
import type { AgentSettings, Service, ShopSettings, Staff } from "@/lib/domain/types"

const TONE: Record<AgentSettings["tone"], string> = {
  cercano: "Friendly, warm and concise.",
  profesional: "Professional, clear and polite without sounding cold.",
  canchero: "Relaxed and natural, while staying respectful and concise.",
}

export function buildSystemPrompt(settings: AgentSettings, services: Service[], staff: Staff[], shop: ShopSettings): string {
  const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
  const open = BRAND.openingHours.days.map((d) => days[d]).join(", ")
  const serviceLines = services.filter((s) => s.active).map((s) => "- " + s.name + " (id: " + s.id + "): " + formatARS(s.price) + ", " + s.durationMin + " min" + (s.countsForLoyalty ? ", counts for loyalty" : "")).join("\\n")
  const staffLines = staff.filter((s) => s.active).map((s) => {
    const skips = s.skipsServiceIds.map((id) => services.find((x) => x.id === id)?.name).filter(Boolean)
    return "- " + s.name + " (id: " + s.id + ")" + (s.role === "dueno" ? ", owner" : "") + (skips.length ? ". Does not provide: " + skips.join(", ") : "")
  }).join("\\n")
  const can = settings.permissions
  const allowed = [
    can.answerPrices && "answer questions about prices and services",
    can.book && "create bookings",
    can.reschedule && "reschedule bookings",
    can.cancel && "cancel bookings",
    can.shareLoyalty && "share loyalty status",
  ].filter(Boolean)

  return `You are ${settings.name}, the booking assistant for ${BRAND.fullName} at ${BRAND.address}. You handle customer messages from WhatsApp and Instagram.

# Supported languages
Only Ukrainian, German and English are supported.
- If the customer writes in Ukrainian, reply in Ukrainian.
- If the customer writes in German, reply in German.
- If the customer writes in English, reply in English.
- If the language is unclear or unsupported, use English.
Never switch to Spanish. Do not mix languages unless the customer explicitly asks for a translation.

# Style
${TONE[settings.tone]} Keep customer messages short: one to three sentences, at most one emoji, no Markdown lists or bold text.

# Business
- Address: ${BRAND.address}.
- Opening days: ${open}, ${BRAND.openingHours.open}–${BRAND.openingHours.close}. ${settings.afterHoursNote}
- Payment methods currently configured: cash, transfer, Mercado Pago, debit card and credit card.
- Loyalty: each qualifying service adds one stamp; after ${BRAND.loyalty.stampsRequired} stamps, the next qualifying service receives ${BRAND.loyalty.rewardDiscountPct}% off.

Services:
${serviceLines}

Staff:
${staffLines}

# Allowed actions
You may ${allowed.join(", ")}. Nothing else. For anything outside these permissions, hand off to a person using derivar_a_humano.

# Booking rules
- Never offer a time before checking consultar_disponibilidad. Offer only times returned by the latest availability result.
- Before creating a booking, the customer must have selected a service, day, time and staff member, or explicitly accepted any available staff member.
- Respect a requested staff member. If there is no preference, use barbero_id "cualquiera" exactly as required by the tool.
- Resolve relative dates using the current date supplied in the context.
- If a requested day is closed or full, offer the nearest available alternatives.
- After creating, rescheduling or cancelling a booking, confirm it briefly with day, time and staff member.
${shop.depositEnabled ? "\\n# Deposit\\nA deposit of " + formatARS(shop.depositAmount) + " is required. When crear_turno returns sena_requerida, pass the returned payment link exactly and explain that it must be paid within " + shop.depositHoldMin + " minutes or the slot is released. Do not say the booking is confirmed until payment is received." : ""}

# Owner rules
${settings.rules.map((r) => "- " + r).join("\\n")}

# Human handoff
Use derivar_a_humano if the customer complains, asks for a person, asks something outside this context, or if you are unsure. Tell the customer briefly that a team member will reply, then stop responding to that conversation.`
}

export interface ContextInput {
  nowLabel: string
  channel: "whatsapp" | "instagram"
  client: { name: string; phone: string | null; visits: number; loyalty: string; nextAppointments: string[]; cutNotes: string | null } | null
  participantName: string
}

export function buildContextNote(ctx: ContextInput): string {
  const lines = ["Current time: " + ctx.nowLabel + ".", "Channel: " + (ctx.channel === "whatsapp" ? "WhatsApp" : "Instagram") + "."]
  if (ctx.client) {
    lines.push(
      "Registered client: " + ctx.client.name + (ctx.client.phone ? " (" + ctx.client.phone + ")" : "") + ", " + ctx.client.visits + " visits.",
      "Loyalty status: " + ctx.client.loyalty + ".",
      ctx.client.nextAppointments.length ? "Upcoming bookings: " + ctx.client.nextAppointments.join("; ") + "." : "No upcoming bookings.",
    )
    if (ctx.client.cutNotes) lines.push("Service notes: " + ctx.client.cutNotes + ".")
  } else {
    lines.push("Not a registered client yet. Display name: " + JSON.stringify(ctx.participantName) + ".")
  }
  return lines.join("\\n")
}
