from pathlib import Path
root=Path("/app/src")
p=root/"components/agenda/new-appointment.tsx"
s=p.read_text(encoding="utf-8")
anchor='slots.length === 0 ? ('
where=s.find(anchor)
if where<0:raise RuntimeError("Booking empty-slot conditional moved")
begin=s.find('<p className="rounded-lg border border-dashed',where)
end=s.find('</p>',begin)
if begin<0 or end<0:raise RuntimeError("Booking empty-slot notice moved")
old=s[begin:end+4]
if '{staff.name}' not in old or '{duration}' not in old:
 raise RuntimeError("Refusing to replace unknown appointment warning")
new='''<p data-booking-native-locale className="booking-slot-message rounded-lg border border-dashed border-line-strong px-3 py-3 text-center text-[13px] leading-relaxed text-ivory-3">
              <span data-slot-locale="en">{staff.name} has no available {duration}-minute appointment slots on this day. Select another time below, a different team member or another day.</span>
              <span data-slot-locale="de">Für {staff.name} gibt es an diesem Tag keine freien Termine mit {duration} Minuten Dauer. Wähle unten eine andere Uhrzeit, eine andere Fachkraft oder einen anderen Tag.</span>
              <span data-slot-locale="uk">У {staff.name} на цей день немає вільного часу для запису тривалістю {duration} хв. Оберіть інший час нижче, іншого майстра або інший день.</span>
            </p>'''
s=s[:begin]+new+s[end+4:]
p.write_text(s,encoding="utf-8")

p=root/"i18n/bridge.tsx"
s=p.read_text(encoding="utf-8")
old='script,style,code,pre,[contenteditable=true]'
if old not in s:raise RuntimeError("Locale bridge exclusion selector changed")
s=s.replace(old,old+',[data-booking-native-locale]')
p.write_text(s,encoding="utf-8")

p=root/"app/globals.css"
s=p.read_text(encoding="utf-8")
s+='''
/* These complete booking warning sentences are authored in each language,
   not assembled by translating words around a dynamic employee name. */
.booking-slot-message [data-slot-locale]{display:none}
html:not([lang^="uk"]):not([lang^="de"]) .booking-slot-message [data-slot-locale="en"]{display:inline}
html[lang^="de"] .booking-slot-message [data-slot-locale="de"]{display:inline}
html[lang^="uk"] .booking-slot-message [data-slot-locale="uk"]{display:inline}
'''
p.write_text(s,encoding="utf-8")
print("BOOKING_SLOT_WARNING_WHOLE_SENTENCES_EN_DE_UK")
