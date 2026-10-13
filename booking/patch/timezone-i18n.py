from pathlib import Path
p=Path("/app/src/lib/time.ts")
s=p.read_text(encoding="utf-8")
s=s.replace('export const TZ = "America/Argentina/Buenos_Aires"\nconst OFFSET = "-03:00"','export const TZ = process.env.NEXT_PUBLIC_BOOKING_TIME_ZONE || "Europe/Berlin"')
s=s.replace('return new Date(`\u0024{day}T\u0024{time}:00\u0024{OFFSET}`)','''const desired = new Date(day + "T" + time + ":00Z").getTime()
  let instant = desired
  const partsAt = (timestamp: number) => {
    const parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
    }).formatToParts(new Date(timestamp))
    const map = Object.fromEntries(parts.map(p => [p.type,p.value]))
    return Date.UTC(Number(map.year),Number(map.month)-1,Number(map.day),Number(map.hour),Number(map.minute),Number(map.second))
  }
  for (let i = 0; i < 3; i++) instant += desired-partsAt(instant)
  return new Date(instant)''')
s=s.replace('''const d = at(day, "12:00")
  d.setUTCDate(d.getUTCDate() + n)
  return dayKey(d)''','''const d = new Date(day + "T12:00:00Z")
  d.setUTCDate(d.getUTCDate() + n)
  return d.toISOString().slice(0,10)''')
s=s.replace('return at(day, "12:00").getUTCDay()', 'return new Date(day + "T12:00:00Z").getUTCDay()')
p.write_text(s,encoding="utf-8")
print("BOOKING_IANA_TIMEZONE_PATCHED",TZ if False else "Europe/Berlin")
