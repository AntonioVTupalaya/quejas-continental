import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "quejas.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quejas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT UNIQUE,
            fecha TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            nombres TEXT NOT NULL,
            matricula TEXT NOT NULL,
            celular TEXT,
            dni TEXT,
            eap TEXT,
            asignatura TEXT,
            nrc TEXT,
            docente TEXT,
            tipo TEXT NOT NULL,
            detalle TEXT NOT NULL,
            solicita TEXT,
            fecha_hecho TEXT,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            queja_id INTEGER NOT NULL,
            dia TEXT NOT NULL,
            inicio TEXT NOT NULL,
            fin TEXT NOT NULL,
            FOREIGN KEY (queja_id) REFERENCES quejas (id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    conn.close()


def generar_folio(conn):
    cursor = conn.execute("SELECT COUNT(*) AS total FROM quejas")
    total = cursor.fetchone()["total"]
    anio = datetime.now().strftime("%Y")
    return f"Q-{anio}-{total + 1:04d}"


def insertar_queja(datos, horarios=None):
    conn = get_connection()
    cursor = conn.cursor()
    folio = generar_folio(conn)
    creado_en = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO quejas (
            folio, fecha, apellidos, nombres, matricula, celular, dni, eap,
            asignatura, nrc, docente, tipo, detalle, solicita, fecha_hecho,
            estado, creado_en
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            folio,
            datos["fecha"],
            datos["apellidos"],
            datos["nombres"],
            datos["matricula"],
            datos["celular"],
            datos["dni"],
            datos["eap"],
            datos.get("asignatura", ""),
            datos.get("nrc", ""),
            datos.get("docente", ""),
            datos["tipo"],
            datos["detalle"],
            datos.get("solicita", ""),
            datos["fecha_hecho"],
            datos["estado"],
            creado_en,
        ),
    )
    queja_id = cursor.lastrowid

    if horarios:
        for h in horarios:
            cursor.execute(
                "INSERT INTO horarios (queja_id, dia, inicio, fin) VALUES (?, ?, ?, ?)",
                (queja_id, h["dia"], h["inicio"], h["fin"]),
            )

    conn.commit()
    conn.close()
    return folio


def _adjuntar_horarios(quejas):
    if not quejas:
        return quejas
    conn = get_connection()
    ids = [q["id"] for q in quejas]
    placeholders = ",".join(["?"] * len(ids))
    rows = conn.execute(
        f"SELECT * FROM horarios WHERE queja_id IN ({placeholders}) ORDER BY queja_id, id",
        ids,
    ).fetchall()
    conn.close()
    horarios_por_queja = {}
    for r in rows:
        horarios_por_queja.setdefault(r["queja_id"], []).append(
            {"dia": r["dia"], "inicio": r["inicio"], "fin": r["fin"]}
        )
    for q in quejas:
        q["horarios"] = horarios_por_queja.get(q["id"], [])
    return quejas


def obtener_quejas():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM quejas ORDER BY id DESC").fetchall()
    conn.close()
    return _adjuntar_horarios([dict(r) for r in rows])


def actualizar_estado(queja_id, estado):
    conn = get_connection()
    conn.execute("UPDATE quejas SET estado = ? WHERE id = ?", (estado, queja_id))
    conn.commit()
    conn.close()


def eliminar_queja(queja_id):
    conn = get_connection()
    conn.execute("DELETE FROM horarios WHERE queja_id = ?", (queja_id,))
    conn.execute("DELETE FROM quejas WHERE id = ?", (queja_id,))
    conn.commit()
    conn.close()


def buscar_quejas(termino, tipo=None, estado=None):
    conn = get_connection()
    query = (
        "SELECT * FROM quejas WHERE (apellidos LIKE ? OR nombres LIKE ? OR matricula LIKE ? "
        "OR folio LIKE ? OR detalle LIKE ? OR dni LIKE ? OR asignatura LIKE ? OR nrc LIKE ? OR docente LIKE ?)"
    )
    params = [f"%{termino}%"] * 9
    if tipo and tipo != "Todos":
        query += " AND tipo = ?"
        params.append(tipo)
    if estado and estado != "Todos":
        query += " AND estado = ?"
        params.append(estado)
    query += " ORDER BY id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return _adjuntar_horarios([dict(r) for r in rows])
