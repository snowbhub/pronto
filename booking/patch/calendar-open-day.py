from pathlib import Path

root = Path('/app')
# Calendar entry points must explicitly request the day grid. This clears a
# stale week view when the user taps Calendar from any navigation surface.
for rel in (
    'src/components/shell/nav.ts',
    'src/components/shell/mobile-nav.tsx',
    'src/components/shell/booking-workspace-shell.tsx',
):
    p = root / rel
    if not p.exists():
        continue
    s = p.read_text(encoding='utf-8')
    s = s.replace('href="/agenda"', 'href="/agenda?view=day"')
    s = s.replace('href: "/agenda",', 'href: "/agenda?view=day",')
    p.write_text(s, encoding='utf-8')
print('BOOKING_CALENDAR_ENTRY_OPENS_DAY_GRID')
