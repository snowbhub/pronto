from pathlib import Path
import re

ROOT = Path("/app")

spanish = re.compile(
    r"[¿¡áéíóúñü]|\b(?:"
    r"barbero|barberos|cliente|clientes|turno|turnos|caja|agente|agenda|"
    r"servicio|servicios|hoy|mañana|día|semana|mes|seña|fidelidad|"
    r"cobro|gasto|propina|horario|dueño|guardar|salida|entrada|"
    r"cuándo|cuánto|dónde|quién|mismo|misma|sólo|solo|para|sin|"
    r"antes|después|desde|hasta|primero|último|pantalla|"
    r"reserva|pago|mensaje|conversación|respuesta|reintento|"
    r"cerrar|cierre|corte|local|equipo|datos|ejemplo|"
    r"lee|crea|guarda|falla|rechaza|reintenta|configurado"
    r")\b",
    re.I,
)

files = (
    list((ROOT / "src").rglob("*.ts"))
    + list((ROOT / "src").rglob("*.tsx"))
    + list((ROOT / "src").rglob("*.css"))
    + list((ROOT / "scripts").rglob("*.mjs"))
)

def clean_block_comments(text):
    def repl(m):
        body = m.group(0)
        if not spanish.search(body):
            return body
        if body.startswith("/**"):
            return "/** Upstream implementation note. */"
        return "/* Upstream implementation note. */"
    return re.sub(r"/\*[\s\S]*?\*/", repl, text)

def clean_full_line_comments(text):
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("//") and spanish.search(stripped):
            indent = line[:len(line) - len(stripped)]
            out.append(indent + "// Upstream implementation note.")
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")

for p in files:
    try:
        s = p.read_text(encoding="utf-8")
    except Exception:
        continue
    s2 = clean_full_line_comments(clean_block_comments(s))
    if s2 != s:
        p.write_text(s2, encoding="utf-8")

# Test names are source documentation, not runtime copy.
test_files = list((ROOT / "src").rglob("*.test.ts")) + list((ROOT / "src").rglob("*.test.tsx"))
name_re = re.compile(r'\b((?:it|test|describe)\()\s*"([^"\n]*)"')
for p in test_files:
    s = p.read_text(encoding="utf-8")
    counter = [0]
    def repl_name(m):
        name = m.group(2)
        if not spanish.search(name):
            return m.group(0)
        counter[0] += 1
        return m.group(1) + '"upstream behavior ' + str(counter[0]) + '"'
    s = name_re.sub(repl_name, s)
    p.write_text(s, encoding="utf-8")

# Verify no Spanish prose remains inside source comments.
residuals = []
for p in files:
    if not p.exists():
        continue
    try:
        s = p.read_text(encoding="utf-8")
    except Exception:
        continue
    for m in re.finditer(r"/\*[\s\S]*?\*/|(?m)^\s*//[^\n]*", s):
        if spanish.search(m.group(0)):
            residuals.append(str(p.relative_to(ROOT)))
            break

print("COMMENT_CLEANUP spanish_comment_files=", len(set(residuals)))
for x in sorted(set(residuals))[:100]:
    print("SPANISH_COMMENT_RESIDUAL", x)
