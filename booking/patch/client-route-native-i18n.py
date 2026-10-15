from pathlib import Path
import re
root=Path('/app/src')
p=root/'i18n/bridge.tsx'
s=p.read_text(encoding='utf-8')
anchor='function translateTree(root:Node,locale:Locale){'
if anchor not in s:raise RuntimeError('Locale bridge tree anchor missing')
s=s.replace(anchor,anchor+'\n  // The client directory is localized by React itself; never mutate streaming/hydrating text.\n  if(location.pathname==="/clientes")return',1)
p.write_text(s,encoding='utf-8')
p=root/'app/(panel)/clientes/page.tsx'
s=p.read_text(encoding='utf-8')
anchor='import { Suspense } from "react"'
if anchor not in s:raise RuntimeError('Client page import missing')
s=s.replace(anchor,anchor+'\nimport { cookies } from "next/headers"\nimport { normalizeLocale, translateText } from "@/i18n/messages"',1)
anchor='  const d = await getClientes()'
if anchor not in s:raise RuntimeError('Client page data anchor missing')
s=s.replace(anchor,anchor+'\n  const locale = normalizeLocale((await cookies()).get("booking_locale")?.value)\n  const tr=(value:string)=>translateText(value,locale)',1)
s,n=re.subn(r'eyebrow="[^"]+"', 'eyebrow={tr("Client portfolio")}',s,count=1)
if n!=1:raise RuntimeError('Client PageHeader eyebrow missing')
s,n=re.subn(r'(?m)^\s*title="[^"]+"', '        title={tr("Clients")}',s,count=1)
if n!=1:raise RuntimeError('Client PageHeader title missing')
start=s.find('        description=')
end=s.find('\n        actions=',start)
if start<0 or end<0:raise RuntimeError('Client PageHeader description missing')
replacement='''        description={locale==="uk"
          ? `${d.rows.length} клієнтів · ${frequent} постійних · ${atRisk} у зоні ризику. Тут зберігаються нотатки, історія візитів і лояльність.`
          : locale==="de"
            ? `${d.rows.length} Kunden · ${frequent} Stammkunden · ${atRisk} gefährdete Kontakte. Profile enthalten Notizen, Besuchsverlauf und Treuepunkte.`
            : `${d.rows.length} clients · ${frequent} regular · ${atRisk} at risk. Profiles include service notes, visit history and loyalty status.`}'''
s=s[:start]+replacement+s[end:]
s=s.replace('actions={<NewAppointmentButton variant="outline" />}','actions={<NewAppointmentButton variant="outline" label={tr("New booking")} />}')
s=s.replace('<ClientDirectory rows={d.rows} now={d.now} services={d.services} staff={d.staff} />','<ClientDirectory rows={d.rows} now={d.now} services={d.services} staff={d.staff} locale={locale} />')
s=s.replace('<ClientsView rows={d.rows} now={d.now} services={d.services} staff={d.staff} />','<ClientsView rows={d.rows} now={d.now} services={d.services} staff={d.staff} locale={locale} />')
p.write_text(s,encoding='utf-8')
p=root/'components/clients/clients-view.tsx'
s=p.read_text(encoding='utf-8')
anchor='import { useEffect, useMemo, useState } from "react"'
if anchor not in s:raise RuntimeError('ClientsView imports changed')
s=s.replace(anchor,anchor+'\nimport { translateText, type Locale } from "@/i18n/messages"',1)
start=s.find('export function ClientsView({')
end=s.find('function ClientSheet(',start)
if start<0 or end<0:raise RuntimeError('ClientsView bounds missing')
head=s[start:end]
head=head.replace('  staff,\n}: {','  staff,\n  locale,\n}: {',1)
head=head.replace('  staff: Staff[]\n}) {','  staff: Staff[]\n  locale: Locale\n}) {',1)
anchor='  const router = useRouter()'
if anchor not in head:raise RuntimeError('ClientsView router hook missing')
head=head.replace(anchor,'  const tr=(value:string)=>translateText(value,locale)\n'+anchor,1)
head=head.replace('{s.label}','{tr(s.label)}')
head=head.replace('{SEGMENT_LABEL[r.segment]}','{tr(SEGMENT_LABEL[r.segment])}')
head=head.replace('staff={staff} onClose={() => setOpen(null)}','staff={staff} locale={locale} onClose={() => setOpen(null)}')
head=head.replace('{formatDayShort(dayKey(r.next.startsAt))}','{new Intl.DateTimeFormat(locale==="uk"?"uk-UA":locale==="de"?"de-DE":"en-GB",{day:"numeric",month:"short",timeZone:"Europe/Berlin"}).format(new Date(r.next.startsAt))}')
head,n=re.subn(r'\{`\$\{r.visits\} visits`\}', '{locale==="uk"?`${r.visits} ${r.visits%100>=11&&r.visits%100<=14?"візитів":r.visits%10===1?"візит":r.visits%10>=2&&r.visits%10<=4?"візити":"візитів"}`:locale==="de"?`${r.visits} ${r.visits===1?"Besuch":"Besuche"}`:`${r.visits} ${r.visits===1?"visit":"visits"}`}',head,count=1)
if n!=1:raise RuntimeError('Client mobile visit markup changed')
for raw in ['Client','Cliente','Visits','Visitas','Last visit','Última','Ticket','Loyalty','Fidelidad','Next booking','Próximo turno']:
    head=head.replace('>'+raw+'<','>{tr('+repr(raw)+')}<')
