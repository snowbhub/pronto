from pathlib import Path
root=Path("/app")
p=root/"src/lib/domain/slots.test.ts"
s=p.read_text(encoding="utf-8")
s=s.replace('toContain("franco o un turno fijo")','toContain("time off or a fixed booking")')
s=s.replace('toContain("cobralo o marcalo como terminado")','toContain("charge it or mark it completed")')
p.write_text(s,encoding="utf-8")
p=root/"src/lib/agent/providers/providers.test.ts"
s=p.read_text(encoding="utf-8")
s=s.replace('Contexto del sistema — no es parte del mensaje del cliente','System context — not part of the client message')
p.write_text(s,encoding="utf-8")
print("BOOKING_TEST_EXPECTATIONS_CANONICAL")
