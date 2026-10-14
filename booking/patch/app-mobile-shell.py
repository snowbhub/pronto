from pathlib import Path
p=Path("/app/src/app/globals.css")
s=p.read_text(encoding="utf-8")
s += """
/* Booking mobile app shell: single vertical scroller, not a desktop canvas.
   Preserve existing light/dark color tokens. */
@media (max-width: 767px) {
  html, body { width:100%; max-width:100%; overflow-x:clip; overscroll-behavior-x:none; }
  body { min-height:100dvh; }
  .booking-app-shell { height:100dvh; min-height:0; overflow:hidden; display:flex; flex-direction:column; }
  .booking-app-main { flex:1; min-height:0; min-width:0; overflow-x:hidden; overflow-y:auto; overscroll-behavior-y:contain; -webkit-overflow-scrolling:touch; }
  .booking-app-main > * { min-width:0; max-width:100%; }
  .booking-app-header { flex:none; min-height:56px; padding-right:130px; }
  .booking-app-nav { flex:none; position:relative; inset:auto; width:100%; padding-bottom:env(safe-area-inset-bottom); }
  .booking-app-shell .panel { max-width:100%; }
  .booking-app-shell .panel > *, .booking-app-shell .grid > * { min-width:0; }
  .booking-app-shell [class*="overflow-x-auto"] { scrollbar-width:none; }
  .booking-app-shell [class*="overflow-x-auto"]::-webkit-scrollbar { display:none; }
  .booking-app-shell h1 { font-size:clamp(1.4rem,6vw,1.8rem); line-height:1.12; }
  .booking-app-shell .eyebrow { font-size:0.625rem; }
  .booking-app-shell .panel { border-radius:16px; }
  .booking-app-shell input, .booking-app-shell select, .booking-app-shell textarea { font-size:16px; max-width:100%; }
}
"""
p.write_text(s,encoding="utf-8")
p=Path("/app/src/app/(panel)/layout.tsx")
s=p.read_text(encoding="utf-8")
s=s.replace('className="flex min-h-dvh"','className="booking-app-shell flex min-h-dvh"')
s=s.replace('className="flex min-w-0 flex-1 flex-col"','className="flex min-h-0 min-w-0 flex-1 flex-col"')
s=s.replace('className="flex-1 pb-24 lg:pb-10"','className="booking-app-main flex-1 pb-5 lg:pb-10"')
s=s.replace('className="booking-app-shell flex min-h-dvh"','className="booking-app-shell flex min-h-dvh flex-col"')
s=s.replace('<div className="booking-app-shell flex min-h-dvh flex-col">','<div className="booking-app-shell flex min-h-dvh flex-col"><div className="flex min-h-0 min-w-0 flex-1">')
s=s.replace('      </div>\n      <MobileNav info={shell} />','      </div>\n      <MobileNav info={shell} />\n      </div>')
p.write_text(s,encoding="utf-8")
p=Path("/app/src/components/shell/mobile-nav.tsx")
s=p.read_text(encoding="utf-8").replace('className="fixed inset-x-0 bottom-0 z-40','className="booking-app-nav fixed inset-x-0 bottom-0 z-40')
p.write_text(s,encoding="utf-8")
p=Path("/app/src/components/shell/topbar.tsx")
s=p.read_text(encoding="utf-8").replace('className="sticky top-0 z-30 flex h-14','className="booking-app-header sticky top-0 z-30 flex h-14')
p.write_text(s,encoding="utf-8")
p=Path("/app/src/components/shell/page-header.tsx")
s=p.read_text(encoding="utf-8").replace('max-w-[1320px] px-4 py-6','max-w-[1320px] px-4 py-4')
p.write_text(s,encoding="utf-8")
print("BOOKING_APP_MOBILE_SHELL_APPLIED")


p=Path("/app/src/components/shell/topbar.tsx")
s=p.read_text(encoding="utf-8")
s=s.replace('      </div>\n    </header>', '        <div id="booking-header-actions" className="shrink-0" />\n      </div>\n    </header>')
p.write_text(s,encoding="utf-8")
p=Path("/app/src/app/reservar/page.tsx")
s=p.read_text(encoding="utf-8")
s=s.replace("py-4 pl-4 pr-32 sm:pl-6 sm:pr-36", "px-4 py-4 sm:px-6")
s=s.replace('          </div>\n        </div>\n      </header>', '          </div>\n          <div id="booking-public-header-actions" className="shrink-0" />\n        </div>\n      </header>')
p.write_text(s,encoding="utf-8")
print("BOOKING_HEADER_CONTROLS_EMBEDDED")
