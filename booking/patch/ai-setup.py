from pathlib import Path
root=Path("/app")
p=root/"src/app/(panel)/agente/page.tsx"
s=p.read_text(encoding="utf-8")
s='import Link from "next/link"\n'+s
s=s.replace('import { store } from "@/lib/data/repo"','import { store } from "@/lib/data/repo"\nimport { readZernioConfig,readZernioWebhookConfig } from "@/lib/zernio/config"')
s=s.replace('  const config = readAgentConfig()','  const config = readAgentConfig()\n  const zernio = readZernioConfig()\n  const webhook = readZernioWebhookConfig()')
s=s.replace('''      <section className="panel mt-8 grid grid-cols-2 sm:grid-cols-4">''','''      <section className="panel mt-5 space-y-3 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-semibold">AI integration status</h2>
          <span className="rounded-full bg-surface-3 px-3 py-1 text-xs">{config.configured && zernio.configured && webhook.configured && d.settings.enabled ? "Ready" : "Setup required"}</span>
        </div>
        <ul className="space-y-2 text-sm text-ivory-2">
          <li>{config.configured ? "✓" : "○"} AI model: {config.configured ? config.model : config.reason}</li>
          <li>{zernio.configured ? "✓" : "○"} WhatsApp / Instagram provider: {zernio.configured ? "API key configured" : "ZERNIO_API_KEY required"}</li>
          <li>{webhook.configured ? "✓" : "○"} Incoming messages: {webhook.configured ? "Webhook secret configured" : "ZERNIO_WEBHOOK_SECRET required"}</li>
        </ul>
        <p className="text-sm text-ivory-3">Configure GEMINI_API_KEY (or ANTHROPIC_API_KEY), ZERNIO_API_KEY and ZERNIO_WEBHOOK_SECRET in your Railway service variables. Then connect messaging accounts under Settings → Connections. No AI can respond without these credentials.</p>
        <div className="flex flex-wrap gap-3"><Link href="/ajustes?tab=conexiones" className="rounded-xl border border-line-strong px-4 py-3 text-sm font-semibold">Messaging connections</Link><a href="https://railway.com/project/eb72c125-99bb-4b61-b445-b63ddba8776a" target="_blank" rel="noreferrer" className="rounded-xl bg-ivory px-4 py-3 text-sm font-semibold text-obsidian">Open Railway settings</a></div>
      </section>
      <section className="panel mt-8 grid grid-cols-2 sm:grid-cols-4">''')
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/page.tsx"
s=p.read_text(encoding="utf-8")
s='import { readAgentConfig } from "@/lib/agent/config"\nimport { readZernioConfig,readZernioWebhookConfig } from "@/lib/zernio/config"\n'+s
s=s.replace('enabled={d.agent.enabled}','enabled={d.agent.enabled && readAgentConfig().configured && readZernioConfig().configured && readZernioWebhookConfig().configured}')
p.write_text(s,encoding="utf-8")
print("BOOKING_AI_SETUP_STATUS_FIX")
