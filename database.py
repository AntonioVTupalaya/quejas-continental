import os
import uuid
from datetime import datetime

from supabase import create_client


def get_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)


def subir_evidencia(nombre_archivo, contenido, mime):
    sb = get_client()
    ruta = f"{uuid.uuid4().hex}_{nombre_archivo}"
    sb.storage.from_("evidencias").upload(
        ruta,
        contenido,
        file_options={"content-type": mime, "x-upsert": "true"},
    )
    return sb.storage.from_("evidencias").get_public_url(ruta)


def init_db():
    sb = get_client()
    try:
        sb.table("quejas").select("id").limit(1).execute()
    except Exception:
        raise RuntimeError(
            "Tabla 'quejas' no existe en Supabase. Crealas en el SQL Editor."
        )


def generar_folio(sb):
    anio = datetime.now().strftime("%Y")
    prefijo = f"Q-{anio}-"
    rows = sb.table("quejas").select("folio").ilike("folio", f"{prefijo}%").execute().data
    maximo = 0
    for r in rows:
        try:
            maximo = max(maximo, int(r["folio"].rsplit("-", 1)[1]))
        except (ValueError, IndexError):
            continue
    return f"Q-{anio}-{maximo + 1:04d}"


def insertar_queja(datos, horarios=None):
    sb = get_client()
    folio = generar_folio(sb)
    creado_en = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fila = {
        "folio": folio,
        "fecha": datos["fecha"],
        "apellidos": datos["apellidos"],
        "nombres": datos["nombres"],
        "matricula": datos["matricula"],
        "celular": datos.get("celular", ""),
        "correo": datos.get("correo", ""),
        "dni": datos.get("dni", ""),
        "eap": datos.get("eap", ""),
        "asignatura": datos.get("asignatura", ""),
        "nrc": datos.get("nrc", ""),
        "docente": datos.get("docente", ""),
        "tipo": datos["tipo"],
        "detalle": datos["detalle"],
        "solicita": datos.get("solicita", ""),
        "evidencia_url": datos.get("evidencia_url", ""),
        "evidencia_nombre": datos.get("evidencia_nombre", ""),
        "fecha_hecho": datos["fecha_hecho"],
        "estado": datos.get("estado", "Pendiente"),
        "creado_en": creado_en,
    }
    res = sb.table("quejas").insert(fila).execute()
    queja_id = res.data[0]["id"]

    if horarios:
        filas_h = [
            {"queja_id": queja_id, "dia": h["dia"], "inicio": h["inicio"], "fin": h["fin"]}
            for h in horarios
        ]
        sb.table("horarios").insert(filas_h).execute()

    return folio


def _adjuntar_horarios(sb, quejas):
    if not quejas:
        return quejas
    ids = [q["id"] for q in quejas]
    rows = sb.table("horarios").select("*").in_("queja_id", ids).execute().data
    horarios_por_queja = {}
    for r in sorted(rows, key=lambda x: x["id"]):
        horarios_por_queja.setdefault(r["queja_id"], []).append(
            {"dia": r["dia"], "inicio": r["inicio"], "fin": r["fin"]}
        )
    for q in quejas:
        q["horarios"] = horarios_por_queja.get(q["id"], [])
    return quejas


def obtener_quejas():
    sb = get_client()
    rows = sb.table("quejas").select("*").order("id", desc=True).execute().data
    return _adjuntar_horarios(sb, rows)


def actualizar_estado(queja_id, estado):
    sb = get_client()
    sb.table("quejas").update({"estado": estado}).eq("id", queja_id).execute()


def eliminar_queja(queja_id):
    sb = get_client()
    sb.table("horarios").delete().eq("queja_id", queja_id).execute()
    sb.table("quejas").delete().eq("id", queja_id).execute()


def buscar_quejas(termino, tipo=None, estado=None):
    sb = get_client()
    query = sb.table("quejas").select("*").ilike("apellidos", f"%{termino}%").or_(
        f"nombres.ilike.%{termino}%,matricula.ilike.%{termino}%,folio.ilike.%{termino}%,"
        f"detalle.ilike.%{termino}%,dni.ilike.%{termino}%,asignatura.ilike.%{termino}%,"
        f"nrc.ilike.%{termino}%,docente.ilike.%{termino}%"
    )
    if tipo and tipo != "Todos":
        query = query.eq("tipo", tipo)
    if estado and estado != "Todos":
        query = query.eq("estado", estado)
    rows = query.order("id", desc=True).execute().data
    return _adjuntar_horarios(sb, rows)
