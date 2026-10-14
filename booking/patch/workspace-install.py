from pathlib import Path
root=Path("/app")
src=Path("/tmp/booking-patch/workspace-shell.tsx")
dest=root/"src/components/shell/booking-workspace-shell.tsx"
dest.write_text(src.read_text(encoding="utf-8"),encoding="utf-8")
layout=root/"src/app/(panel)/layout.tsx"
s=layout.read_text(encoding="utf-8")
anchor='import { MobileNav } from "@/components/shell/mobile-nav"'
if anchor not in s:raise RuntimeError("Layout shell imports changed")
s=s.replace(anchor,anchor+'\nimport { BookingWorkspaceShell } from "@/components/shell/booking-workspace-shell"')
a=s.find('<div className="booking-app-shell ')
b=s.find('    </NewAppointmentProvider>',a)
if a<0 or b<0:raise RuntimeError("Layout shell JSX changed; refusing dangerous rewrite")
s=s[:a]+'''<BookingWorkspaceShell
        sidebar={<Sidebar info={shell} />}
        topbar={<Topbar info={shell} now={shell.now} simulated={shell.simulated} />}
        mobileNav={<MobileNav info={shell} />}
      >
        {children}
      </BookingWorkspaceShell>
'''+s[b:]
layout.write_text(s,encoding="utf-8")
print("BOOKING_WORKSPACE_MODES_SPLIT",s.count("BookingWorkspaceShell"))
