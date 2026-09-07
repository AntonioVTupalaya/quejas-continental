# Sistema de Quejas y Reclamos de Alumnos

Aplicación web construida con **Streamlit** y **Supabase (Postgres)** para capturar y gestionar quejas, reclamos, sugerencias y observaciones de alumnos de la Universidad Continental (Dirección de Asuntos Académicos – Ciencias).

## Requisitos

- Python 3.9+
- Cuenta en [Supabase](https://supabase.com) (proyecto creado)
- Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Credenciales de Supabase

La app lee las credenciales desde `st.secrets` (Cloud) o variables de entorno (local).

Localmente, crea el archivo `.streamlit/secrets.toml` (no se sube a GitHub):

```toml
[supabase]
url = "https://TU-PROYECTO.supabase.co"
key = "TU-ANON-PUBLIC-KEY"
```

Tablas requeridas (SQL Editor de Supabase):

```sql
CREATE TABLE IF NOT EXISTS public.quejas (
    id BIGSERIAL PRIMARY KEY,
    folio TEXT UNIQUE NOT NULL,
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
);

CREATE TABLE IF NOT EXISTS public.horarios (
    id BIGSERIAL PRIMARY KEY,
    queja_id BIGINT NOT NULL REFERENCES public.quejas(id) ON DELETE CASCADE,
    dia TEXT NOT NULL,
    inicio TEXT NOT NULL,
    fin TEXT NOT NULL
);
```

## Cómo ejecutar

```bash
streamlit run app.py
```

Se abrirá el navegador en `http://localhost:8501`.

## Funcionalidades

- **Registrar queja/reclamo**: formulario con datos del alumno, curso (EAP, NRC, asignatura, docente, horario) y descripción.
- **Folio automático**: cada registro recibe un folio único (Q-AÑO-####).
- **Base de datos Supabase (Postgres)**: los datos persisten en la nube.

## Estructura

```
app.py          # Aplicación principal (UI + CSS con paleta PRISM UC)
database.py     # Capa de acceso a datos (Supabase/Postgres)
carga_datos.py  # Carga de horarios/NRC/Docentes desde Excel
logo_uc.png     # Logo institucional
```