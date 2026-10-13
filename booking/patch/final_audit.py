from pathlib import Path
import re

ROOT = Path("/app")
TECH = {
    "barbero","cliente","servicio","servicios","efectivo","transferencia","fidelidad",
    "agente","humano","corte","semana","mes","horario","datos","listo","cobro","sena",
    "pendiente","confirmado","cancelado","completado","panel","web","ia","alquiler",
    "insumos","otros","debito","credito","producto","franco","dueno","cercano",
    "profesional","canchero","dia","vista","filtro"
}
marker = re.compile(
    r"\b(?:turno|turnos|barbero|barberos|cliente|clientes|caja|finanzas|ajustes|bandeja|"
    r"agente|fidelidad|gasto|gastos|seña|guardar|elegí|revisá|dueño|hoy|mañana|"
    r"servicio|servicios|propina|propinas|horario|semana|mes|cobro|cerrado|ingresos|"
    r"cuánto|corte|más|tenés|quedan|desde|hasta|día|días|salida|entrada|"
    r"conversación|mensaje|pago|reserva|responder)\b",
    re.I
)

files=[]
for r in [ROOT/"src/app", ROOT/"src/components"]:
    files += list(r.rglob("*.tsx"))
    files += list(r.rglob("*.ts"))

res=[]
for p in files:
    s=p.read_text(encoding="utf-8",errors="ignore")
    s=re.sub(r"/\*[\s\S]*?\*/","",s)
    s=re.sub(r"(?m)^\s*//[^\n]*","",s)
    literals=[]
    literals += [m.group(1) for m in re.finditer(r'"([^"\n]{2,260})"',s)]
    literals += [m.group(1) for m in re.finditer(r"'([^'\n]{2,260})'",s)]
    literals += [m.group(1).strip() for m in re.finditer(r">([^<>{}\n]{2,260})<",s)]
    for v in literals:
        low=v.strip().lower()
        if low in TECH or v.startswith("/") or v.startswith("@/") or "className" in v:
            continue
        if marker.search(v):
            res.append((str(p.relative_to(ROOT)),v[:240]))

brand=[]
for p in ROOT.rglob("*"):
    if not p.is_file() or "node_modules" in p.parts or ".next" in p.parts or ".git" in p.parts:
        continue
    if p.name=="importar-historial.mjs":
        continue
    if p.suffix not in {".ts",".tsx",".js",".mjs",".css",".json",".md"}:
        continue
    try:s=p.read_text(encoding="utf-8")
    except:continue
    if re.search(r"\bVirex\b|VIREX|virex-mark|virex-wordmark|operon-badge",s,re.I):
        brand.append(str(p.relative_to(ROOT)))

print("FINAL_AUDIT visible_spanish_literals=",len(res),"old_brand_files=",len(set(brand)))
for path,value in res[:100]:
    print("FINAL_UI_RESIDUAL",path,":",value)
for path in sorted(set(brand))[:100]:
    print("FINAL_BRAND_RESIDUAL",path)
