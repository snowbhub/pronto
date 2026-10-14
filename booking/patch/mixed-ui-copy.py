from pathlib import Path
import re
root=Path("/app")
p=root/"src/app/login/login-form.tsx"
s=p.read_text(encoding="utf-8")
s=re.sub(r'(<span className="mb-1\.5 block text-\[12\.5px\] text-ivory-2">)[^<]*(</span>)',r'\1Panel password\2',s,count=1)
s=s.replace('"Entrando…"','"Signing in…"').replace('"Entrar"','"Sign in"')
p.write_text(s,encoding="utf-8")
p=root/"src/components/settings/team-editor.tsx"
s=p.read_text(encoding="utf-8")
for old in ["Sumar a alguien al equipo","Sumar до alguien al equipo","Sumar someone to team"]:
 s=s.replace(old,"Add team member")
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('Nadie por ahora. 👌','Nobody yet. 👌').replace('Nadie por зараз. 👌','Nobody yet. 👌')
p.write_text(s,encoding="utf-8")
p=root/"src/lib/zernio/config.ts"
s=p.read_text(encoding="utf-8")
s=s.replace('Falta ZERNIO_API_KEY. Se crea en el panel de Zernio.','ZERNIO_API_KEY is missing. Create an API key in Zernio and add it to Railway.')
s=s.replace('Falta ZERNIO_API_KEY. Se crea en y pany з Zernio.','ZERNIO_API_KEY is missing. Create an API key in Zernio and add it to Railway.')
s=s.replace('Falta ZERNIO_WEBHOOK_SECRET.','ZERNIO_WEBHOOK_SECRET is missing.')
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('Conectada: todo lo que se carga queda guardado.','Connected. Your data is saved in PostgreSQL.')
s=s.replace('Conectada: todo lo que se carga queda збережено.','Connected. Your data is saved in PostgreSQL.')
s=s.replace('Conectada: todo lo que se carga queda saved.','Connected. Your data is saved in PostgreSQL.')
p.write_text(s,encoding="utf-8")
print("BOOKING_MIXED_UI_COPY_FIXED")