head=re.sub(r'placeholder="([^"]+)"',lambda m:'placeholder={tr('+repr(m.group(1))+')}',head)
head,n=re.subn(r'(<p className="px-5 py-10 text-center text-\[13px\] text-ivory-3">)([^<]+)(</p>)',lambda m:m.group(1)+'{tr('+repr(m.group(2))+')}' +m.group(3),head,count=1)
if n!=1:raise RuntimeError('Client empty text changed')
head,n=re.subn(r'(\s*)Show more \(\{filtered.length - limit\} remaining\)',r'\1{locale==="uk"?`Показати ще (${filtered.length-limit})`:locale==="de"?`Mehr anzeigen (${filtered.length-limit})`:`Show more (${filtered.length-limit} remaining)`}',head,count=1)
head=head.replace('>Mostrar más ({filtered.length - limit} restantes)<','>{locale==="uk"?`Показати ще (${filtered.length-limit})`:locale==="de"?`Mehr anzeigen (${filtered.length-limit})`:`Show more (${filtered.length-limit} remaining)`}<')
s=s[:start]+head+s[end:]
start=s.find('function ClientSheet(')
end=s.find('function Stat(',start)
if start<0 or end<0:raise RuntimeError('ClientSheet bounds missing')
sub=s[start:end]
sub=sub.replace('  staff,\n  onClose,','  staff,\n  locale,\n  onClose,',1)
sub=sub.replace('  staff: Staff[]\n  onClose:','  staff: Staff[]\n  locale: Locale\n  onClose:',1)
anchor='  const { open } = useNewAppointment()'
if anchor not in sub:raise RuntimeError('ClientSheet hook missing')
sub=sub.replace(anchor,'  const tr=(value:string)=>translateText(value,locale)\n'+anchor,1)
sub=re.sub(r'(<Stat label=")([^"]+)(")',lambda m:'<Stat label={tr('+repr(m.group(2))+')}',sub)
for raw in ['Recent visits','Últimas visitas','No visits yet.','Todavía no vino.','How they like their haircut','Cómo se corta','Agendar','Book']:
    sub=sub.replace('>'+raw+'<','>{tr('+repr(raw)+')}<')
sub=sub.replace('> con {staff.find','> {locale==="uk"?"із":locale==="de"?"mit":"with"} {staff.find')
s=s[:start]+sub+s[end:]
p.write_text(s,encoding='utf-8')
print('BOOKING_CLIENTS_REACT_NATIVE_LOCALE_READY')
